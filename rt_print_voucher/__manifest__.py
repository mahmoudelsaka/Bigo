# -*- coding: utf-8 -*-
{
    'name': "RT Print Voucher",

    'summary': """
        """,

    'description': """
        Add button to print statement line.
    """,

    'author': "Rightechs Solutions",
    'website': "http://www.rightechs.info",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'report/ropo_voucher.xml',
        # 'report/ropo_order.xml',
        'report/report_menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
