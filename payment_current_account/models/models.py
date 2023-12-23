# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Payment(models.Model):
    _inherit = 'account.payment'

    destination_account_id = fields.Many2one(
        domain="[('account_type', 'in', ('asset_receivable','asset_current', 'liability_payable', 'liability_current'))]", )

    def _seek_for_lines(self):
        ''' Helper used to dispatch the journal items between:
        - The lines using the temporary liquidity account.
        - The lines using the counterpart account.
        - The lines being the write-off lines.
        :return: (liquidity_lines, counterpart_lines, writeoff_lines)
        '''
        self.ensure_one()

        liquidity_lines = self.env['account.move.line']
        counterpart_lines = self.env['account.move.line']
        writeoff_lines = self.env['account.move.line']

        for line in self.move_id.line_ids:
            if line.account_id in self._get_valid_liquidity_accounts():
                liquidity_lines += line
            elif line.account_id.account_type in ('asset_receivable', 'asset_current', 'liability_payable',
                                                  'liability_current') or line.account_id == self.company_id.transfer_account_id:
                counterpart_lines += line
            else:
                writeoff_lines += line
        return liquidity_lines, counterpart_lines, writeoff_lines
