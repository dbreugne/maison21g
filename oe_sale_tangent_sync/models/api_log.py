# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json


class TangentApiLog(models.Model):
    _name = 'tangent.api.log'
    _description = 'Tangent API Log'
    _order = 'create_date desc'

    name = fields.Char('Name', compute='_compute_name', store=True)
    config_id = fields.Many2one('tangent.api.config', string='API Configuration', 
                              required=True, ondelete='cascade')
    endpoint_url = fields.Char('Endpoint URL', required=True)
    http_method = fields.Selection([
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
    ], string='HTTP Method', required=True, default='POST')
    request_headers = fields.Text('Request Headers')
    request_params = fields.Text('Request Parameters')
    request_body = fields.Text('Request Body')
    response_status = fields.Integer('Response Status Code')
    response_body = fields.Text('Response Body')
    is_success = fields.Boolean('Success', compute='_compute_is_success', store=True)
    error_message = fields.Text('Error Message')
    processing_time = fields.Char('Processing Time')
    company_id = fields.Many2one('res.company', string='Company', related='config_id.company_id', store=True)
    
    # Many2many relations to orders
    pos_order_ids = fields.Many2many('pos.order', 'tangent_api_log_pos_order_rel', 
                                   'log_id', 'pos_order_id', string='POS Orders',
                                   help="POS orders included in this API synchronization")
    sale_order_ids = fields.Many2many('sale.order', 'tangent_api_log_sale_order_rel',
                                    'log_id', 'sale_order_id', string='Sale Orders', 
                                    help="Sale orders included in this API synchronization")
    
    # Computed fields for order counts
    pos_order_count = fields.Integer('POS Orders Count', compute='_compute_order_counts', store=True)
    sale_order_count = fields.Integer('Sale Orders Count', compute='_compute_order_counts', store=True)
    total_order_count = fields.Integer('Total Orders Count', compute='_compute_order_counts', store=True)
    
    @api.depends('create_date', 'endpoint_url')
    def _compute_name(self):
        for log in self:
            if log.create_date:
                # Convert to user's timezone
                user_datetime = fields.Datetime.context_timestamp(log, log.create_date)
                date_str = user_datetime.strftime('%Y-%m-%d %H:%M:%S')
                endpoint = log.endpoint_url.split('/')[-1] if log.endpoint_url else 'unknown'
                log.name = f"{date_str} - {endpoint}"
            else:
                log.name = 'New API Log'
    
    @api.depends('response_status')
    def _compute_is_success(self):
        for log in self:
            log.is_success = log.response_status and 200 <= log.response_status < 300
    
    @api.depends('pos_order_ids', 'sale_order_ids')
    def _compute_order_counts(self):
        for log in self:
            log.pos_order_count = len(log.pos_order_ids)
            log.sale_order_count = len(log.sale_order_ids)
            log.total_order_count = log.pos_order_count + log.sale_order_count
    
    def format_json(self, text):
        """Format JSON text for better readability"""
        if not text:
            return ""
        try:
            parsed = json.loads(text)
            return json.dumps(parsed, indent=4, sort_keys=True)
        except Exception:
            return text
    
    def format_request_body(self):
        """Format request body as JSON if possible"""
        return self.format_json(self.request_body)
    
    def format_response_body(self):
        """Format response body as JSON if possible"""
        return self.format_json(self.response_body)
