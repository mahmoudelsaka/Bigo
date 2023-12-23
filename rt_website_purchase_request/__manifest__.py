# -*- coding: utf-8 -*-
{
    'name': "Portal Purchase Request",

    'summary': """
        Rt website purchase  request""",

    'description': """
        Rt website purchase request
    """,

    'author': "Rightechs Solutions",
    'website': "https://rightechs.net/",
    'license': 'AGPL-3',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    # for the full list
    'category': 'website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    # any module necessary for this one to work correctly
    # any module necessary for this one to work correctly
    'depends': ['base', "purchase_stock", "purchase_requisition", 'account', 'website', 'purchase_request', 'portal'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/purchase_request.xml',
        'views/users.xml',
        'views/dashboard.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/purchase_order_line.xml',
        'views/purchase_request_line.xml',

    ],
    "assets": {
        'web.assets_frontend': [
            "/rt_website_purchase_request/static/src/js/user_portal.js",
            "/rt_website_purchase_request/static/src/js/button_search.js",
            "/rt_website_purchase_request/static/src/js/select_product.js",
            '/rt_website_purchase_request/static/xml/search_component.xml',
        ]
    },

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
