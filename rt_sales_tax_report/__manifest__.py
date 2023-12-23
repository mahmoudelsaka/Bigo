# -*- coding: utf-8 -*-
{
    'name': "RT Sales/Purchase Tax",

    'description': """
        RT Sales/Purchase Tax report   
         """,

    'author': "Rightechs Solution",
    'website': "http://rightechs.info",

    'category': 'Extra',
    'version': '0.1',

    'depends': ['base', 'account'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'wizard/tax_report_view.xml'
    ],

}
