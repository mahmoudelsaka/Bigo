# -*- coding: utf-8 -*-

###################################################################################

#    Rightechs Solutions.
#    Copyright (C) 2021-TODAY Rightechs Solutions(<https://www.rightechs.info>).
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
    'name': "Account Cheque Batch",

    'summary': """
        """,

    'description': """
        This module will add :
        1- In Account Config Setting :-
           A- Advanced Payment Account type of receivable.
           B- Installment Account type of receivable.
        2- In Cheque Views two boolean fields :-
           A- Installment.
           B- Advanced Payment.
       3- Cheque Batch Menu: to create batch Cheques.
       4- Print Cheque Batch Report AS PDF
    """,

    'author': "Rightechs Solutions",
    'website': "http://www.rightechs.info",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '16.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'rt_account_check',
                'rt_account_payment_fix', 'account_accountant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml',
        'views/account_check_batch_view.xml',
        'wizard/res_config_settings.xml',
        'report/check_batch_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}
