# -*- coding: utf-8 -*-
{
    'name': 'Custom Product Labels',
    'version': '11.0.1.0.1',
    'category': 'Product Management',
    'author': 'Thu Yein Aung',
    'website': "https://www.futurehubmyanmar.com",
    'license': 'LGPL-3',
    'summary': """Print custom product labels""",
    'images': [],
    'description': """
Module allows to print custom product barcode on paper.
Label size: 10px for each product barcode, paperformat: A4 (88 pcs per sheet, 4 pcs x 22 rows).
    """,
    'depends': ['product'],
    'data': [
        'wizard/print_product_label_views.xml',
        'report/product_label_templates.xml',
        'report/product_label_reports.xml',
    ],
    'support': 'thuyeinaung@futurehubmyanmar.com',
    'application': False,
    'installable': True,
    'auto_install': False,
}
