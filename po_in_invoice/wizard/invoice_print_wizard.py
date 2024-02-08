from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError


class CustomerDataWizard(models.TransientModel):
    """Create a new wizard customer.data.wizard"""
    _name = 'customer.data.wizard'
    _description = 'Wizard to generate the customer data report'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)

    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")

    def print_report(self):
        domain = []
        if self.partner_id:
            domain.append(("partner_id", '=', self.partner_id.id))
        if self.from_date:
            domain.append(("invoice_date", '>=', self.from_date))
        if self.to_date:
            domain.append(("invoice_date", '<=', self.to_date))
        invoices = self.env['account.move'].search(domain)
        if not invoices:
            raise UserError(_('There are no record found for the Customer: %s ') % (self.partner_id.name))

        return self.env.ref('account.account_invoices').report_action(invoices)
