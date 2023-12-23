
# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _

class InvoiceUpdate(models.Model):
    _name = 'invoice.update'

    def update_data_invoices(self):
        active_ids = self._context.get('active_ids', [])
        invoices = self.env['account.move'].browse(active_ids)
        for rec in invoices:
            # rec.analytic_account_id = self.analytic_account_id.id
            if rec.analytic_account_id or rec.building_id or rec.unit_id:
                for invoices in rec.invoice_line_ids:
                    if invoices.account_id:
                        rec.write(
                            {'analytic_account_id': rec.analytic_account_id.id, 'building_id': rec.building_id.id,
                             'unit_id': rec.unit_id.id, 'installment_type': rec.installment_type})

                    print('====================Analyticc33')
                    partner = rec.partner_id
                    print('====================Analyticc88')
                    if rec.analytic_account_id:
                        for line in rec.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')):
                            if line.account_id.user_type_id.type in ('receivable', 'payable'):
                                print('==================Account RES')
                                # rec.analytic_account_id = res.analytic_account_id.id
                                line.write({'analytic_account_id': invoices.analytic_account_id.id,'building_id':invoices.building_id.id,'unit_id':rec.unit_id.id,'installment_type':invoices.installment_type})






