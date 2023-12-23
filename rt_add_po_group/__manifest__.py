# -*- coding: utf-8 -*-
{
    'name': "rt add po group",

    'summary': """
        rt add po group""",

    'description': """
        rt add po group
    """,

    'author': "Rightechs Solutions",
    'website': "https://rightechs.net/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'purchase_request'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/po_groups.xml',
        'views/views.xml',
        'views/templates.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
