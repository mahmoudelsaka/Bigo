# -*- coding: utf-8 -*-
{
    'name': "Purchase Order Access",

    'summary': """
       """,

    'description': """
        This Module will:-
            - Add a new access rule to purchase user to see his orders only
            -  Add a new access rule to purchase manager to see all orders
    """,

    'author': "Rightechs Solutions",
    'website': "https://www.rightechs.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Base',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/ir_security.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
