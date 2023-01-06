# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'True Mart POS Project',
    'version': '1.0',
    'category': 'True Mart POS Project and Accounting',
    'sequence': 10,
    'summary': 'True Mart POS Project and Accounting',
    'description': """
    
Point of Sale System (Ture Mart) Project
============================================================
True_Mart_POS Project is customized module for Ture Mart to use FutureHub Point of Sale System.

""",
    'author': 'Future Hub Myanmar Co.Ltd.',
    'website': 'www.futurehubmyanmar.com',
    'images': [],
    'depends': ['point_of_sale','account','report_xlsx'],
    'data': [
             'views/pos_product_view.xml',
             'report/product_tag_for_shelves_qweb_report.xml',
             'report/product_tag_for_shelves_template.xml',
             #account reports
             'report/account_report_excel.xml',
             'wizards/account_excel_report.xml',
             'wizards/account_cash_book_wizard_view.xml',
             'report/account_report_cash_book_view.xml',
             #SO PO reports
             'report/tm_excel_report_link_view.xml',
             'wizards/tm_po_report_wizard_view.xml',
             'wizards/tm_so_report_wizard_view.xml',
             'views/hide_create_edit_UpdateQTY_view.xml',
             'views/report_menu_view.xml',
             #top sale reports
#              'report/tm_top_sale_product_report_view.xml',
#              'report/tm_top_pos_product_report_view.xml',
             'security/ir.model.access.csv'
            ],
             
    'qweb': [
        #'static/src/xml/tm_pos.xml',
    ],
    'demo': [ ],
    'test': [],
    'css':[],
    'installable': True,
    'auto_install': False,
}