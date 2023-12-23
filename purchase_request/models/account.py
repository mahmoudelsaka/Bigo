# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models, api


class AccountRequest(models.Model):
    _inherit = "account.account"

    is_request = fields.Boolean('Is Request')


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends('display_type', 'company_id')
    def _compute_account_id(self):
        res = super(AccountMoveLine, self)._compute_account_id()
        product_lines = self.filtered(lambda line: line.display_type == 'product' and line.move_id.is_invoice(True))
        for rec in product_lines:
            if rec.move_id.is_purchase_document(include_receipts=True):
                if rec.product_id:
                    if rec.product_id.detailed_type != 'product':
                        purchase_line_id = rec.purchase_line_id.id
                        gl_account_id = rec.purchase_line_id.gl_account_id.id
                        rec.account_id = gl_account_id
        return res
