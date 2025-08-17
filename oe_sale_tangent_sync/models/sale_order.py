# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    tangent_api_sync_date = fields.Datetime('Tangent API Sync Date', 
                                          help="Date and time when this order was last synchronized with Tangent API")
    tangent_api_id = fields.Many2one('tangent.api.config', string='Tangent API Config',
                                   help="The Tangent API configuration used for synchronizing this order")
    tangent_api_response = fields.Text('API Response', help="Last response received from Tangent API for this order")

    is_sync_included = fields.Boolean('Sync Included', default=False, 
                                     help="Enable to include this order in the Tangent API synchronization")
    
    # Many2many relation to API logs
    tangent_api_log_ids = fields.Many2many('tangent.api.log', 'tangent_api_log_sale_order_rel',
                                         'sale_order_id', 'log_id', string='API Logs',
                                         help="API synchronization logs for this order")
    
    def get_amount_in_company_currency(self, amount):
        """Convert amount to company currency
        
        Args:
            amount (float): Amount in order currency
            
        Returns:
            float: Amount in company currency
        """
        if self.currency_id == self.company_id.currency_id:
            return amount
        currency_rate = self.currency_rate or 1.0
        return amount / currency_rate
    

    def get_gto_in_company_currency(self):
        """Get GTO (Gross Total Order) in company currency
        
        Returns:
            float: GTO in company currency
        """
        return self.get_amount_in_company_currency(self.amount_untaxed)
    
    def get_gst_in_company_currency(self):
        """Get GST (tax) in company currency
        
        Returns:
            float: GST in company currency
        """
        return self.get_amount_in_company_currency(self.amount_tax)
    
    def get_payment_amount_by_method_in_company_currency(self, payment_method_name):
        """Get payment amount by payment method in company currency
        
        Args:
            payment_method_name (str): Payment method name (lowercase)
            
        Returns:
            float: Payment amount in company currency
        """
        payment_amount = 0.0
        # Get all invoices linked to this sale order
        for invoice in self.invoice_ids.filtered(lambda inv: inv.payment_state in ['paid', 'partial']):
            # Get all payments for this invoice
            for payment in invoice._get_reconciled_payments():
                # Check if payment journal name contains the payment method name
                if payment_method_name.lower() in payment.journal_id.name.lower():
                    # Convert payment amount to sale order currency
                    payment_in_invoice_currency = payment.amount
                    if payment.currency_id != invoice.currency_id:
                        payment_in_invoice_currency = payment.currency_id._convert(
                            payment.amount,
                            invoice.currency_id,
                            invoice.company_id,
                            payment.date
                        )
                    # Calculate the payment amount proportional to the invoice amount
                    if invoice.amount_total:
                        payment_ratio = payment_in_invoice_currency / invoice.amount_total
                        # Apply this ratio to the sale order amount and convert to company currency
                        payment_amount += self.get_amount_in_company_currency(self.amount_untaxed * payment_ratio)
        return payment_amount
    
    def get_discount_in_company_currency(self):
        """Get total discount in company currency
        
        Returns:
            float: Discount in company currency
        """
        discount_amount = sum(line.price_unit * line.product_uom_qty * line.discount / 100 for line in self.order_line)
        return self.get_amount_in_company_currency(discount_amount)

    def get_tangent_payment_datas(self):
        """Get payment data for Tangent API
        
        Returns:
            dict: Payment data for Tangent API
        """
        result = {'others': 0.0}
        paid_invoices = self.invoice_ids.filtered(lambda inv: inv.payment_state in ['paid', 'partial', 'in_payment'])
        for invoice in paid_invoices:
            # Convert invoice amount to sale order currency
            invoice_in_sale_currency = invoice.amount_total
            if invoice.currency_id != self.currency_id:
                invoice_in_sale_currency = invoice.currency_id._convert(
                    invoice.amount_total,
                    self.currency_id,
                    self.company_id,
                    invoice.date or invoice.invoice_date
                )
            result['others'] += invoice_in_sale_currency
        return result

    def action_view_api_logs(self):
        """Open API logs related to this sale order"""
        self.ensure_one()
        return {
            'name': _('API Logs for %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'tangent.api.log',
            'view_mode': 'tree,form',
            'domain': [('sale_order_ids', 'in', self.id)],
            'context': {'default_sale_order_ids': [(6, 0, [self.id])]},
        }