{
    'name': 'MS: Invoice Guard',
    'version': '17.0.1.0.0',
    'sequence': 1,
    'category': 'Accounting',
    'description': """
        Block invoice creation from a sale order when the only invoiceable
        amount is negative (e.g. a discount line) while positive product lines
        are still waiting for delivery. Without this guard Odoo turns the
        negative invoice into a Customer Credit Note, which is wrong for
        undelivered e-commerce orders (see CN/2026/0016-0038 incident).
    """,
    'summary': 'Prevent credit notes created by invoicing undelivered orders',
    'author': 'Maison21G',
    'depends': ['sale'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
