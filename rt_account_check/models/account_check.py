##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountCheck(models.Model):
    _name = 'account.check'
    _description = 'Account Check'
    _order = "id desc"
    _inherit = ['mail.thread']

    name = fields.Char(
        required=True,
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]},
        index=True,
    )
    number = fields.Float(
        required=True,
        size=25, digits=(25, 0),
        readonly=True,
        states={'draft': [('readonly', False)]},
        # copy=False,
        # index=True,
    )

    checkbook_id = fields.Many2one(
        'account.checkbook',
        'Checkbook',
        readonly=True,
        copy=True,
        states={'draft': [('readonly', False)]},
        auto_join=True,
        index=True, tracking=True
    )
    issue_check_subtype = fields.Selection(
        related='checkbook_id.issue_check_subtype',
        readonly=True, tracking=True
    )
    type = fields.Selection(
        [('issue_check', 'Issue Check'), ('third_check', 'Third Check')],
        readonly=True,
        string='Check Type',
        index=True,
        tracking=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        'Partner', tracking=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        # index=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('holding', 'Holding'),
        ('deposited', 'Collected'),
        # ('selled', 'Selled'),
        ('delivered', 'Replaced'),
        ('cashed', 'Cashed'),
        ('transfered', 'Under Collection'),
        ('reclaimed', 'Reclaimed'),
        ('withdrawed', 'Withdrawed'),
        ('handed', 'Handed'),
        ('rejected', 'Rejected'),
        ('credited', 'Credited'),
        ('returned', 'Returned'),
        ('changed', 'Changed'),
        ('cancel', 'Cancel'),
    ],
        required=True,
        default='draft',
        copy=False,
        # compute='_compute_state',
        # readonly=True,
        index=True, tracking=True
    )
    issue_date = fields.Date(
        'Issue Date',
        required=True, tracking=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        # default=fields.Date.context_today,
    )
    owner_vat = fields.Char(
        'Owner Vat',
        readonly=True,
        tracking=True,
        states={'draft': [('readonly', False)]},
    )
    owner_name = fields.Char(
        'Owner Name',
        readonly=True,
        tracking=True,
        states={'draft': [('readonly', False)]},
    )
    bank_id = fields.Many2one(
        'res.bank', 'Bank',
        readonly=True, tracking=True,
        states={'draft': [('readonly', False)]}
    )

    amount = fields.Monetary(
        currency_field='company_currency_id',
        readonly=True, tracking=True,
        states={'draft': [('readonly', False)]}
    )
    amount_currency = fields.Monetary(
        currency_field='currency_id',
        readonly=True,
        states={'draft': [('readonly', False)]}, tracking=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        readonly=True,
        states={'draft': [('readonly', False)]}, tracking=True
    )
    payment_date = fields.Date(
        readonly=True,
        states={'draft': [('readonly', False)]}, tracking=True,
        index=True,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=True,
        domain=[('type', 'in', ['cash', 'bank'])],
        readonly=True,
        states={'draft': [('readonly', False)]},
        index=True, tracking=True
    )
    company_id = fields.Many2one(
        related='journal_id.company_id',
        readonly=True,
        store=True, tracking=True
    )
    company_currency_id = fields.Many2one(
        related='company_id.currency_id',
        readonly=True, tracking=True
    )
    move_ids = fields.Many2many('account.move', 'Entries', compute='count_move_ids')
    count_entries = fields.Integer('Entries', compute='count_move_ids')
    invoice_ids = fields.Many2many('account.move', 'Entries', compute='count_entries_ids')
    count_invoice = fields.Integer('Entries', compute='count_entries_ids')
    payment_id = fields.Many2one('account.payment', 'Payment',  ondelete='cascade')

    def convert_amount_currency_to_company_currency(self, amount_currency):
        company = self.company_id
        balance = self.currency_id._convert(amount_currency, company.currency_id, company, self.payment_date)
        return balance

    def count_move_ids(self):
        for check in self:
            check.move_ids = self.env['account.move'].search(
                [('rejected_check_id', '=', check.id), ('move_type', '=', 'entry')])
            check.count_entries = len(check.move_ids)

    def count_entries_ids(self):
        for check in self:
            check.invoice_ids = self.env['account.move'].search(
                [('rejected_check_id', '=', check.id), ('move_type', 'in', ('out_invoice', 'out_refund'))])
            check.count_invoice = len(check.invoice_ids)

    def action_open_invoice(self):
        move_pool = self.env['account.move']
        return self.action_open_account_invoice(move_pool)

    def action_open_account_invoice(self, move):
        views = [(False, 'tree')]
        if len(self.invoice_ids) == 0:
            views = [(False, 'form')]
        if len(self.invoice_ids) >= 1:
            views = [(False, 'tree'), (False, 'form')]
        for check in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form,tree',
                'view_type': 'form',
                'res_id': move.id,
                'views': views,
                'target': 'current',
                'domain': [('move_type', 'in', ('out_invoice', 'out_refund')), ('rejected_check_id', '=', check.id)],
                'context': {
                    'search_default_rejected_check_id': check.id
                }
            }

    def action_open_entries(self):
        move_pool = self.env['account.move']
        return self.action_open_account_entries(move_pool)

    def action_open_account_entries(self, move):
        views = [(False, 'tree')]
        if len(self.move_ids) == 0:
            views = [(False, 'form')]
        if len(self.move_ids) >= 1:
            views = [(False, 'tree'), (False, 'form')]
        for check in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form,tree',
                'view_type': 'form',
                'res_id': move.id,
                'views': views,
                'target': 'current',
                'domain': [('move_type', '=', 'entry'), ('rejected_check_id', '=', check.id)],
                'context': {
                    'search_default_rejected_check_id': check.id
                }
            }

    @api.constrains('issue_date', 'payment_date')
    @api.onchange('issue_date', 'payment_date')
    def onchange_date(self):
        for rec in self:
            if (
                    rec.issue_date and rec.payment_date and
                    rec.issue_date > rec.payment_date):
                raise UserError(
                    _('Check Payment Date must be greater than Issue Date'))

    @api.constrains('type', 'number', )
    def issue_number_interval(self):
        for rec in self:
            # if not range, then we dont check it
            if rec.type == 'issue_check' and rec.checkbook_id.range_to:
                if rec.number > rec.checkbook_id.range_to:
                    raise UserError(_(
                        "Check number (%s) can't be greater than %s on "
                        "checkbook %s (%s)") % (
                                        rec.number,
                                        rec.checkbook_id.range_to,
                                        rec.checkbook_id.name,
                                        rec.checkbook_id.id,
                                    ))
                elif rec.number == rec.checkbook_id.range_to:
                    rec.checkbook_id.state = 'used'
        return False

    @api.constrains('type', 'owner_name', 'bank_id', )
    def _check_unique(self):
        for rec in self:
            if rec.type == 'issue_check':
                same_checks = self.search([
                    ('checkbook_id', '=', rec.checkbook_id.id),
                    ('type', '=', rec.type),
                    ('number', '=', rec.number),
                ])
                same_checks -= self
                if same_checks:
                    raise ValidationError(_(
                        'Check Number (%s) must be unique per Checkbook!\n'
                        '* Check ids: %s') % (
                                              rec.name, same_checks.ids))

            # elif self.type == 'third_check':
            #     # agregamos condicion de company ya que un cheque de terceros
            #     # se puede pasar entre distintas cias
            #     same_checks = self.search([
            #         ('company_id', '=', rec.company_id.id),
            #         ('bank_id', '=', rec.bank_id.id),
            #         ('owner_name', '=', rec.owner_name),
            #         ('type', '=', rec.type),
            #         ('number', '=', rec.number),
            #     ])
            #     same_checks -= self
            #     if same_checks:
            #         raise ValidationError(_(
            #             'Check Number (%s) must be unique per Owner and Bank!'
            #             '\n* Check ids: %s') % (
            #                                   rec.name, same_checks.ids))
        return True

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel'):
                raise ValidationError(_(
                    'The Check must be in draft state for unlink !'))
        return super(AccountCheck, self).unlink()

    # checks operations from checks
    def bank_debit(self):
        self.ensure_one()
        action_date = self._context.get('action_date', fields.Date.today())
        print('action_data =========== ',action_date)
        debit_account = False
        if self.state == 'handed':
            # if self.issue_date < self.payment_date:
            #     raise Warning(_('You can\'t change check status to credited before due date (%s)' % self.payment_date))
            ref = 'Credited Check nbr %s - %s ' % (self.name, self.journal_id.name)
            journal = self.journal_id and self.journal_id.id
            if self.payment_id:
                debit_account = self.env['account.payment.method.line'].sudo().search(
                    [('id', '=', self.payment_id.payment_method_line_id.id)], limit=1).payment_account_id.id
            else:
                for account in self.journal_id.outbound_payment_method_line_ids:
                    if account.payment_method_id.name == 'Issue Check':
                        debit_account = account.payment_account_id.id

            # debit_account = self.journal_id.payment_credit_account_id and self.journal_id.payment_credit_account_id.id
            credit_account = self.journal_id.default_account_id and self.journal_id.default_account_id.id
            partner_id = self.partner_id and self.partner_id.id or False
            amount = self.amount
            amount_currency = self.amount
            if self.currency_id.id != self.company_id.currency_id.id:
                amount = self.convert_amount_currency_to_company_currency(self.amount)
            move_data = {
                'journal_id': journal,
                'ref': ref,
                'date': action_date,
                'move_type': 'entry',
                'rejected_check_id': self.id,
                'line_ids': [
                    (0, 0, {
                        'name': ref,
                        'partner_id': partner_id,
                        'debit': amount,
                        'currency_id': self.currency_id.id,
                        'amount_currency': round(amount_currency, 2),
                        'credit': 0.0,
                        'account_id': debit_account,

                    }),
                    (0, 0, {
                        'name': ref,
                        'partner_id': partner_id,
                        'debit': 0.0,
                        'currency_id': self.currency_id.id,
                        'amount_currency': round(-1 * amount_currency, 2),
                        'credit': amount,
                        'account_id': credit_account,

                    }),
                ],
            }

            print('checks_move_dataaaa ======== ', move_data)
            move_id = self.env['account.move'].create(move_data)
            move_id.action_post()
            print('moooooooooooove_id ', move_id)
            self.write({'state': 'credited'})

    @api.model
    def post_payment_check(self, payment):
        """ No usamos post() porque no puede obtener secuencia, hacemos
        parecido a los statements donde odoo ya lo genera posteado
        """
        # payment.post()
        for payment_data in payment._prepare_move_line_default_vals():
            print('payment_data =========== ', payment_data)
            move = self.env['account.move'].create(payment_data)
        payment.write({'state': 'posted', 'move_name': move.name})

    def claim(self):
        self.ensure_one()
        if self.state in ['rejected'] and self.type == 'third_check':
            # anulamos la operación en la que lo recibimos
            return self.action_create_debit_note(
                'reclaimed', 'customer', self.partner_id,
                self.company_id._get_check_account('rejected'))

    def get_payment_values(self, journal):
        """ return dictionary with the values to create the reject check
        payment record.
        We create an outbound payment instead of a transfer because:
        1. It is easier to inherit
        2. Outbound payment withot partner type and partner is not seen by user
        and we don't want to confuse them with this payments
        """
        action_date = self._context.get('action_date', fields.Date.today())
        self.ensure_one()

        return {
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'journal_id': journal.id,
            'date': action_date,
            'payment_type': 'outbound',
            'payment_method_id': journal._default_outbound_payment_methods()[0].id,
        }

    def reject(self):
        self.ensure_one()
        if self.state == 'handed':
            debit = False
            ref = 'Rejected Issue Check nbr %s - %s ' % (self.name, self.journal_id.name)
            journal = self.journal_id and self.journal_id.id
            for res in self.journal_id.outbound_payment_method_line_ids:
                if res.payment_method_id.name == 'Issue Check':
                    print('===============debit=============', res.payment_method_id.name)
                    debit = res.payment_account_id.id
                    print('===============debit=============', debit)
            debit_account = debit
            print('===============debit_account=============', debit_account)
            credit_account = self.company_id.rejected_check_account_id.id and self.company_id.rejected_check_account_id.id
            partner_id = self.partner_id and self.partner_id.id or False
            self.write({'state': 'rejected'})
            amount = self.amount
            amount_currency = self.amount
            if self.currency_id.id != self.company_id.currency_id.id:
                amount = self.convert_amount_currency_to_company_currency(self.amount)
            move_data = {
                'journal_id': journal,
                'ref': ref,
                'date': fields.Date.context_today(self),
                'move_type': 'entry',
                'rejected_check_id': self.id,
                'line_ids': [
                    (0, 0, {
                        'name': ref,
                        'partner_id': partner_id,
                        'debit': amount,
                        'credit': 0.0,
                        'account_id': debit_account,
                        'currency_id': self.currency_id.id,
                        'amount_currency': round(amount_currency, 2),

                    }),
                    (0, 0, {
                        'name': ref,
                        'partner_id': partner_id,
                        'debit': 0.0,
                        'credit': amount,
                        'account_id': credit_account,
                        'currency_id': self.currency_id.id,
                        'amount_currency': round(-1 * amount_currency, 2),
                    }),
                ],
            }
            move_id = self.env['account.move'].create(move_data)
            move_id.action_post()

    def customer_return(self):
        company_id = self.env.user.company_id
        ref = ''
        debit_account = False
        credit_account = False
        if self.state == 'holding':
            ref = 'Returned Check nbr %s - %s ' % (self.name, self.journal_id.name)
            debit_account = self.partner_id.property_account_receivable_id and self.partner_id.property_account_receivable_id.id or False
            for res in self.journal_id.inbound_payment_method_line_ids:
                if res.payment_method_id.name == 'Received Third Check':
                    credit_account = res.payment_account_id.id
                # print('=================debit================', credit_account)
            # self.write({'state': 'returned'})

        if self.state == 'transfered':
            ref = 'Returned Check nbr %s - %s ' % (self.name, self.journal_id.name)
            debit_account = self.partner_id.property_account_receivable_id and self.partner_id.property_account_receivable_id.id or False
            for res in self.journal_id.inbound_payment_method_line_ids:
                if res.payment_method_id.name == 'Received Third Check':
                    credit_account = res.payment_account_id.id
                print('=================debit================', credit_account)
            # self.write({'state': 'returned'})
            # credit_account = self.journal_id.payment_debit_account_id and self.journal_id.payment_debit_account_id.id
        if self.state == 'rejected':
            credit_account = company_id._get_check_account('rejected').id
            ref = 'Returned Check nbr %s - %s ' % (self.name, self.journal_id.name)
            # ref = 'Rejected Issue Check nbr %s - %s ' % (self.name, self.journal_id.name)
            debit_account = self.partner_id.property_account_receivable_id and self.partner_id.property_account_receivable_id.id
        if self.state in ('transfered', 'rejected','holding'):
            self.create_returned_entry(ref, debit_account, credit_account)
        self.write({'state': 'returned'})

    def create_returned_entry(self, ref, debit_account, credit_account):
        action_date = self._context.get('action_date', fields.Date.today())
        amount = self.amount
        amount_currency = self.amount
        if self.currency_id.id != self.company_id.currency_id.id:
            amount = self.convert_amount_currency_to_company_currency(self.amount)
        move_data = {
            'journal_id': self.journal_id and self.journal_id.id or False,
            'ref': ref,
            'date': action_date,
            'move_type': 'entry',
            'rejected_check_id': self.id,
            'line_ids': [
                (0, 0, {
                    'name': ref,
                    'partner_id': self.partner_id and self.partner_id.id or False,
                    'debit': amount,
                    'credit': 0.0,
                    'account_id': debit_account,
                    'currency_id': self.currency_id.id,
                    'amount_currency': round(amount_currency, 2),
                }),
                (0, 0, {
                    'name': ref,
                    'partner_id': self.partner_id and self.partner_id.id or False,
                    'debit': 0.0,
                    'credit': amount,
                    'account_id': credit_account,
                    'currency_id': self.currency_id.id,
                    'amount_currency': round(-1 * amount_currency, 2),
                }),
            ],
        }
        move_id = self.env['account.move'].create(move_data)
        move_id.action_post()
