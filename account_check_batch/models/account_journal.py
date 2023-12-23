from odoo import models,fields,api,_


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    payment_debit_account_id = fields.Many2one(
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id)]")
    payment_credit_account_id = fields.Many2one(
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id)]" )
    suspense_account_id = fields.Many2one(
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id), \
                                 ('account_type', 'not in', ('receivable', 'payable'))]")
    default_account_id = fields.Many2one(

        domain="[('deprecated', '=', False), ('company_id', '=', company_id),"
               "('account_type', 'not in', ('receivable', 'payable'))]")
