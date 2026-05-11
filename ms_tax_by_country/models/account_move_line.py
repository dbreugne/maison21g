from odoo import api, models

TAX_SINGAPORE_NAMES = ['Sales Tax 9% SR', '[old] Sales Tax 9% SR']
TAX_SINGAPORE_LABEL = '9% SR'
TAX_INTERNATIONAL_NAMES = ['Sales Tax 0% ZR']
TAX_INTERNATIONAL_LABEL = '0% ZR'
SINGAPORE_COUNTRY_CODE = 'SG'


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _get_sg_tax_by_country(self, country):
        """Return the correct GST tax based on shipping country."""
        if country.code == SINGAPORE_COUNTRY_CODE:
            names = TAX_SINGAPORE_NAMES
            label = TAX_SINGAPORE_LABEL
        else:
            names = TAX_INTERNATIONAL_NAMES
            label = TAX_INTERNATIONAL_LABEL

        company_id = self.company_id.id
        for name in names:
            tax = self.env['account.tax'].search([
                ('name', '=', name),
                ('type_tax_use', '=', 'sale'),
                ('company_id', '=', company_id),
                ('active', '=', True),
            ], limit=1)
            if tax:
                return tax

        return self.env['account.tax'].search([
            ('description', '=', label),
            ('type_tax_use', '=', 'sale'),
            ('company_id', '=', company_id),
            ('active', '=', True),
        ], limit=1)

    @api.depends('move_id.partner_shipping_id.country_id')
    def _compute_tax_ids(self):
        super()._compute_tax_ids()
        for line in self:
            if line.display_type in ('line_section', 'line_note', 'payment_term'):
                continue
            if not line.move_id.is_sale_document(include_receipts=True):
                continue
            country = line.move_id.partner_shipping_id.country_id
            if not country:
                continue
            tax = line._get_sg_tax_by_country(country)
            if tax:
                line.tax_ids = tax
