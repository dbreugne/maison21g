from odoo import models, fields

class AccountAccount(models.Model):
    _inherit = "account.account"

    account_type = fields.Selection(
        selection_add=[
            ('income_revenue', 'Net Sales (Sell-In)'),
            ('expense_dis_expense', 'Distribution Expenses'),
           ('expense_sell_expense', 'Selling expenses'),
           ('expense_mark_expense', 'Marketing expenses'),
           ('expense_GA_expense', 'G&A expenses'),
           ('expense_da_expense', 'Depricaition and Amortisation'),
        ],
        ondelete={
            'income_revenue': 'cascade',
            'expense_dis_expense': 'cascade',
            'expense_sell_expense': 'cascade',
            'expense_mark_expense': 'cascade',
            'expense_GA_expense': 'cascade',
            'expense_da_expense': 'cascade',
        }
    )
