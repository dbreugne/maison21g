{
    "name": "INOM Customer Classification Enhanced",
    "version": "17.0.1.0.0",
    "summary": "Channel / Category / Sub-Category classification with SO & Invoice cascade",
    "author": "INOM ERP",
    "license": "LGPL-3",
    "category": "Sales",
    "depends": ["base", "contacts", "sale_management", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/channel_views.xml",
        "views/category_views.xml",
        "views/subcategory_views.xml",
        "views/hq_category_views.xml",
        "views/res_partner_views.xml",
        "views/sale_order_views.xml",
        "views/account_move_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": False
}