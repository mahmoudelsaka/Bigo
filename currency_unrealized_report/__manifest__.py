# -*- coding: utf-8 -*-
###################################################################################
#
#    Rightechs Solutions.
#    Copyright (C) 2023-TODAY Rightechs Solutions(<https://www.rightechs.info>).
#    Author: Rightechs Solutions (<https://www.rightechs.info>)
#
#    This program is paid software: you can't modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Paid Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
{
    'name': "Revaluation Currency",
    'summary': "Currency Unrealized Report",
    'description': """
        Create move line for each invoice
            -
    """,
    'author': "Rightechs Solutions",
    'website': "https://www.rightechs.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Extra App',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_reports', 'base_real_estate'],

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
