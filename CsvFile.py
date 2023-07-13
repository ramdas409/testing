import base64

from odoo import models,fields,api,_
import pandas as pd
import os
import re
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class CsvFile(models.Model):
    _name="csv.file"

    def action_csv_upload(self):
        store_files = [i.name for i in self.env['store.files'].search([])]
        print(store_files)
        x = "/home/dasari/csv"
        list_files = os.listdir(x)
        list_files = [filename for filename in list_files if not filename.endswith('.csv#')]
        print(list_files)
        for file_name in list_files:
            if (file_name in store_files):
                raise ValidationError("file already stored")
            else:
                pattern = "\w+.csv"
                result = re.search(pattern, file_name)
                print(result)
                if (result):
                    file_path = x + "/" + file_name
                    print(file_path)
                    data = pd.read_csv(file_path)
                    print(data)

                    # with open(file_path, 'rb') as fd:
                    #     data = fd.read()
                    #     print(data)
                    #
                    #     enc_data = base64.b64encode(data)
                    #     print(enc_data, "ffff")


                    list_ref_no = [vals.ref_no for vals in self.env['temp.rec'].search([])]
                    print("list of orders in temp.rec", list_ref_no)
                    client_order_ref = data['ref_no'].to_list()
                    print("list  of client order refs", client_order_ref)
                    common_order = set(client_order_ref).intersection(set(list_ref_no))
                    print("list of common oreders", common_order)


                    client_prod_no = data['item_code'].to_list()
                    print("common ", client_prod_no)
                    list_prod_no = [prod.name for prod in self.env['product.template'].search([])]
                    print(list_prod_no)
                    # print(set(client_prod_no))
                    common_prod_ref = set(client_prod_no).difference(set(list_prod_no))

                    print("common oreder products", common_prod_ref)
                    if (common_order):
                        raise ValidationError("Order Number Already exist")
                    if (common_prod_ref):
                        raise ValidationError("Some Products(Client Reference) Doesn't exist in Product Master")
                    stored_file = self.env['store.files']
                    with open(file_path, 'rb') as fd:
                        data_val = fd.read()
                        print(data_val)
                    # print(data_val)
                    enc_data = base64.b64encode(data_val)
                    print(enc_data)
                    print(type(enc_data))
                    stored_file.create({
                        'data': data_val,
                        'name': file_name,
                        'upload_time': datetime.now()
                    })
                    temp_rec = self.env['temp.rec']
                    for index, columns in data.iterrows():
                        temp_rec.create({
                            'file_name': file_name,
                            'up_date': datetime.now(),
                            'ref_no':columns['ref_no'],
                            'name': columns['name'],
                            'add1': columns['add1'],
                            'add2': columns['add2'],
                            'add3': columns['add3'],
                            'city': columns['city'],
                            'zip_code': columns['zip_code'],
                            'ph_res': columns['ph_res'],
                            'ph_off': columns['ph_off'],
                            'mobile': columns['mobile'],
                            'email_id': columns['email_id'],
                            'item_code': columns['item_code'],
                            'item_desc': columns['item_desc'],
                            'qty': columns['qty']})
                else:
                    raise UserError(_("Invalid file! (Allowed format - .csv)"))


