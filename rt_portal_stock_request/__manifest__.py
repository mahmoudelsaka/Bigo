# -*- coding: utf-8 -*-
{
    'name': "Rt portal stock request ",

    'summary': """
        Rt portal stock request""",

    'description': """
        Rt portal stock request
    """,

    'author': "Rightechs Solutions",
    'website': "https://rightechs.net/",
    'license': 'AGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '0.16',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'stock_request', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/user.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/account.xml',
    ],
    "assets": {
        'web.assets_frontend': [
            "/rt_portal_stock_request/static/src/js/user_portal.js",
            "/rt_portal_stock_request/static/src/js/search_product.js",
            "/rt_portal_stock_request/static/src/xml/search_product.xml",
        ]
    },
    'demo': [
        'demo/demo.xml',
    ],
}
