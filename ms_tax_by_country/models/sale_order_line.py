from odoo import api, models

# Search priority: exact name first, then fallback to label on invoices
TAX_SINGAPORE_NAMES = ['Sales Tax 9% SR', '[old] Sales Tax 9% SR']
TAX_SINGAPORE_LABEL = '9% SR'
TAX_INTERNATIONAL_NAMES = ['Sales Tax 0% ZR']
TAX_INTERNATIONAL_LABEL = '0% ZR'
SINGAPORE_COUNTRY_CODE = 'SG'


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _get_tax_by_country(self, country):
        """Return the correct sales tax based on shipping country."""
        if country.code == SINGAPORE_COUNTRY_CODE:
            names = TAX_SINGAPORE_NAMES
            label = TAX_SINGAPORE_LABEL
        else:
            names = TAX_INTERNATIONAL_NAMES
            label = TAX_INTERNATIONAL_LABEL

        company_id = self.company_id.id
        # Try each name in priority order
        for name in names:
            tax = self.env['account.tax'].search([
                ('name', '=', name),
                ('type_tax_use', '=', 'sale'),
                ('company_id', '=', company_id),
                ('active', '=', True),
            ], limit=1)
            if tax:
                return tax

        # Fallback: match by invoice label (description)
        return self.env['account.tax'].search([
            ('description', '=', label),
            ('type_tax_use', '=', 'sale'),
            ('company_id', '=', company_id),
            ('active', '=', True),
        ], limit=1)

    @api.depends('order_id.partner_shipping_id.country_id')
    def _compute_tax_id(self):
        super()._compute_tax_id()
        for line in self:
            country = line.order_id.partner_shipping_id.country_id
            if not country:
                continue
            tax = line._get_tax_by_country(country)
            if tax:
                line.tax_id = tax
