# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'POS Coupons & Promotions',
    'version': '1.2',
    'summary': """Allows to use discount coupons and promotions in pos orders.
    
    
    Integrate coupon and promotion mechanism in pos order.
        
        pos promotion
pos coupon
pos promotion coupon
pos promotion and coupon
pos promotion programme
coupon on pos
coupon on ecommerce
coupon on sales
sales coupon
ecommerce coupon
ecommerce promotion
point of sale coupon
point of sale promotion
point of sale programme
point of sale promotion coupon
point of sale coupon code
sales promotion
sales promotion programme
discount
sales discount
ecommerce discount
pos discount
point of sale discount
website
seller
product
seller product
best product
ecommerce product
ecommerce best seller
ecommerce best seller product
top selling product
top product
top selling ecommerce product
top selling website product
point of sale top selling product
point of sale top selling item
point of sale top product
point of sale top product selling
pos top selling product
post top selling item
pos top product
pos excel report
pos excel export
POS reward
point of sale reward
pos invoice
sale coupon
promotion
coupon
sale
product promotion
product discount
sales order discount
manufacturing
retailer
retail store
promo code
promotion code
coupon code
customer
customer discount
Reward
shipping
free shipping
fix price discount
percentage discount
promotion validity
minimum purchase
purchase
shoppers
Free product
Free item
free
coupon code validity
special offer
festival
christmas
redemption
claim
expire
redeem
sale promotion
pos receipt
POS Promotional programm 
All in one
all in one coupon
all in one promo code
company logo
POS session
POS logo on session
POS logo on receipt
POS receipt company logo
POS receipt company address
POS session company logo
POS session company address
Point of sale company logo
point of sale receipt company logo
point of sale receipt logo
point of sale receipt address
point of sale session logo
    """,
    'category': 'Point Of Sale',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'www.synconics.com',
    'description': """
        Integrate coupon and promotion mechanism in pos order.
    """,
    'depends': ['sale_coupon', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/point_of_sale.xml',
        'views/pos_config_views.xml',
        'views/sale_coupon_program_views.xml',
        'views/sale_coupon_views.xml',
        'views/pos_order_views.xml',
        'report/pos_order_report_views.xml'
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'images': [
        'static/description/main_screen.png',
    ],
    'price': 70.0,
    'currency': 'EUR',
    'auto_install': False,
    'application': True,
    'installable': True,
    'license': 'OPL-1',
}
