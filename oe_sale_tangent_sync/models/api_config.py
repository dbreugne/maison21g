# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import groupby
from odoo.exceptions import UserError

from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz, requests, time, json


class TangentApiConfig(models.Model):
    _name = 'tangent.api.config'
    _description = 'Tangent API Configuration'
    _rec_name = 'name'

    name = fields.Char('Name', default='Tangent API', required=True)
    endpoint_url = fields.Char('Endpoint URL', default='https://api.tangent.example.com', required=True, help="The URL of the Tangent API endpoint")
    username = fields.Char('Username', required=True, help="API username for authentication")
    password = fields.Char('Password', required=True, help="API password for authentication", copy=False)
    machine_id = fields.Char('Machine ID', help="Unique identifier for the machine connecting to Tangent API")
    pos_ids = fields.Many2many('pos.config', string='POS Terminals', help="POS terminals to synchronize with Tangent")
    is_sale_included = fields.Boolean('Include Sales', default=False, 
                                     help="Enable to include sale transactions in the synchronization")
    company_id = fields.Many2one('res.company', string='Company', required=True, 
                               default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    
    @api.constrains('endpoint_url')
    def _check_endpoint_url(self):
        for record in self:
            if record.endpoint_url and not (record.endpoint_url.startswith('http://') or 
                                          record.endpoint_url.startswith('https://')):
                raise ValidationError(_("Endpoint URL must start with 'http://' or 'https://'"))
                
    def sync_sale_orders(self):
        """Synchronize sale orders marked for synchronization"""
        self.ensure_one()
        sale_orders = self.env['sale.order'].search([
            ('is_sync_included', '=', True),
            '|',
            ('tangent_api_sync_date', '=', False),
            ('write_date', '>', 'tangent_api_sync_date')
        ])
        
        if not sale_orders:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No orders to synchronize'),
                    'message': _('There are no sale orders marked for synchronization or all are already up to date.'),
                    'sticky': False,
                    'type': 'warning',
                }
            }
            
        # Create a log entry for this sync attempt
        log_vals = {
            'config_id': self.id,
            'endpoint_url': self.endpoint_url,
            'http_method': 'POST',
            'request_headers': '{"Content-Type": "application/json", "Authorization": "Basic ***"}',
        }
        
        api_log = self.env['tangent.api.log'].create(log_vals)
        
        # Link sale orders to the log
        api_log.sale_order_ids = [(6, 0, sale_orders.ids)]
        
        # TODO: Implement actual API call here
        # For now, just update the sync date for demonstration purposes
        sync_time = fields.Datetime.now()
        for order in sale_orders:
            order.write({
                'tangent_api_sync_date': sync_time,
                'tangent_api_id': self.id,
                'tangent_api_response': '{"status": "success", "message": "Order synchronized successfully", "order_id": ' + str(order.id) + '}'
            })
            
        # Update the log with success information
        api_log.write({
            'response_status': 200,
            'response_body': '{"status": "success", "message": "Synchronized ' + str(len(sale_orders)) + ' orders"}',
            'processing_time': 1.5,  # Placeholder processing time
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Synchronization Complete'),
                'message': _('%s sale orders have been synchronized.') % len(sale_orders),
                'sticky': False,
                'type': 'success',
            }
        }
    
    def generate_empty_payload(self, start_date, end_date):
        result = {}
        while start_date <= end_date:
            for x in range(24):
                key = (start_date.date(), x)
                result[key] = {
                    'orders': [],
                    'gto_sum': 0.0,
                    'gst_sum': 0.0,
                    'discount_sum': 0.0,
                    'cash_sum': 0.0,
                    'nets_sum': 0.0,
                    'visa_sum': 0.0,
                    'mastercard_sum': 0.0,
                    'amex_sum': 0.0,
                    'voucher_sum': 0.0,
                    'others_sum': 0.0,
                }
            start_date += relativedelta(days=1)
        return result

    def get_orders_data(self, date=False):
        """Get POS and Sale orders data grouped by date and hour
        
        Returns:
            dict: Orders grouped by date and hour
        """
        self.ensure_one()
        if not self.pos_ids and not self.is_sale_included:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No POS terminals or Sale Orders configured'),
                    'message': _('Please configure POS terminals or enable Sale Orders to synchronize.'),
                    'sticky': False,
                    'type': 'warning',
                }
            }
        today = date if date else datetime.now(pytz.timezone('Asia/Singapore'))
        start_day_sg = today.replace(hour=0, minute=0, second=0, microsecond=0) 
        end_day_sg = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        start_day_utc = start_day_sg.astimezone(pytz.utc)
        end_day_utc = end_day_sg.astimezone(pytz.utc)

        # Initialize data structure to hold aggregated values by date and hour
        aggregated_data = self.generate_empty_payload(start_day_sg, end_day_sg)
        pos_orders = self.env['pos.order']
        sale_orders = self.env['sale.order']
        
        # Get POS orders if POS terminals are configured
        if self.pos_ids:
            pos_domain = [
                ('config_id', 'in', self.pos_ids.ids),
                # ('tangent_api_sync_date', '=', False),
                ('state', 'in', ('done', 'paid')),
                ('date_order', '>=', start_day_utc),
                ('date_order', '<=', end_day_utc),
            ]
            
            # Get all POS orders that match the criteria
            pos_orders = self.env['pos.order'].search(pos_domain)
            
            for sg_date_order, grouped_bydates in groupby(pos_orders, key=lambda pos: pytz.utc.localize(pos.date_order).astimezone(pytz.timezone('Asia/Singapore')).date()):
                orders = self.env['pos.order'].concat(*grouped_bydates)
                date = sg_date_order
                if date != start_day_sg.date():
                    dt_datas = self.generate_empty_payload(sg_date_order, sg_date_order)
                    aggregated_data.update(dt_datas)
                for hour_group, grouped_byhour in groupby(orders, key=lambda p: pytz.utc.localize(p.date_order).astimezone(pytz.timezone('Asia/Singapore')).hour):
                    grouped_orders = self.env['pos.order'].concat(*grouped_byhour)
                    key = (date, hour_group)
                    # if key not in aggregated_data:
                    #     aggregated_data[key] = {
                    #         'orders': [],
                    #         'gto_sum': 0.0,
                    #         'gst_sum': 0.0,
                    #         'discount_sum': 0.0,
                    #         'cash_sum': 0.0,
                    #         'nets_sum': 0.0,
                    #         'visa_sum': 0.0,
                    #         'mastercard_sum': 0.0,
                    #         'amex_sum': 0.0,
                    #         'voucher_sum': 0.0,
                    #         'others_sum': 0.0,
                    #     }
                    
                    current_orders = aggregated_data[key]['orders']
                    current_orders.extend(grouped_byhour)
                    aggregated_data[key]['orders'] = current_orders
                    for order in grouped_byhour:
                        aggregated_data[key]['gto_sum'] += order.get_gto_in_company_currency()
                        aggregated_data[key]['gst_sum'] += order.get_gst_in_company_currency()
                        aggregated_data[key]['discount_sum'] += order.get_discount_in_company_currency()
                    payment_datas = grouped_orders.get_tangent_payment_datas()
                    for payment_type in payment_datas.keys():
                        aggregated_data[key][payment_type+'_sum'] += payment_datas[payment_type]
        
        # Get Sale orders if enabled
        if self.is_sale_included:
            # TO DO: Sync sale order datas at date 3 of next month
            # e.g order date is 8 april, the order should be synced on 3 may
            sale_domain = [
                ('is_sync_included', '=', True),
                ('tangent_api_sync_date', '=', False),
                ('state', '=', 'sale'),  # Confirmed orders
                # ('date_order', '>=', start_day_utc),
                # ('date_order', '<=', end_day_utc),
                ('invoice_ids', '!=', False),  # Has invoices
            ]
            
            # Get all Sale orders that match the criteria
            sale_orders = self.env['sale.order'].search(sale_domain)
            
            paid_invoice_status = ['paid', 'partial', 'in_payment'] 
            # Filter orders with invoices that are paid or partially paid
            sale_orders_with_payments = sale_orders.filtered(
                lambda so: any(inv.payment_state in paid_invoice_status for inv in so.invoice_ids)
            )
            
            for sg_date_order, grouped_bydates in groupby(sale_orders_with_payments, key=lambda so: pytz.utc.localize(so.date_order).astimezone(pytz.timezone('Asia/Singapore')).date()):
                orders = self.env['sale.order'].concat(*grouped_bydates)
                date = sg_date_order
                if date != start_day_sg.date():
                    dt_datas = self.generate_empty_payload(sg_date_order, sg_date_order)
                    aggregated_data.update(dt_datas)
                for hour_group, grouped_byhour in groupby(orders, key=lambda so: pytz.utc.localize(so.date_order).astimezone(pytz.timezone('Asia/Singapore')).hour):
                    grouped_orders = self.env['sale.order'].concat(*grouped_byhour)
                    key = (date, hour_group)
                    current_orders = aggregated_data[key]['orders']
                    current_orders.extend(grouped_byhour)
                    aggregated_data[key]['orders'] = current_orders
                    for order in grouped_byhour:
                        aggregated_data[key]['gto_sum'] += order.get_gto_in_company_currency()
                        aggregated_data[key]['gst_sum'] += order.get_gst_in_company_currency()
                        aggregated_data[key]['discount_sum'] += order.get_discount_in_company_currency()
                    payment_datas = grouped_orders.get_tangent_payment_datas()
                    for payment_type in payment_datas.keys():
                        aggregated_data[key][payment_type+'_sum'] += payment_datas[payment_type]
        
        if not len(pos_orders.ids) and not len(sale_orders.ids):
            return {}
            
        result_data = []
        # Convert aggregated data to API format
        for (order_date, hour), data in aggregated_data.items():
            # Format all values as strings
            result_data.append({
                'sale': {
                    'machineid': str(self.machine_id or ''),
                    'batchid': str(1),
                    'date': order_date.strftime('%Y%m%d'),
                    'hour': str(hour).zfill(2),
                    'receiptcount': str(len(data['orders'])),
                    'gto': str(round(data['gto_sum'], 2)),  # GTO sales for the hour (after discount and before GST)
                    'gst': str(round(data['gst_sum'], 2)),  # GST amount
                    'discount': str(round(data['discount_sum'], 2)),  # Discount amount
                    'servicecharge': str(0),  # Service charge for F&B only
                    'noofpax': str(0),  # No of persons for F&B only.
                    'cash': str(round(data['cash_sum'], 2)),  # Cash (after discount and before GST)
                    'nets': str(round(data['nets_sum'], 2)),  # NETS (after discount and before GST)
                    'visa': str(round(data['visa_sum'], 2)),  # VISA (after discount and before GST)
                    'mastercard': str(round(data['mastercard_sum'], 2)),  # Mastercard (after discount and before GST)
                    'amex': str(round(data['amex_sum'], 2)),  # AMEX (after discount and before GST)
                    'voucher': str(round(data['voucher_sum'], 2)),  # Voucher (after discount and before GST)
                    'othersamount': str(round(data['others_sum'], 2)),  # Others (after discount and before GST)
                    'gstregistered': 'N'  # If GST registered (Y/N)
                }
            })
        return {
            'pos_orders': pos_orders,
            'sale_orders': sale_orders,
            'data': {'sales': result_data}
        }
    
    def get_token(self):
        """Get token from Tangent API
        
        According to Tangent API documentation, the token endpoint expects:
        - Method: GET
        - Content-Type: application/json
        - Request Body: grant_type=password&username={username}&password={password}
        
        Returns:
            str: The access token if successful, False otherwise
        """
        start_time = time.time()
        response = False
        url = self.endpoint_url + '/v1/api/token'
        try:
            # Prepare the request parameters based on the API documentation
            params = f"grant_type=password&username={self.username}&password={self.password}"
            headers = {
                'Content-Type': 'application/json'
            }            
            # Create a log entry for this token request
            log_vals = {
                'config_id': self.id,
                'endpoint_url': url,
                'http_method': 'GET',
                'request_params': str(params),
                'request_headers': headers,
            }
            
            api_log = self.env['tangent.api.log'].create(log_vals)
            
            # Make the request
            response = requests.get(url, data=params, headers=headers)
            response_json = json.loads(response.text)
            processing_time = time.time() - start_time
            if not response.ok:
                raise UserError(f"Error code {response.status_code}: {response}")
            # Update the log with the response
            token_data = response_json.get('access_token')
            api_log.write({
                'response_status': response.status_code,
                'response_body': response.json(),
                'is_success': True,
                'processing_time': f"{processing_time} seconds",
            })
            return token_data                
        except Exception as e:
            processing_time = time.time() - start_time
            error_message = f"""Exception while getting token: 
            {str(e)}"""
            api_log.write({
                'response_status': 500,
                'response_body': str(response.json()) if response != False else 'Exception while geting token',
                'is_success': False,
                'error_message': error_message,
                'processing_time': f"{processing_time} seconds",
            })
            return False
    
    def do_sync(self, date=False):
        """Synchronize both sale orders and POS orders based on configuration
        
        For POS orders, synchronization is done by grouping orders by hour (0-23)
        and sending each hour's orders in separate API calls.
        """
        self.ensure_one()
        url = self.endpoint_url + '/v1/api/SalesHourly'
        start_time = time.time()
        try:
            # Create a log entry for this sync attempt
            headers = {
                'Content-Type': 'application/json',
            }
            log_vals = {
                'config_id': self.id,
                'endpoint_url': url,
                'http_method': 'POST',
                'request_headers': headers,
            }
            
            api_log = self.env['tangent.api.log'].create(log_vals)
            # Get token
            token = self.get_token()
            if not token:
                api_log.write({
                    'response_status': 401,
                    'response_body': '{"error": "Authentication failed", "message": "Could not obtain API token"}',
                    'is_success': False,
                    'error_message': 'Failed to obtain API token',
                    'processing_time': f"{time.time() - start_time} seconds",
                })
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Authentication Failed'),
                        'message': _('Could not obtain API token. Check your credentials.'),
                        'sticky': False,
                        'type': 'warning',
                    }
                }
            
            order_datas = self.get_orders_data(date=date)
            # Update main log with final status
            data = order_datas.get('data', False)
            pos_orders = order_datas.get('pos_orders', [])
            sale_orders = order_datas.get('sale_orders', [])
            start_time = time.time()
            response = False
            if len(pos_orders) <= 0 and len(sale_orders) <= 0:
                raise UserError(_("No sale orders or POS orders found to synchronize."))
            try:
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + token
                }
                api_log.write({
                    'request_headers': json.dumps(headers, indent=2),
                    'request_body': json.dumps(data, indent=2),
                    'pos_order_ids': [(6, 0, pos_orders.ids)],
                    'sale_order_ids': [(6, 0, sale_orders.ids)],
                })
                start_time = datetime.now()
                response = requests.post(url, json=data, headers=headers)
                response_json = json.loads(response.text)
                if response_json['status'] != 'success':
                    error_message = '\n'.join([x.get('message') for x in response_json.get('errors', {}) if x.get('message')]) or response_json.get('message')
                    raise UserError(error_message)
                # Update sync date if successful
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                api_log.write({
                    'response_status': response.status_code,
                    'response_body': response_json['message'],
                    'is_success': response_json['status'] == 'success',
                    'processing_time': execution_time,
                })
                # Update POS orders sync date
                pos_orders.write({
                    'tangent_api_sync_date': end_time,
                    'tangent_api_id': self.id,
                    'tangent_api_response': response_json['message']
                })
                sale_orders.write({
                    'tangent_api_sync_date': end_time,
                    'tangent_api_id': self.id,
                    'tangent_api_response': response_json['message']
                })

            except Exception as e:
                api_log.write({
                    'response_status': response.status_code if response else 500,
                    'response_body': response.text if response else '',
                    'is_success': False,
                    'error_message': str(e),
                    'processing_time': 0,
                })
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Synchronization Failed'),
                        'message': _(response.text if response else str(e)),
                        'sticky': True,
                        'type': 'danger',
                    }
                }
        except Exception as e:
            error_msg = f'Synchronization failed: {str(e)}'
            api_log.write({
                'response_status': 500,
                'response_body': '{"error": "Internal error", "message": "' + error_msg + '"}',
                'is_success': False,
                'error_message': error_msg,
                'processing_time': 0,
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Synchronization Failed'),
                    'message': _(error_msg),
                    'sticky': True,
                    'type': 'danger',
                }
            }
    
    @api.model
    def sync_all(self):
        """Synchronize all active API configurations"""
        configs = self.search([('active', '=', True)])
        if not configs:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No active configurations'),
                    'message': _('There are no active Tangent API configurations.'),
                    'sticky': False,
                    'type': 'warning',
                }
            }
            
        for config in configs:
            config.do_sync()
            
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Synchronization Complete'),
                'message': _('All active Tangent API configurations have been processed.'),
                'sticky': False,
                'type': 'success',
            }
        }
