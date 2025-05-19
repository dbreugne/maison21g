
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import xmlrpc.client as xc
import ssl
import requests
import json, ast
import logging 
from datetime import timedelta 
import datetime


class StockWarehouse(models.Model):
    _inherit ='stock.warehouse'

    is_mbs=fields.Boolean('Is MBS?') 
 
class OrderDataHourly(models.Model):
    _name ='order.data.hourly' 
    _description = "Order Data Hourly yo sync" 
 
    name = fields.Char('Name', required=True,)
    machineid = fields.Char('Machine ID')
    date = fields.Char('Date')
    hour = fields.Char('Hours' )
    receiptcount = fields.Integer('Receipt Count')  
    gto = fields.Float('GTO')  
    gst = fields.Float('GST')  
    discount = fields.Float('Discount')  
    gstregistered = fields.Boolean('GST Registered?')  
    batchid = fields.Integer('Batch ID')  
    servicecharge = fields.Float('Service Charge')  
    noofpax = fields.Integer('Noofpax')  
    cash = fields.Float('Cash')  
    nets = fields.Float('Nets')  
    visa = fields.Float('Visa')  
    mastercard = fields.Float('Master Card')  
    amex = fields.Float('Amex Card')
    voucher = fields.Float('Voucher')
    othersamount = fields.Float('Others Amount')
    state =  fields.Selection([('draft','Draft'),('synced','Synced'),('failed','Failed')], default='draft')
    partner_ids = fields.Many2many("res.partner", 'partner_hourly_sale_ref', 'data_id', 'partner_id', string="Customers") 
    order_ids = fields.Many2many("sale.order", 'hourly_sale_ref', 'data_id', 'order_id', string="Orders") 


    @api.model_create_multi
    def create(self, vals_list): 
        for vals in vals_list: 
            vals['name'] = self.env['ir.sequence'].next_by_code('order.data.hourly', sequence_date=None) or _("New")
        res = super(OrderDataHourly, self).create(vals)
        return res

                
 
class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_mbs = fields.Boolean('Is MBS Customer?')
    data_ids = fields.Many2many("order.data.hourly", 'partner_hourly_sale_ref', 'partner_id', 'data_id', string="Records")
 
class SaleOrder(models.Model):
    _inherit = 'sale.order'
                
    is_b2b = fields.Boolean('B2B?', compute="check_b2b_order", store=True)
    data_ids = fields.Many2many("order.data.hourly", 'hourly_sale_ref', 'order_id', 'data_id', string="Records")
                
    @api.depends("partner_invoice_id")
    def check_b2b_order(self):
        for rec in self:
            if rec.partner_invoice_id.is_mbs:
                rec.is_b2b = True
            else:
                rec.is_b2b = False
            

