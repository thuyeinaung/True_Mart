# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'POS Minimart',
    'version': '11.0.0',
    'category': 'point of sale',
    'sequence': 10,
    'summary': 'pos_minimart',
    'description': """
    
POS Restaurant.

""",
    'author': 'Future Hub Myanmar Co.Ltd.',
    'website': 'www.futurehubmyanmar.com',
    'depends': ['base','product','point_of_sale','web'],
    'data': [   
                  'data/report_paperformat.xml'
                  ,'reports/pos_qweb_report.xml'
                  ,'reports/pos_product_label_template.xml'
                ],
    'images': [],
    'qweb': [ 
            
         ],
    'demo': [],
    'test': [],

    'installable': True,
    'auto_install': False,
}
