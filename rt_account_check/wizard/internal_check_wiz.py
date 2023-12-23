from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError
import logging

_logger = logging.getLogger(__name__)


class AccountPayementInternalCheck(models.TransientModel):
    _name = 'account.payment.internal.check'

    def set_check_state(self):
        state = False
        check_ids = self.env['account.check']
        for rec in check_ids.browse(self.env.context['active_ids']):
            if rec[0].state == 'transfered':
                state = 'transfered'
            elif rec[0].state == 'handed':
                state = 'handed'
            elif rec[0].state == 'rejected':
                state = 'rejected'
            elif rec[0].state == 'holding':
                state = 'holding'
            elif rec[0].state == 'deposited':
                state = 'deposited'
            else:
                state = 'holding'
        return state

    date = fields.Date('Date', default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', 'Partner')
    destination_journal_id = fields.Many2one('account.journal', 'Destination Journal(Bank)',
                                             domain=[('type', 'in', ('cash', 'bank'))])
    treasury_id = fields.Many2one('account.journal', 'Destination Journal(Cash)', domain=[('type', '=', 'cash')])
    destination_account_id = fields.Many2one('account.account', 'Destination Account')
    transfer_state = fields.Selection([
        # ('returned', 'Returned'),
        ('deposited', 'Collected'),
        # ('selled', 'Selled'),
        ('delivered', 'Replaced'),
        ('cashed', 'Cashed'),
        ('rejected', 'Rejected'),
        ('holding', 'Holding')
    ], 'Next Status', )

    holding_state = fields.Selection([
        ('transfered', 'Under Collection'),
        # ('selled', 'Selled'),
        ('delivered', 'Replaced'),
        ('cashed', 'Cashed'),
    ], 'Next Status', default='transfered')

    # reject_state = fields.Selection([
    #     ('returned', 'Returned'),
    # ], 'Next Status', default='returned')

    check_state = fields.Selection([
        ('holding', 'Holding'),
        ('deposited', 'Collected'),
        ('transfered', 'Under Collection'),
        ('handed', 'Handed'),
    ], default=set_check_state)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.destination_account_id = self.partner_id.property_account_receivable_id.id or False

    @api.onchange('check_state')
    def onchange_states(self):
        if self.check_state == 'holding':
            self.transfer_state = None
            # self.reject_state = None
            self.holding_state = 'transfered'

        if self.check_state == 'transfered':
            self.holding_state = None
            # self.reject_state = None
            # self.transfer_state = 'returned'

        # if self.check_state == 'rejected':
        #     # self.transfer_state = None
        #     self.holding_state = None
        #     self.reject_state = 'returned'

        if self.check_state == 'handed':
            # self.transfer_state = 'rejected'
            self.holding_state = None
            # self.reject_state = None

    def get_credit_debit_accounts(self):
        pass

    def create_internal_entries(self):
        check_ids = self.env['account.check']
        move_ids = []
        journal_ids = []
        company_ids = []
        amount = 0.0
        debit_account = False
        credit_account = False
        partner_id = False
        journal = False
        ref = ''
        inv_account = False
        company_id = self.env.user.company_id
        print('############### ', company_id)
        for rec in check_ids.browse(self.env.context['active_ids']):
            if self.transfer_state == 'holding':
                if not self.destination_journal_id:
                    raise UserError(_('Select Destination Journal Fisrt!'))
                ref = 'Holding Checks - ' + self.destination_journal_id.name
                journal = self.destination_journal_id and self.destination_journal_id.id
                for debit in self.destination_journal_id.inbound_payment_method_line_ids:
                    if debit.payment_method_id.name == 'Received Third Check' or debit.payment_method_id.name == 'Manual':
                        debit_account = debit.payment_account_id.id
                        print('=================debit================', debit_account)

                for res in rec.journal_id.inbound_payment_method_line_ids:
                    if res.payment_method_id.name == 'Received Third Check' or res.payment_method_id.name == 'Manual':
                        credit_account = res.payment_account_id.id
                    print('=================debit================', credit_account)
                # credit_account = rec.journal_id.default_account_id and rec.journal_id.default_account_id.id
                partner_id = rec.partner_id and rec.partner_id.id or False
                rec.write({'state': 'holding'})

            if self.holding_state == 'transfered':
                if not self.destination_journal_id:
                    raise UserError(_('Select Destination Journal Fisrt!'))
                ref = 'Transfer Checks - ' + self.destination_journal_id.name
                journal = self.destination_journal_id and self.destination_journal_id.id
                for res in rec.journal_id.inbound_payment_method_line_ids:
                    if res.payment_method_id.name == 'Received Third Check' or res.payment_method_id.name == 'Manual':
                        credit_account = res.payment_account_id.id

                    print('=================credit_account================', credit_account)
                for jour in self.destination_journal_id.inbound_payment_method_line_ids:
                    if jour.payment_method_id.name == 'Manual':
                        debit_account = jour.payment_account_id.id
                        print('=================debit================', debit_account)

                    elif jour.payment_method_id.name == 'Received Third Check':
                        debit_account = jour.payment_account_id.id
                # credit_account = rec.journal_id.default_account_id and rec.journal_id.default_account_id.id
                partner_id = rec.partner_id and rec.partner_id.id or False
                rec.write({'state': 'transfered'})

            if self.holding_state == 'delivered' and self.check_state == 'deposited':
                ref = ('Replace Check nbr %s - ' + rec.journal_id.name) % (rec.name)
                debit_account = self.destination_account_id and self.destination_account_id.id
                journal = rec.journal_id and rec.journal_id.id
                credit_account = rec.journal_id.default_account_id and rec.journal_id.default_account_id.id
                partner_id = rec.partner_id and rec.partner_id.id or False
                rec.write({'state': 'delivered'})

            if self.transfer_state == 'deposited':
                ref = ('Deposited Check nbr %s - ' + rec.journal_id.name) % (rec.name)
                journal = rec.journal_id and rec.journal_id.id
                for res in rec.journal_id.inbound_payment_method_line_ids:
                    if res.payment_method_id.name == 'Received Third Check' or res.payment_method_id.name == 'Manual':
                        credit_account = res.payment_account_id.id
                        print('================= credit_account ================', credit_account)
                debit_account = rec.journal_id.default_account_id and rec.journal_id.default_account_id.id
                # credit_account = rec.journal_id.payment_debit_account_id and rec.journal_id.payment_debit_account_id.id
                partner_id = rec.partner_id and rec.partner_id.id or False
                rec.write({'state': 'deposited'})

            if self.transfer_state == 'selled' or self.holding_state == 'selled':
                if rec.state == 'holding':
                    ref = 'Delivered Checks  nbr %s - %s' % (rec.name, self.treasury_id.name)
                    journal = self.treasury_id and self.treasury_id.id
                    debit_account = self.treasury_id.default_account_id and self.treasury_id.default_account_id.id
                    credit_account = rec.journal_id.payment_credit_account_id and rec.journal_id.payment_credit_account_id.id
                    partner_id = rec.partner_id and rec.partner_id.id or False
                if rec.state == 'transfered':
                    if not self.treasury_id:
                        raise UserError(_('Select Cash Journal Fisrst!'))

                    ref = 'Selled Checks nbr %s - %s ' % (rec.name, self.treasury_id.name)
                    journal = self.treasury_id and self.treasury_id.id
                    debit_account = self.treasury_id.default_account_id and self.treasury_id.default_account_id.id
                    credit_account = rec.journal_id.payment_debit_account_id and rec.journal_id.payment_debit_account_id.id
                    partner_id = rec.partner_id and rec.partner_id.id or False
                rec.write({'state': 'selled'})

            if self.transfer_state == 'rejected' or self.holding_state == 'rejected':
                ref = 'Rejected Check nbr %s - %s ' % (rec.name, rec.journal_id.name)
                print('-----------------Ref-----------------', ref)
                journal = rec.journal_id and rec.journal_id.id
                account = company_id._get_check_account('rejected')
                debit_account = account and account.id
                for res in rec.journal_id.inbound_payment_method_line_ids:
                    if res.payment_method_id.name == 'Received Third Check' or res.payment_method_id.name == 'Manual':
                        credit_account = res.payment_account_id.id
                        print('=================credit_account================', credit_account)
                # credit_account = rec.journal_id.default_account_id and rec.journal_id.default_account_id.id
                partner_id = self.partner_id and self.partner_id.id or False
                rec.write({'state': 'rejected'})

            if self.check_state != 'deposited' and self.transfer_state == 'delivered' or self.check_state != 'deposited' and self.holding_state == 'delivered':
                ref = 'Delivered Check nbr %s - %s ' % (rec.name, rec.journal_id.name)
                journal = rec.journal_id and rec.journal_id.id
                debit_account = self.destination_account_id and self.destination_account_id.id
                for res in rec.journal_id.inbound_payment_method_line_ids:
                    if res.payment_method_id.name == 'Received Third Check' or res.payment_method_id.name == 'Manual':
                        credit_account = res.payment_account_id.id
                # credit_account = rec.journal_id.payment_debit_account_id and rec.journal_id.payment_debit_account_id.id
                partner_id = rec.partner_id and rec.partner_id.id or False
                rec.write({'state': 'delivered'})

            if self.transfer_state == 'cashed' or self.holding_state == 'cashed':
                ref = 'Cached Check nbr %s - %s ' % (rec.name, rec.journal_id.name)
                journal = rec.journal_id and rec.journal_id.id
                for res in rec.journal_id.inbound_payment_method_line_ids:
                    if res.payment_method_id.name == 'Received Third Check' or res.payment_method_id.name == 'Manual':
                        credit_account = res.payment_account_id.id
                debit_account = self.destination_account_id and self.destination_account_id.id
                # credit_account = rec.journal_id.payment_debit_account_id and rec.journal_id.payment_debit_account_id.id
                partner_id = rec.partner_id and rec.partner_id.id or False
                rec.write({'state': 'cashed'})

            if self.transfer_state == 'returned':
                sale_journal = self.env['account.journal'].search(
                    [('type', '=', 'sale'), ('company_id', '=', rec.company_id.id)])
                journal = sale_journal[0].id
                if rec.state == 'transfered':
                    ref = 'Retruned Check nbr %s - %s ' % (rec.name, rec.journal_id.name)
                    journal = rec.journal_id and rec.journal_id.id
                    debit_account = rec.partner_id.property_account_receivable_id and rec.partner_id.property_account_receivable_id.id or False
                    partner_id = rec.partner_id and rec.partner_id.id or False
                    credit_account = rec.journal_id.payment_debit_account_id and rec.journal_id.payment_debit_account_id.id

                if rec.state == 'rejected':
                    ref = 'Returned Check nbr %s - %s ' % (rec.name, rec.journal_id.name)
                    journal = rec.journal_id and rec.journal_id.id
                    partner_id = rec.partner_id and rec.partner_id.id or False
                    debit_account = rec.partner_id.property_account_receivable_id and rec.partner_id.property_account_receivable_id.id or False
                    credit_account = company_id._get_check_account('rejected').id
                rec.write({'state': 'returned'})
            print('invoice_account_line ', inv_account)

            amount = rec.amount
            _logger.info('amount ============================ %s' % amount)

            journal_ids.append(rec.journal_id)
            company_ids.append(rec.company_id)
            for jo in journal_ids:
                if jo and (rec.journal_id.id != jo.id):
                    raise UserError(_('Journal it\'s not matching for selected checks'))
            for com in company_ids:
                if com and (rec.company_id.id != com.id):
                    raise UserError(_('Checks must be in the same company.'))

            if self.transfer_state in ['deposited', 'rejected', 'delivered', 'holding', 'selled', 'returned', 'cashed'] \
                    or self.holding_state in ['transfered', 'rejected', 'delivered', 'selled', 'cashed']:
                move_id = self.create_move_entries(journal, ref, rec, partner_id, amount, debit_account, credit_account)

            if self.destination_journal_id:
                rec.write({'journal_id': self.destination_journal_id.id})
        return

    def convert_amount_currency_to_company_currency(self, check, amount_currency, ):
        company = check.company_id
        balance = check.currency_id._convert(amount_currency, company.currency_id, company, self.date)
        return balance

    def create_move_entries(self, journal, ref, rec, partner_id, amount, debit_account, credit_account):
        move_data = self.prepare_move_vals(journal, ref, rec, partner_id, amount, debit_account, credit_account)
        _logger.info('move_data222 ============================ %s' % move_data)

        move_id = self.env['account.move'].create(move_data)
        move_id.action_post()
        print('move_id ================= ', move_id)
        return move_id

    def prepare_move_line_vals(self, ref, partner_id, amount, debit_account, credit_account, rec):
        currency = rec.currency_id and rec.currency_id.id
        balance = amount
        amount_currency = amount
        default_company_currency = self.env.user.company_id.currency_id
        if rec.currency_id.id != default_company_currency.id:
            balance = self.convert_amount_currency_to_company_currency(rec, amount)
            amount_currency = amount
            _logger.info('balance ============================ %s' % balance)

        line_ids = []
        debit_line = {
            'name': ref,
            'partner_id': partner_id,
            'debit': balance,
            'credit': 0.0,
            'account_id': debit_account,
            'amount_currency': amount_currency,
            'currency_id': currency,

        }
        _logger.info('debit_line ============================ %s' % debit_line)

        line_ids.append((0, 0, debit_line))
        credit_line = {
            'name': ref,
            'partner_id': partner_id,
            'debit': 0.0,
            'amount_currency': -1 * amount_currency,
            'currency_id': currency,
            'credit': balance,
            'account_id': credit_account, }

        line_ids.append((0, 0, credit_line))
        _logger.info('line_ids ============================ %s' % line_ids)

        return line_ids

    def prepare_move_vals(self, journal, ref, rec, partner_id, amount, debit_account, credit_account):
        line_ids = self.prepare_move_line_vals(ref, partner_id, amount, debit_account, credit_account, rec)
        move_data = {
            'journal_id': journal,
            'ref': ref,
            'date': self.date,
            'currency_id': rec.currency_id and rec.currency_id.id or False,
            'move_type': 'entry',
            'rejected_check_id': rec.id,
            'line_ids': line_ids
        }
        print('move_data ', move_data)
        _logger.info('move_data ============================ %s' % move_data)
        return move_data

    # It's not working now, bcz system will create journal entries instead off customer invoice
    def create_debit_note(self, journal, rec, amount, inv_account):
        name = 'Rejected Check - ' + rec.name
        inv_line_ids = {
            # 'product_id':False,
            'account_id': inv_account,
            'price_unit': amount,
            'name': 'Rejected Check nbr - ' + rec.name
        }
        inv_vals = {
            'rejected_check_id': rec.id,
            'ref': name,
            'invoice_date': self.date,
            'invoice_origin': _(name),
            'journal_id': journal,
            'partner_id': rec.partner_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': [(0, 0, inv_line_ids)],
        }
        print('************ inv_vals ********** ', inv_vals)
        invoice = self.env['account.move'].create(inv_vals)
        invoice.action_post()
        print('invoice - ----- ', invoice)
        return

    # def create_move_entries(self, journal, ref, rec, partner_id, amount, debit_account, credit_account):
    #     currency = False
    #     debit = 0.0
    #     credit = 0.0
    #     amount_currency = 0.0
    #     default_company_currency = self.env.user.company_id.currency_id
    #     if rec.currency_id.id != default_company_currency.id:
    #         debit, credit = self.convert_amount_currency_to_company_currency(rec, amount)
    #         print('debit ========== credit =============== ', debit, credit)
    #         currency = rec.currency_id and rec.currency_id.id
    #         amount_currency = amount
    #     else:
    #         debit = amount
    #         credit = amount
    #         # currency = False
    #         # amount_currency = 0.0
    #     move_data = {
    #         'journal_id': journal,
    #         'ref': ref,
    #         'date': self.date,
    #         'move_type': 'entry',
    #         'rejected_check_id': rec.id,
    #         'line_ids': [
    #             (0, 0, {
    #                 'name': ref,
    #                 'date_maturity': rec.payment_date,
    #                 'partner_id': partner_id,
    #                 'debit': debit,
    #                 'currency_id': currency,
    #                 'amount_currency': amount_currency,
    #                 'credit': 0.0,
    #                 'account_id': debit_account,
    #             }),
    #             (0, 0, {
    #                 'name': ref,
    #                 'date_maturity': rec.payment_date,
    #                 'partner_id': partner_id,
    #                 'debit': 0.0,
    #                 'credit': credit,
    #                 'currency_id': currency,
    #                 'amount_currency': -amount_currency,
    #                 'account_id': credit_account,
    #             }),
    #         ],
    #     }
    #     print('move_data ', move_data)
    #     move_id = self.env['account.move'].create(move_data)
    #     move_id.action_post()
    #     print('moooooooooooove_id ', move_id)

