import io

from odoo import api, fields, models
from datetime import datetime, timedelta, date
import csv
import os
import base64


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def get_sequence(self):
        start_date = date(2021, 5, 13)
        today = date.today()
        delta = today - start_date
        return "MBSSH{seq}".format(seq=delta.days)

    def get_csv_line_by_date_time(self, hour_date_time, tz, current_date_time):
        start_time = current_date_time.replace(minute=00, second=00)
        end_time = current_date_time.replace(minute=59, second=59)
        domain = [("create_date", ">=", fields.Datetime.to_string(start_time)),
                  ("create_date", "<=", fields.Datetime.to_string(end_time)),
                  ("config_id","in",[6])]
        sale_orders = self.with_context(tz=tz).search(domain)
        amount_tax = 0.0
        amount_total = 0.0
        for indx, item in enumerate(sale_orders, start=1):
            payment_methods = [k.payment_method_id.name.lower() for k in item.payment_ids]
            if "cash" or "credit card" in payment_methods:
                amount_tax += item.amount_tax
                amount_total += item.amount_total
        row = ["MBSSH10",
               hour_date_time.strftime("%Y-%m-%d"),
               hour_date_time.strftime("%H"),
               amount_total,
               amount_tax,
               len(sale_orders)
               ]
        return row
    def create_sale_order_csv(self, env=None):
        directory = self.env.company.csv_folder or "/tmp"
        try:
            if not os.path.isdir(directory):
                os.makedirs(directory)
        except:
            raise
        current_date_time = datetime.now() - timedelta(hours=1)
        tz = self.user_id.tz
        hour_date_time = fields.Datetime.context_timestamp(self.with_context(tz=tz), current_date_time)
        current_row = self.get_csv_line_by_date_time(hour_date_time, tz, current_date_time)
        attachment_name = "{date_time}.csv".format(
                date_time=hour_date_time.strftime("%Y%m%d"))
        attachment = self.env["ir.attachment"].sudo().search([('name', '=', attachment_name)],
                                                             limit=1)
        if attachment:
            content = base64.b64decode(attachment.datas.decode('utf-8')).decode()
            lines = content.splitlines()
            last_line = lines[-1]
            last_hour = int(last_line.split(",")[2]) if last_line and len(last_line)>3 else 0
            total_to_update = hour_date_time.hour - last_hour
            if total_to_update == 0 and lines:
                lines.pop(-1)
            elif total_to_update > 1:
                for hour in range(total_to_update, 0, -1):
                    hour_date_to_get = hour_date_time - timedelta(hours=hour)
                    if hour < last_hour:
                        missed_row = self.get_csv_line_by_date_time(hour_date_to_get, tz, current_date_time)
                        lines.append(",".join(str(x) for x in missed_row))
            lines.append(",".join(str(x) for x in current_row))
            joined_lines = "\n".join(lines) + "\n"
            attachment.write(
                {"datas": base64.b64encode(joined_lines.encode("utf-8")), "mimetype": attachment.mimetype}
            )
        else:
            lines = []
            for hour in range(hour_date_time.hour, 0, -1):
                domain_hour = current_date_time - timedelta(hours=hour)
                time_to_get = fields.Datetime.context_timestamp(self.with_context(tz=tz), domain_hour)
                if hour <= hour_date_time.hour:
                    missed_row = self.get_csv_line_by_date_time(time_to_get, tz, domain_hour)
                    lines.append(",".join(str(x) for x in missed_row))
            lines.append(",".join(str(x) for x in current_row))
            joined_lines = "\n".join(lines) + "\n"
            self.env['ir.attachment'].create({
                'datas': base64.b64encode(joined_lines.encode("utf-8")),
                'mimetype': "text/csv",
                'name': attachment_name,
                'type': 'binary',
                'public': False
            })
        """
        Remov all old files (on local server) in case this is configured..
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