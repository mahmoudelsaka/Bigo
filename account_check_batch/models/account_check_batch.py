import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class AccountCheckBatch(models.Model):
    _name = 'account.check.batch'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', 'Customer', required=1, tracking=True)
    journal_id = fields.Many2one('account.journal', 'Journal', required=1, tracking=True, domain=[('type', '=', 'bank')])
    account_id = fields.Many2one('account.account', 'Account', required=1, tracking=True,
                                 domain=[('account_type', 'in', ['asset_receivable', 'liability_payable', 'asset_current', 'liability_current'])])
    duration = fields.Integer('Duration', tracking=True)
    amount = fields.Float('Installment Amount', required=1, tracking=True)
    down_payment_amount = fields.Float('DownPayment', default=0, tracking=True)
    start = fields.Integer('1st Number', tracking=True)
    count_check = fields.Integer('Number of Checks', tracking=True)
    bank_id = fields.Many2one('res.bank', 'Bank', readonly=False, tracking=True)

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id.id, tracking=True)
    owner_vat = fields.Char('Owner Vat', tracking=True)
    owner_name = fields.Char('Owner Name', tracking=True)
    is_created = fields.Boolean('Is Created')
    state = fields.Selection(selection=[('draft', 'Draft'), ('progress', 'In Progress'), ('confirm', 'Confirm')],
                             default='draft', tracking=True)
    check_batch_line = fields.One2many('account.check.batch.line', 'check_batch_id', 'Checks')
    payment_ids = fields.Many2many('account.payment', 'Payment', compute='count_payment_ids')
    count_payment = fields.Integer('Payments', compute='count_payment_ids')
    issue_date = fields.Date('Issue Date', required=1, default=fields.Date.context_today, tracking=True)
    start_date = fields.Date('Check Start Date', required=1, tracking=True)
    payment_type = fields.Selection(selection=[('unit', 'Unit'), ('main', 'Commuinty'), ('dp', 'Down Payment'),
                                               ('utilities-electricity', 'Utilities(Electricity)'),
                                               ('utilities-water', 'Utilities(Water)'),
                                               ('utilities-stp', 'Utilities(STP)'),
                                               ('utilities-telecom', 'Utilities(Telecom)'),
                                               ('community', 'Community Deposit'), ('others', 'Others')
                                               ],
                                    string='Type',
                                    default='unit', tracking=True)
    is_printed = fields.Boolean('Batch Is Printed')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        compute='_compute_currency_id', store=True, readonly=False, precompute=True,
        help="The payment's currency.")

    @api.depends('journal_id')
    def _compute_currency_id(self):
        for pay in self:
            pay.currency_id = pay.journal_id.currency_id or pay.journal_id.company_id.currency_id

    # Retrieve Journal in batch lines if changed in parent
    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:
            for line in self.check_batch_line:
                line.journal_id = self.journal_id and self.journal_id.id or False

    # Retrieve Account in batch lines if changed in parent
    @api.onchange('account_id')
    def onchange_account_id(self):
        if self.account_id:
            for line in self.check_batch_line:
                line.account_id = self.account_id and self.account_id.id or False

    # Retrieve Bank in batch lines if changed in parent
    @api.onchange('bank_id')
    def onchange_bank_id(self):
        if self.bank_id:
            for line in self.check_batch_line:
                line.check_bank_id = self.bank_id and self.bank_id.id or False

    # Retrieve Owner Vat in batch lines if changed in parent
    @api.onchange('owner_vat')
    def onchange_owner_vat(self):
        if self.owner_vat:
            for line in self.check_batch_line:
                line.owner_vat = self.owner_vat or False

    # Retrieve Owner Name in batch lines if changed in parent
    @api.onchange('owner_name')
    def onchange_owner_name(self):
        if self.owner_name:
            for line in self.check_batch_line:
                line.owner_name = self.owner_name or False

    # Print Receipt
    def reprint_receipt_order(self):
        self.write({'is_printed': True})
        return self.env.ref('account_check_batch.action_report_check_batch_report').report_action(self)

    # Get Customer Payments
    def count_payment_ids(self):
        for batch in self:
            batch.payment_ids = self.env['account.payment'].search([('check_batch_id', '=', batch.id)])
            batch.count_payment = len(batch.payment_ids)

    # Reset to Draft
    def action_draft(self):
        self.ensure_one()
        if self.payment_ids:
            self.payment_ids.unlink()
        self.state = 'draft'

    def check_total_unit_amount(self):
        total_amount = 0.0
        for line in self.check_batch_line:
            if line.payment_type == 'unit':
                total_amount += line.amount
        # if round(self.amount, 2) != round(total_amount, 2):
        #     raise UserError(_('Total amount for unit must be equal price unit'))

    def action_confirm(self):
        self.check_total_unit_amount()
        self.create_payment_vals()
        # self.create_down_payment_check()
        self.state = 'confirm'

    # def action_generate_check(self):
    #     if self.amount <= 0.0:
    #         raise UserError(_('Unit Price must be greater than Zero!'))
    #     self.create_check_line()
    #     self.write({'state': 'progress'})

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.account_id = self.partner_id.property_account_receivable_id.id or False

    @api.onchange('amount')
    def onchange_price(self):
        if self.amount < 0:
            self.amount = self.amount * -1

    def unlink(self):
        for batch in self:
            if batch.state != 'draft':
                raise UserError(_('You can\'t delete record only in %s status' % batch.state))
        return super(AccountCheckBatch, self).unlink()

    def _prepare_check_val(self, amount):
        vals = {
            'check_issue_date': self.issue_date,
            'check_bank_id': self.bank_id and self.bank_id.id,
            'owner_vat': self.owner_vat,
            'owner_name': self.owner_name,
            'amount': amount,
            'check_batch_id': self.id,
            'account_id': self.account_id and self.account_id.id or False,
            'journal_id': self.journal_id and self.journal_id.id or False,
        }
        return vals
    def create_check_line(self):
        batch_line = self.env['account.check.batch.line']
        for check in self:
            if check.check_batch_line:
                check.check_batch_line.unlink()
            amount = 0.0
            if check.amount and check.count_check:
                amount = check.amount / check.count_check
            date = self.start_date
            start_date = datetime.strptime(str(date), '%Y-%m-%d')
            check_no = self.start
            for i in range(1, check.count_check + 1):
                check_vals = check._prepare_check_val(amount)
                check_vals['check_no'] = check_no
                check_vals['check_name'] = check_no
                check_vals['check_payment_date'] = start_date
                check_vals['payment_type'] = check.payment_type

                check_batch_id = batch_line.create(check_vals)
                _logger.info(f'***** check_batch_id ****** {check_batch_id}')
                check_no += 1
                _logger.info(f'**** check_number ***** check_no')
                start_date = start_date + relativedelta(months=check.duration)
            if check.down_payment_amount:
                check_no = str(self.start_date.year) + str(self.start_date.month) + str(self.start_date.day)

                down_payment_vals = check._prepare_check_val(check.down_payment_amount)
                down_payment_vals['check_no'] = int(check_no)
                down_payment_vals['check_name'] = 'Down Payment/' + self.partner_id.name + '/' + check_no
                down_payment_vals['check_payment_date'] = self.start_date
                down_payment_vals['payment_type'] = 'dp'

                check_down_payment_line = batch_line.create(down_payment_vals)
            check.write({'is_created': True})

    def create_down_payment_check(self, line):
        check_vals = {}
        if line.payment_type == 'dp':
            check_vals = {
                'name': line.check_name,
                'number': line.check_no,
                'type': 'third_check',
                'installment_type': 'dp',
                'journal_id': line.journal_id and line.journal_id.id,
                'partner_id': self.partner_id and self.partner_id.id or False,
                'currency_id': self.env.user.company_id.currency_id and self.env.user.company_id.currency_id.id or False,
                'state': 'deposited',
                'issue_date': line.check_issue_date,
                'payment_date': line.check_payment_date or False,
                'bank_id': line.check_bank_id and line.check_bank_id.id,
                'owner_vat': line.owner_vat,
                'owner_name': line.owner_name,
                'amount_currency': line.amount,
                'amount': line.amount,
                'company_id': self.env.user.company_id and self.env.user.company_id.id or False,
            }
        return check_vals

    def payment_vals(self, line):

        vals = {
        }
        account_payment_method_line = self.env['account.payment.method.line'].search(
            [('journal_id', '=', self.journal_id.id),
             ('payment_method_id.code', '=', 'received_third_check')], limit=1)
        if account_payment_method_line:
            if not account_payment_method_line.payment_account_id:
                raise UserError(
                    _('Outstanding receipt account not define in Journal %s to create payment' % self.journal_id.name))


        if line.payment_type != 'dp':
            # if line.payment_type == 'unit':
            #     unit_type = 'apart'
            vals = {
                'destination_account_id': self.account_id and self.account_id.id,
                'company_id': self.company_id and self.company_id.id,
                'check_bank_id': line.check_bank_id.id or False,
                'check_owner_name': line.owner_name,
                'check_owner_vat': line.owner_vat,
                'check_number1': line.check_no,
                'check_name': line.check_name,
                'check_issue_date': line.check_issue_date,
                'installment_type': line.payment_type,
                'payment_method_line_id': account_payment_method_line.id,
                'check_batch_id': self.id,
                'partner_id': self.partner_id.id,
                'journal_id': line.journal_id and line.journal_id.id,
                'amount': line.amount,
                'state': 'draft',
                'check_payment_date': line.check_payment_date,
                # TODO arreglar que monto va de amount y cual de amount currency
                # 'amount_currency': self.amount,
                'currency_id': self.currency_id.id,

            }
        return vals

    def create_payment_vals(self):
        payment_pool = self.env['account.payment'].sudo()
        for line in self.check_batch_line:
            if line.payment_type != 'dp':
                vals = self.payment_vals(line)

                payment = payment_pool.create(vals)
                _logger.info(f'****** Pyment Vals ****** {payment}')
                payment.action_post()
                line.write({'payment_id': payment.id})
            else:
                check_vals = self.create_down_payment_check(line)
                down_payment_check = self.env['account.check'].sudo().create(check_vals)
                _logger.info(f'down_payment_check-ID ==== {down_payment_check}')

    def action_open_account_payment(self):
        payment = self.env['account.payment']
        views = [(False, 'tree')]
        if len(self.payment_ids) == 0:
            views = [(False, 'form')]
        if len(self.payment_ids) > 0:
            views = [(False, 'tree'), (False, 'form')]
        for batch in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.payment',
                'view_mode': 'form,tree',
                'view_type': 'form',
                'res_id': payment.id,
                'views': views,
                'target': 'current',
                'domain': [('partner_type', '=', 'customer'), ('check_batch_id', '=', batch.id)]
            }


