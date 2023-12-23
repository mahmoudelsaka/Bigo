# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountJournal(models.Model):
	_inherit = 'account.journal'

	payment_sequence_id = fields.Many2one('ir.sequence','Payment Sequence')
	receipt_sequence_id = fields.Many2one('ir.sequence','Receipt Sequence')

class account_bank_statement_line(models.Model):
	_inherit = 'account.bank.statement.line'

	name2 = fields.Char('PO/RO Sequence')

	def set_new_sequence(self):
		receipt_sequence_id = self.journal_id.receipt_sequence_id
		payment_sequence_id = self.journal_id.payment_sequence_id
		for statement in self:
			if statement.amount > 0:
				if receipt_sequence_id:
					new_seq = receipt_sequence_id.next_by_id()
					statement.write({'name2': new_seq})
					# print('backorder_name:----> ', picking.name)
				else:
					statement.name2 = 'Receipt Order'
			if statement.amount < 0:
				if payment_sequence_id:
					new_seq2 = payment_sequence_id.next_by_id()
					statement.write({'name2': new_seq2})
					# print('backorder_name:----> ', picking.name)
				else:
					statement.name2 = 'Payment Order'

		return

	def action_print_voucher(self):
		if not self.name2:
			self.set_new_sequence()
		""" Print Receipt/Payment Vouchers """
		assert len(self) == 1, 'This option should only be used for a single id at a time.'
		return self.env.ref('rt_print_voucher.receipt_payment_voucher').report_action(self)

