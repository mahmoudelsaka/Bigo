# -*- coding: utf-8 -*-
{
    'name': "Rightechs Partner Account Statement",

    'summary': """
    Partner Account Statement
        """,

    'description': """
        Generate XLSX file for Customer Statement.
    """,

    'author': "Rightechs Solutions",
    'website': "http://www.rightechs.info",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'rt_account_check',
                'account_check_batch', 'base_real_estate'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'wizard/partner_account_statement_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
