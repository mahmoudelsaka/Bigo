# -*- coding: utf-8 -*-
{
    'name': " RT Filter By account in Patner Ledger",


    'author': "Rightechs Soluations",
    'website': "www.rightechs.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account Reports',
    'version': '0.15',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_reports'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
