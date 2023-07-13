from odoo import models, _
from odoo.exceptions import UserError, ValidationError
import pandas as pd
import os
import re
import base64
from datetime import datetime


class Bingo(models.Model):
    _name = 'bingo.data'

    def data_check_submit(self):
        x = "/home/dasari/Desktop/orders"
        y = [i.file_name for i in self.env['stored.file'].search([])]
        list_files=os.listdir(x)
        ab = os.listdir(x)
        list_files = [filename for filename in ab if not filename.endswith('.xlsx#')]
        print(list_files,">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.")
        for file_name in list_files:
            print(file_name)
            if (file_name in y):
                print(file_name, " file is already stored")
            else:
                # y  = "/home/dasari/Desktop/orders/Fulla_File.xlsx"
                file_path=x+"/"+file_name
                print(y)
                pattern = "\w+.xlsx"
                result = re.search(pattern, file_path)
                print(result)

                if (result):

                    data = pd.read_excel(file_path, engine='openpyxl')
                    print('pattern matched')
                    print(data)
                    list_order_no = [vals.ref_no for vals in self.env['temp.rec'].search([])]
                    print("list of orders in temp.rec", list_order_no)
                    product_no = [prod.default_code for prod in self.env['product.template'].search([])]
                    print("list of products available", product_no)
                    client_order_ref = data['WS-REF-NBR              17'].to_list()
                    print("list  of client order refs", client_order_ref)
                    common_order = set(list_order_no).intersection(set(client_order_ref))
                    print("list of common oreders", common_order)

                    client_product_no = data['WS-OUT-ITEM-CODE         9'].to_list()
                    print("common ", client_product_no)
                    common_prod_ref = set(product_no).difference(set(client_product_no))
                    print("common oreder products", common_prod_ref)
                    if (common_order):
                        raise ValidationError("Order Number Already exist")
                    if (common_prod_ref):
                        raise ValidationError("Some Products(Client Reference) Doesn't exist in Product Master")

                    stored_file = self.env['stored.file']
                    with open(file_path, 'rb') as fd:
                        data_val = fd.read()
                    # print(data_val)
                    enc_data = base64.b64encode(data_val)
                    # print(enc_data)
                    stored_file.create({
                        'data': enc_data,
                        'file_name': file_name,
                        'stored_date': datetime.now()
                    })
                    temp_rec = self.env['temp.rec']
                    for index, columns in data.iterrows():
                        temp_rec.create({
                            'file_name': file_name,
                            'up_date': datetime.now(),
                            'add1': columns['WS-OUT-997-ADDR1        40'],
                            'add2': columns['WS-OUT-997-ADDR2        40'],
                            'city': columns['WS-OUT-997-CITY         30'],
                            'zip_code': columns['WS-OUT-997-POSTAL-CODE  10'],
                            'ph_res': columns['WS-OUT-997-HOME-PHONE   20'],
                            'ph_off': columns['WS-OUT-997-EMP-PHONE    20'],
                            'mobile': columns['WS-OUT-997-MOBILE-NO    20'],
                            'email_id': columns['WS-997-EMAIL-ID         60'],
                            'item_code': columns['WS-OUT-ITEM-CODE         9'],
                            'item_desc': columns['WS-OUT-ITEM-DESC        30'],
                            'qty': columns['WS-OUT-QTY               9']})

                else:
                    raise UserError(_("Invalid file! (Allowed format - .xlsx)"))

