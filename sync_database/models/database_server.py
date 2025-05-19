
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import xmlrpc.client as xc
import ssl
import requests
import json, ast
import logging
from datetime import timedelta 
import datetime
import ast


class DatabaseConnection(models.Model):
    _name ='database.sync'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Sync Order Data Hourly" 
 
 
    name = fields.Char('Name', required=True, default="Marina Bay")
    url_token = fields.Char('Token URL', required=True,)
    url_order = fields.Char('Order URL', required=True,)
    username = fields.Char('User Name',  required=True )
    password = fields.Char('Password',  required=True )
    machine_id = fields.Char('Machine ID:',)  
    batchid = fields.Char('Batch ID:', default='1')  
    token = fields.Text('Token',)  
    state =  fields.Selection([('draft','Draft'),('active','Active')], default='draft')

    def set_to_draft(self):    
        self.state = 'draft'

    def get_token(self):  
        url = self.url_token
        payload =  "grant_type=password&"+"username="+self.username + "&password=" + self.password 
        headers = { 
                  'Content-Type': 'text/plain'
                  }
        logging.info("URL=============================>%s",str(url))  
        r = requests.request("GET", url, headers=headers, data=payload) 
        json_data = json.loads(r.text)
        logging.info("r=============================>%s",str(r.text))
        if "access_token" not in json_data:
            message = 'Connection Error: Token cannot be Generated Invalid Credentials!!' 
            temp_id = self.env['wizard.message'].create({'text':message}) 
            return {
                    'name':_("Token Result"),
                    'view_mode': 'form',
                    'view_id': False,
                    'view_type': 'form',
                    'res_model': 'wizard.message',
                    'res_id': temp_id.id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    'domain': '[]',
                   }
        else:
            self.token = "Bearer "+ json_data["access_token"]
            self.state = "active"
            message = 'Token Generated Successfully!!' 
            temp_id = self.env['wizard.message'].create({'text':message}) 
            return {
                    'name':_("Test Result"),
                    'view_mode': 'form',
                    'view_id': False,
                    'view_type': 'form',
                    'res_model': 'wizard.message',
                    'res_id': temp_id.id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    'domain': '[]',
                   }
         
        
    def sync_draft_order(self):    
        record_ids = self.env["order.data.hourly"].search([('state','=','draft')])
        if not record_ids:            
            message = "No Order Data to Sync"
            temp_id = self.env['wizard.message'].create({'text':message}) 
            return {
                    'name':_("Token Result"),
                    'view_mode': 'form',
                    'view_id': False,
                    'view_type': 'form',
                    'res_model': 'wizard.message',
                    'res_id': temp_id.id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    'domain': '[]',
                   }
        self.sync_order_data(record_ids)
       
    def sync_failed_order(self):    
        record_ids = self.env["order.data.hourly"].search([('state','=','failed')])
        if not record_ids:           
            message = "No Order Data to Re-Sync"
            temp_id = self.env['wizard.message'].create({'text':message}) 
            return {
                    'name':_("Token Result"),
                    'view_mode': 'form',
                    'view_id': False,
                    'view_type': 'form',
                    'res_model': 'wizard.message',
                    'res_id': temp_id.id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    'domain': '[]',
                   }
        self.sync_order_data(record_ids)
        
    def sync_order_data(self, record_ids):  
        url = self.url_order
        order_list = []
        for rec in record_ids:
            rec_data = { "sale": {
              "machineid": str(rec.machineid),
              "date": str(rec.date),
              "hour": str(rec.hour),
              "receiptcount": str(rec.receiptcount),
              "gto": str("{:.2f}".format(rec.gto)),
              "gst": str("{:.2f}".format(rec.gst)),
              "discount": str("{:.2f}".format(rec.discount)),
              "gstregistered": "N",
              "batchid": str(rec.batchid),
              "servicecharge": str("{:.2f}".format(rec.servicecharge)),
              "noofpax": str(rec.noofpax),
              "cash": str("{:.2f}".format(rec.cash)),
              "nets": str("{:.2f}".format(rec.nets)),
              "visa": str("{:.2f}".format(rec.visa)),
              "mastercard": str("{:.2f}".format(rec.mastercard)),
              "amex": str("{:.2f}".format(rec.amex)),
              "voucher": str("{:.2f}".format(rec.voucher)),
              "othersamount": str("{:.2f}".format(rec.othersamount)),
                   } }
            order_list.append(rec_data)
        to_post = {"sales":order_list}
        logging.info("json_data=============================>%s",str(to_post))   
        payload = json.dumps(to_post) 
        headers = { 
               'Content-Type': 'application/json',
               'Authorization': self.token,
                  }
        r = requests.request("POST", url, headers=headers, data=payload)
        json_data = json.loads(r.text) 
        logging.info("json_data=============================>%s",str(json_data))
        if json_data['status'] == 'success':
            record_ids.write({'state':'synced'})
            html = json_data['message']
            self.message_post(body=html)            
            message = json_data['message'] 
            temp_id = self.env['wizard.message'].create({'text':message}) 
            return {
                    'name':_("Token Result"),
                    'view_mode': 'form',
                    'view_id': False,
                    'view_type': 'form',
                    'res_model': 'wizard.message',
                    'res_id': temp_id.id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    'domain': '[]',
                   }
        else:
            record_ids.write({'state':'failed'})
            html = json_data['message']
            self.message_post(body=html)            
            message = json_data['message'] 
            temp_id = self.env['wizard.message'].create({'text':message}) 
            return {
                    'name':_("Token Result"),
                    'view_mode': 'form',
                    'view_id': False,
                    'view_type': 'form',
                    'res_model': 'wizard.message',
                    'res_id': temp_id.id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    'domain': '[]',
                   }
            
                  
                
                
                
                
           

