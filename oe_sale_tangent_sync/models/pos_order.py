# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import groupby

class POSOrder(models.Model):
    _inherit = 'pos.order'
    
    tangent_api_sync_date = fields.Datetime('Tangent API Sync Date', readonly=True,
                                          help="Date and time when this order was last synchronized with Tangent API")
    tangent_api_id = fields.Many2one('tangent.api.config', 'Tangent API ID', readonly=True,
                                   help="The Tangent API ID used for synchronizing this order")
    tangent_api_response = fields.Text('Tangent API Response', readonly=True,
                                     help="Last response received from Tangent API for this order")
    
    # Many2many relation to API logs
    tangent_api_log_ids = fields.Many2many('tangent.api.log', 'tangent_api_log_pos_order_rel',
                                         'pos_order_id', 'log_id', string='API Logs',
                                         help="API synchronization logs for this order")
    
    def get_amount_in_company_currency(self, amount):
        """Convert an amount from the order currency to company currency
        
        Args:
            amount (float): Amount in order currency
            
        Returns:
            float: Amount converted to company currency
        """
        self.ensure_one()
        company_currency = self.company_id.currency_id
        
        if self.currency_id == company_currency:
            return amount
        else:
            return self.currency_id._convert(
                amount,
                company_currency,
                self.company_id,
                self.date_order.date()
            )
    
    def get_gto_in_company_currency(self):
        """Get GTO (Grand Total Order) in company currency
        GTO is the total amount after discount and before tax
        
        Returns:
            float: GTO amount in company currency
        """
        self.ensure_one()
        # GTO = amount_total - amount_tax
        gto = self.amount_total - self.amount_tax
        return self.get_amount_in_company_currency(gto)
    
    def get_gst_in_company_currency(self):
        """Get GST (tax) amount in company currency
        
        Returns:
            float: GST amount in company currency
        """
        self.ensure_one()
        return self.get_amount_in_company_currency(self.amount_tax)
    
    def get_discount_in_company_currency(self):
        """Get total discount amount in company currency
        
        Returns:
            float: Discount amount in company currency
        """
        self.ensure_one()
        # Calculate total discount from order lines
        discount_total = sum(line.price_unit * line.qty * line.discount / 100 for line in self.lines)
        return self.get_amount_in_company_currency(discount_total)
    
    def get_tangent_payment_datas(self):
        result = {}
        skipped_payment_types = ['master', 'no_sync']
        for payment_type, payments in groupby(self.payment_ids, key=lambda p: p.payment_method_id.tangent_payment_type):
            if payment_type not in skipped_payment_types:
                if payment_type not in result.keys():
                    result[payment_type] = 0
                for payment in payments:
                    result[payment_type] += payment.pos_order_id.get_amount_in_company_currency(payment.amount)
        return result

    def get_payment_amount_by_method_in_company_currency(self, method_name=False):
        """Get payment amount for a specific payment method in company currency
        
        Args:
            method_name (str): Name of the payment method (case insensitive)
            
        Returns:
            float: Payment amount in company currency
        """
        self.ensure_one()
        result = {}
        # Find payments with matching method name (case insensitive)
        matching_payments = self.payment_ids.filtered(
            lambda p: p.payment_method_id.name.lower() == method_name.lower()
        )
        # Sum the amounts and convert to company currency
        if not matching_payments:
            return 0
        payment_total = sum(payment.amount for payment in matching_payments)
        self.get_amount_in_company_currency(payment_total)
        return result
        
    def get_voucher_amount_from_coupons(self):
        """Get voucher amount from coupons or loyalty programs used in the order
        
        This method checks if the pos_loyalty module is installed and retrieves
        the value of coupons or loyalty programs used in the order.
        
        Returns:
            float: Voucher amount in company currency
        """
        self.ensure_one()
        voucher_amount = 0
        
        # Check if pos_loyalty module is installed
        if not self.env.get('loyalty.card') or not self.env.get('pos.order.line'):
            return self.get_payment_amount_by_method_in_company_currency('voucher')
            
        # Get order lines that are associated with a coupon
        coupon_lines = self.lines.filtered(lambda line: hasattr(line, 'coupon_id') and line.coupon_id)
        
        if coupon_lines:
            # Sum the price of all coupon lines (negative values represent discounts)
            for line in coupon_lines:
                # Only count negative values as these represent discounts/vouchers applied
                if line.price_subtotal < 0:
                    voucher_amount += abs(line.price_subtotal)
        
        # If no coupon lines found, fall back to payment method
        if voucher_amount == 0:
            voucher_amount = self.get_payment_amount_by_method_in_company_currency('voucher')
            
        return self.get_amount_in_company_currency(voucher_amount)

    def action_view_api_logs(self):
        """Open API logs related to this POS order"""
        self.ensure_one()
        return {
            'name': _('API Logs for %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'tangent.api.log',
            'view_mode': 'tree,form',
            'domain': [('pos_order_ids', 'in', self.id)],
            'context': {'default_pos_order_ids': [(6, 0, [self.id])]},
        }
