from odoo import api, fields, models
from datetime import datetime, timedelta
import csv
import os

import base64


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def create_sale_order_csv(self, env=None):
        directory = self.env.company.csv_folder or "/tmp"
        # try:
        #     if not os.path.isdir(directory):
        #         os.makedirs(directory)
        # except:
        #     raise
        current_date_time = datetime.now()
        last_hour_date_time = current_date_time - timedelta(hours=1)
        tz = self.env.user.tz
        hour_date_time = fields.Datetime.context_timestamp(self.with_context(tz=tz), current_date_time - timedelta(minutes=25))
        domain = [("create_date", "<=", fields.Datetime.to_string(current_date_time)),
                  ("create_date", ">", fields.Datetime.to_string(last_hour_date_time))]
        sale_orders = self.search(domain)
        amount_tax = 0.0
        amount_total = 0.0
        for indx, item in enumerate(sale_orders, start=1):
            amount_tax += item.amount_tax
            amount_total += item.amount_total
        row = ["MBSSH{index}".format(index=hour_date_time.strftime("%H")),
               hour_date_time.strftime("%Y-%m-%d"),
               hour_date_time.strftime("%H"),
               amount_total,
               amount_tax,
               len(sale_orders)
               ]
        file_name = "{directory}/mbssh_{date_time}.csv".format(directory=directory,
                                                               date_time=fields.Date.to_string(current_date_time))
        attachment_name = "mbssh_{date_time}.csv".format(
                date_time=fields.Date.to_string(current_date_time))
        attachment = self.env["ir.attachment"].sudo().search([('name', '=', attachment_name)],
                                                             limit=1)
        if attachment:
            content = attachment.unlink()
            # writer = csv.writer(content, delimiter=',',
            #                     quotechar='|', quoting=csv.QUOTE_MINIMAL)
            # writer.writerow(row)
        # else:
        with open(file_name, 'a', newline='') as file:
            writer = csv.writer(file, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(row)
        self.env['ir.attachment'].create({
            'datas': base64.b64encode(open(file_name).read().encode("utf-8")),
            'name': attachment_name,
            'type': 'binary',
            'public': False
        })
        """
        Remove all old files (on local server) in case this is configured..
        """
        if self.env.company.csv_autoremove:
            delete_date = current_date_time - timedelta(days=self.env.company.csv_days_to_keep)
            self.env["ir.attachment"].sudo().search([('name', 'like', "mbssh_"),
                                                     ('create_date', '<=', delete_date)]).unlink()
            # Loop over all files in the directory.
            for f in os.listdir(directory):
                full_path = os.path.join(directory, f)
                if "mbssh" in full_path:
                    timestamp = os.stat(full_path).st_ctime
                    create_time = datetime.fromtimestamp(timestamp)
                    now = datetime.now()
                    delta = now - create_time
                    if delta.days >= self.env.company.csv_days_to_keep:
                        # Only delete files (which are .csv), no directories.
                        if os.path.isfile(full_path) and (".csv" in f or '.CSV' in f):
                            os.remove(full_path)


class ResCompany(models.Model):
    _inherit = 'res.company'

    csv_folder = fields.Char('CSV Backup Directory', help='Absolute path for storing the CSV', required='True',
                             default='/odoo/csv_backups')
    csv_autoremove = fields.Boolean('Auto. Remove Backups',
                                    help='If you check this option you can choose to automaticly remove the CSV '
                                         'after xx days')
    csv_days_to_keep = fields.Integer('Remove after x days',
                                      help="Choose after how many days the CSV should be deleted. For example:\n"
                                           "If you fill in 5 the CSV will be removed after 5 days.",
                                      required=True)