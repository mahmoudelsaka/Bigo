# -*- coding: utf-8 -*-
{
    'name': "Update Valuation Layer Value",

    'summary': """
        """,

    'description': """
        Make value and unit value in valuation layer as editable to can update it by importing xlsx sheet.
    """,

    'author': "Rightechs Solutions",
    'website': "http://www.rightechs.info",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock','stock_account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'wizard/update_layer_date.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
