##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
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
    'name': 'Account Check Management',
    'version': '16.0.0.1',
    'category': 'Accounting',
    'summary': 'Accounting, Payment, Check, Third, Issue',
    'author': 'Rightechs Solutions',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        # for bank and cash menu and also for better usability
        'rt_account_payment_fix',
        'sale', 'account_accountant', 'account'
    ],
    'data': [
        'data/account_payment_method_data.xml',
        # 'data/ir_actions_server_data.xml',
        'wizard/account_check_action_wizard_view.xml',
        'wizard/print_pre_numbered_checks_view.xml',
        'wizard/res_config_settings_view.xml',
        'views/account_payment_view.xml',
        'views/account_check_view.xml',
        'views/account_journal_dashboard_view.xml',
        'views/account_journal_view.xml',
        'views/account_checkbook_view.xml',
        'views/account_chart_template_view.xml',
        'security/ir.model.access.csv',
        'security/account_check_security.xml',
        'views/check_view_inherit.xml',
        'wizard/internal_check_wiz.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
