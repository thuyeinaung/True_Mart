# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Company POS LOGO',
    'version': '11.0.0',
    'category': 'web',
    'sequence': 10,
    'summary': 'Point of Sale',
    'description': """
    
Change Point of Sale Logo.

""",
    'author': 'Future Hub Myanmar Co.Ltd.',
    'website': 'www.futurehubmyanmar.com',
    'images': ['static/src/img'],
    'depends': ['base','web','point_of_sale','base_setup'],
    'data': [   
                 'views/pos_templates.xml',
                 'views/views.xml',
                ],
    'qweb': [
             'static/src/xml/pos.xml',
             'static/src/xml/base.xml'
             ],
    'demo': [],
    'test': [],
#     'css':['/static/src/less/watermark.less'
#            ,'/static/src/css/pas_project_new.css'],
    'installable': True,
    'auto_install': False,
}