class AccountCheckBatchLine(models.Model):
    _name = 'account.check.batch.line'
    _rec_name = 'check_no'
    _order = 'check_payment_date asc'

    # date = fields.Date('Due Date')
    check_no = fields.Integer('Check No.', required=1)
    check_name = fields.Char('Check Name', required=1)
    check_issue_date = fields.Date('Issue Date', required=1)
    check_payment_date = fields.Date('Payment Date', required=1)
    check_bank_id = fields.Many2one('res.bank', 'Check Bank')
    owner_vat = fields.Char('Owner Vat', )
    owner_name = fields.Char('Owner Name')
    amount = fields.Float('Check Amount', required=1)
    payment_id = fields.Many2one('account.payment', 'Payment', ondelete='cascade', )
    check_batch_id = fields.Many2one('account.check.batch', 'Check Batch')
    payment_type = fields.Selection(selection=[('unit', 'Unit'), ('main', 'Community'), ('dp', 'Down Payment'),
                                               ('utilities-electricity', 'Utilities(Electricity)'),
                                               ('utilities-water', 'Utilities(Water)'),
                                               ('utilities-stp', 'Utilities(STP)'),
                                               ('utilities-telecom', 'Utilities(Telecom)'),
                                               ('community', 'Community Deposit'), ('others', 'Others')
                                               ],
                                    string='Type',
                                    default='unit')
    journal_id = fields.Many2one('account.journal', 'Journal', required=1, domain=[('type', '=', 'bank')])
    account_id = fields.Many2one('account.account', 'Account', required=1,
                                 domain=[('account_type', 'in', ['asset_receivable', 'liability_payable', 'asset_current', 'liability_current'])])
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note'),
    ], default=False, help="Technical field for UX purpose.")

    @api.onchange('check_name')
    def onchange_cheque_name(self):
        if self.check_name:
            if self.check_name.isnumeric():
                self.check_no = self.check_name
            else:
                self.check_no = 0
