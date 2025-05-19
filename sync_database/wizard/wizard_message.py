
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, models, tools, registry 
from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime, timedelta
from odoo.exceptions import AccessError, UserError, ValidationError
import pytz

class wizard_message(models.TransientModel):
    _name = "wizard.message"
    
    text= fields.Text('Message')
            

class GenerateRecord(models.TransientModel):
    _name = "generate.record"
    
    model = fields.Selection([('sale.order',"Sale Order"),('pos.order','POS Order')], default="sale.order", readonly=True)
    order_ids = fields.Many2many("sale.order", string="Sale Orders")
    datetime =  fields.Datetime(string='Datetime', default=fields.Datetime.now())
    date =  fields.Date(string='Date', default=fields.Date.today())
    hours =  fields.Integer(string='Hours', default=1, readonly=True)
    
        
 
    def create_order_record(self):
        """ Get total sale amount and tax grouped by hour for today. """
        record_obj = self.env["order.data.hourly"]
        sync_id = self.env["database.sync"].search([('state','=','active')],limit=1)
        if not sync_id:
            raise UserError(_("Marina Bay Server Connection is Missing or not Active to Sync Order Data!!"))
        elif not sync_id.machine_id:
            raise UserError(_("Machine Id is Missing to Syncing Orders In Order Data Sync !!"))
        elif not sync_id.batchid:
            raise UserError(_("batchid Id is Missing to Syncing Orders In Order Data Sync !!"))
        #print("generate record of ============>>>>",self.date, self.date.year, self.date.month, self.date.day) 
        today = self.date
        # Get UTC timezone
        utc = pytz.UTC 
        # Start and end of today
        user_start = datetime.combine(today, datetime.min.time())
        user_end = datetime.combine(today, datetime.max.time())
        #print("Date Selected============>>>>",today, fields.Date.context_today(self)) 
        if today > fields.Date.context_today(self):
            raise UserError(_("Selected Datetime Should be before Tomorrow !!"))
        result = []
        sale_obj = self.env[self.model]
        date_str = str(self.date.year)
        if self.date.month <= 9:
           date_str += "0"+ str(self.date.month)
        else:
           date_str += str(self.date.month)
        if self.date.day <= 9:
           date_str += "0"+ str(self.date.day)
        else:
           date_str += str(self.date.day) 
        for hour in range(24):
            user_start_hour = user_start + timedelta(hours=hour)
            user_end_hour = user_start_hour + timedelta(hours=1)

            # Convert user's hour into UTC
            user_tz = self.env.user.tz or 'UTC'
            user_tz_obj = pytz.timezone(user_tz)
            
            localized_start = user_tz_obj.localize(user_start_hour)
            localized_end = user_tz_obj.localize(user_end_hour)
            
            utc_start_hour = localized_start.astimezone(utc)
            utc_end_hour = localized_end.astimezone(utc) 
            
            recod_ids = sale_obj.search([('is_b2b','=',True),('date_order','>=',utc_start_hour),('date_order','<=',utc_end_hour),('invoice_status','in',['upselling','invoiced'])])  
            #print("recod_ids record of ============>>>>",date_str,hour,len(recod_ids), utc_start_hour, utc_end_hour)
            # Search orders created in that hour
            total_amount = sum(recod_ids.mapped('amount_total'))
            total_tax = sum(recod_ids.mapped('amount_tax'))
            discount_amount = 0.0
            total_cash = 0.0
            partner_ids = []
            order_ids = []
            for order in recod_ids: 
                if order.warehouse_id.is_mb:
                    partner_ids.append(order.partner_id.id)
                    order_ids.append(order.id)
                    for line in order.order_line:
                        if line.discount and line.price_unit and  line.product_uom_qty:
                            total_unit_price = line.price_unit * line.product_uom_qty
                            if total_unit_price:
                                disc_amount = total_unit_price * line.discount / 100
                                discount_amount += disc_amount 
                            
            total_orders = len(recod_ids)
            gto = total_amount - total_tax  ## GTO sales for the hour (after discount and before GST)
            gst = total_tax  ## GST amount
            discount = discount_amount  ## Discount amount
            servicecharge = 0.0  ## Service charge for F&B only
            noofpax = 0  ## No of persons for F&B only.
            cash = total_cash  ## Cash (after discount and before GST)
            nets = total_amount - total_tax   ## NETS (after discount and before GST)
            visa = 0.0  ## VISA (after discount and before GST)
            mastercard = 0.0  ## Mastercard (after discount and before GST)
            amex = 0.0  ## AMEX (after discount and before GST)
            voucher = 0.0  ## Voucher (after discount and before GST)
            othersamount = 0.0  ## Others (after discount and before GST)
            gstregistered = "Y"
            record_value = {
                    "machineid":sync_id.machine_id,
                    "batchid":sync_id.batchid,
                    "date": date_str,
                    "hour": f"{hour:02d}:00",
                    "receiptcount":total_orders,
                    "gto": gto,
                    "gst": gst,
                    "discount":discount,
                    "cash":cash,
                    "nets":nets,
                    "gstregistered":True,
                    'partner_ids':[(6,0,partner_ids)],
                    'order_ids':[(6,0,order_ids)],
                }
            domain = [
                 ('date','=',record_value['date']),
                 ('hour','=',record_value['hour']),
                 ('machineid','=',record_value['machineid'])
                     ]
            #print("Vals to create record===============>>",record_value)  
            rec_exists = record_obj.search(domain) 
            if rec_exists:
                if rec_exists.state == 'synced':
                    raise UserError(_("Record Already Synced to Marina Bay Server !!"))
                else:
                    rec_exists.unlink()
            record_id = record_obj.create(record_value) 
            result.append(record_value) 
        #print("Vals to create record===============>>",result)   
        return True
 
