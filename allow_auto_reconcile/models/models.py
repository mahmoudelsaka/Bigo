# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class AccountCheck(models.Model):
    _inherit = 'account.check'

    def _reconcile_auto_invoices(self, move_id):
        payment_type = self.installment_type
        # if self.installment_type == 'unit':
        #     payment_type = 'unit'
        invoices = self.env['account.move'].sudo().search([
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('partner_id', '=', self.partner_id.id),
            ('analytic_account_id', '=', self.analytic_account_id.id),
            ('building_id', '=', self.building_id.id),
            ('unit_id', '=', self.unit_id.id),
            ('company_id', '=', self.company_id.id),
            ('installment_type', '=', payment_type),
            ('amount_residual', '>', 0)
        ], order='invoice_date_due asc')

        if not invoices:
            invoices = self.env['account.move'].sudo().search([
                ('move_type', '=', 'entry'),
                ('partner_id', '=', self.partner_id.id),
                ('rejected_check_id', '=', self.id),
                ('company_id', '=', self.company_id.id),
            ])
        print('invoices ======= ', invoices)
        for invoice in invoices:
            print('invoice ========== TBR ===== ', invoice)
            if invoice.state == 'posted':
                for line in move_id.line_ids:
                    if line.account_id.reconcile and not line.reconciled:
                        if self.company_id and self.company_id.invoice_auto_reconcile:
                            invoice.js_assign_outstanding_line(line.id)
                            print('====== invoice is reconciled ==== ')

    def _reconcile_entries(self, move_id):
        entries = self.env['account.move'].sudo().search([
            ('move_type', '=', 'entry'),
            # ('partner_id', '=', self.partner_id.id),
            ('rejected_check_id', '=', self.id),
            ('company_id', '=', self.company_id.id),
        ])
        print('entries ======= ', entries)
        for mv in entries:
            print('entries ========== TBR ===== ', mv)
            if mv.state == 'posted':
                for line in move_id.line_ids:
                    if line.account_id.reconcile and not line.reconciled:
                        if self.company_id and self.company_id.entry_auto_reconcile:
                            mv.js_assign_outstanding_line(line.id)
                            print('====== entries is reconciled ==== ')
