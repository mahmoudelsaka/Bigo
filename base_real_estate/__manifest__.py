# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2023 Rightechs (<http://www.rightechs.net/>)
#               <sale@rightechs.net>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "Base Real Estate",

    'summary': """
        """,

    'description': """
        This module will add :-
            - Unit,Building Menus under account configuration menu.
            - Unit,Building,Project fields in [Cheque, Batch Cheque Invoices, Payment Order, Bank Statement] form view.
            - Create additional entries for collected cheques.
            - Mark invoice as paid auto (Auto Reconciliation) when collect the cheque.
            - Reconcile Check entries
    """,

    'author': "Rightechs Solutions",
    'website': "http://www.rightechs.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Extra',
    'version': '16.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_check_batch', 'rt_account_check',
                'account', 'elsaka_payment_order', 'account_accountant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'security/ir_security.xml',
        'views/receipt_order.xml',
        'views/unit.xml',
        'views/account_check_view.xml',
        'views/check_batch_view.xml',
        'views/account_move_view.xml',
        'views/account_payment_view.xml',
        'views/menus.xml',
        'views/account_bank_statement.xml',
        'views/res_partner_view.xml',
        'wizard/invoices.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}
