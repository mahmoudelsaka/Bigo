# -*- coding: utf-8 -*-
{
    'name': "Rt custom currencies rate",

    'summary': """
        Rt custom currencies rate""",

    'description': """
        Rt custom currencies rate
    """,

    'author': "Rightechs Solutions",
    'website': "https://rightechs.net/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_reports'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
