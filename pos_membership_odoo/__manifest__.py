# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "POS Membership Management",
    "version" : "11.0.1.7",
    "category" : "Point of Sale",
    "depends" : ['base','sale','point_of_sale'],
    "author": "BrowseInfo",
    'summary': 'This apps allows your customers to provide Membership Card for provide Discount on their orders.',
    "description": """
    
    Purpose :- 
This apps allows your cutomers to provide Membership Card for provide Discount on their orders.
    POS Membership card Management
    POS Membership Management
    point of sale Membership Management
    point of sales Membership management
    point of sale Membership card Management
    point of sales Membership card management
    Membership card with POS
    Customer Membership with POS
    Customer Membership on  POS
    customer Membership card on POS

    Customer Membership with point of sales
    Customer Membership on  point of sales
    customer Membership card on  point of sales
    customer Membership on POs
    customer Membership on point of sale
    customer Membershipcard on POS
    customer Membershipcard on point of sale
    
    """,
    "website" : "https://www.browseinfo.in",
    "price": 129,
    "currency": "EUR",
    "data": [
        'security/ir.model.access.csv',
        'wizard/pos_top_clients.xml',
        'views/custom_pos_view.xml',
        'views/print_front_img_report.xml',
        'views/print_back_img_report.xml',
        'views/print_full_front_img_report.xml',
        'views/print_full_back_img_report.xml',
        'views/pos_membership.xml',
        'views/membership_code_report.xml',
        'views/report_pos_membership_code.xml',
        'views/top_client_wizard_report.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/0nGQg7AgzQU',
    "images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
