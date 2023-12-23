from odoo import api, fields, models, _
from odoo.exceptions import Warning
import time

STATE = [('draft', 'Draft'),
         ('first_approved', 'Send'),
         ('second_approved', 'To Approve'),
         ('approved', 'Approved'),
         ('done', 'Done'),
         ('cancel', 'Cancel')]

TYPE = [('receipt', 'Receipt'),
        ('payment', 'Payment')]


class receipt_order(models.Model):
    _name = 'receipt.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_user_company(self):
        user = self.env.user
        return user.company_id.id

    def _default_currency_id(self):
        user = self.env.user
        return user.company_id.currency_id.id

    name = fields.Char('Number', default="/", readonly=True, copy=False)
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True,
                                 tracking=True,
                                 states={'draft': [('readonly', False)], 'approved': [('readonly', True)]})
    # period_id = fields.Many2one('account.period', 'Period',
    # 		states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', 'Journal', domain=[('type', 'in', ['cash', 'bank'])],
                                 states={'draft': [('readonly', False)],
                                         'second_approved': [('required', True)], 'approved': [('readonly', True)]}
                                 )
    created_by = fields.Many2one('res.users', 'Created By', default=lambda self: self.env.user.id,
                                 tracking=True)
    state = fields.Selection(STATE, string="State", default=lambda *a: 'draft',
                             tracking=True, copy=False,
                             states={'draft': [('readonly', False)]})

    statement_id = fields.Many2one('account.bank.statement', 'Treasury', tracking=True)
    statement_line_id = fields.Many2one('account.bank.statement.line', 'Treasury', tracking=True)

    memo = fields.Char('Memo', required=True, copy=True, tracking=True,
                       states={'draft': [('readonly', False)], 'first_approved': [('readonly', True)],
                               'approved': [('readonly', True)]})

    amount = fields.Float('Amount', required=True, tracking=True,
                          states={'draft': [('readonly', False)], 'first_approved': [('readonly', True)],
                                  'approved': [('readonly', True)]})

    ref = fields.Char('Ref#', copy=False,
                      states={'draft': [('readonly', False)], 'approved': [('readonly', True)]})

    due_date = fields.Date('Due Date', required=True,
                           default=lambda *a: time.strftime('%Y-%m-%d'),
                           states={'draft': [('readonly', False)], 'approved': [('readonly', True)]})

    type = fields.Selection(TYPE, string='Type', required=True,
                            states={'draft': [('readonly', False)], 'first_approved': [('readonly', True)],
                                    'approved': [('readonly', True)]})

    currency_id = fields.Many2one('res.currency', 'Currency', default=_default_currency_id,
                                  tracking=True,
                                  states={'draft': [('readonly', False)], 'approved': [('readonly', True)]})

    company_id = fields.Many2one('res.company', 'Company', tracking=True,
                                 default=_default_user_company,
                                 states={'draft': [('readonly', False)], 'approved': [('readonly', True)]})

    note = fields.Text('Internal Note')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', ondelete='set null')
    account_id = fields.Many2one('account.account', 'Account', ondelete='set null')
    count_transactions = fields.Integer('Transactions', compute='calc_transaction_ids')

    def calc_transaction_ids(self):
        for rec in self:
            statement_ids = self.env['account.bank.statement'].search([('id', '=', rec.statement_id.id),
                                                                       ('journal_id', '=', rec.journal_id.id),
                                                                       ('po_ro_id', '=', rec.id)])
            rec.count_transactions = len(statement_ids)

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            if vals.get('type') == 'receipt':
                vals['name'] = self.env['ir.sequence'].next_by_code('receipt.order') or '/'
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('payment.order') or '/'
        new_id = super(receipt_order, self).create(vals)
        return new_id

    @api.onchange('statement_id')
    def onchange_statement_id(self):
        bank_statement_pool = self.env["account.bank.statement"]
        default_currency_id = self._default_currency_id()
        default_company_id = self._default_user_company()
        if self.statement_id:
            if self.statement_id.state != 'open':
                raise Warning(_("Cash Register is not Open."))
            if self.statement_id.company_id.id != self.company_id.id:
                raise Warning(_("Cash Register Company does not match with Order."))
            if self.statement_id.company_id.currency_id.id != self.company_id.currency_id.id:
                raise Warning(_("Cash Register Company does not match with Order."))

    def action_view_transaction(self):
        statement_id = self.env['account.bank.statement']
        # views = [(False, 'tree')]
        views = [(False, 'tree'), (False, 'form')]
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.bank.statement',
                'view_mode': 'form,tree',
                'view_type': 'form',
                'res_id': statement_id.id,
                'views': views,
                'target': 'current',
                'domain': [('id', '=', rec.statement_id.id),
                           ('journal_id', '=', rec.journal_id.id),
                           ('po_ro_id', '=', rec.id)],
            }

    def action_first_approved(self):
        self.state = 'first_approved'

    def action_second_approved(self):
        self.state = 'second_approved'

    def get_statement_data(self, statement_id):
         partner = self.partner_id and self.partner_id.id or False
         bsl_data = {'date': self.due_date,
                    'payment_ref': self.memo,
                    'ref': self.ref,
                    'partner_id': partner,
                     'journal_id': self.journal_id and self.journal_id.id or False,
                    'statement_id': statement_id.id,
                    'narration': self.account_id and self.account_id.code or False,
                    }
         return bsl_data

    def create_statement(self):
        bank_statement_pool = self.env['account.bank.statement.line']

        if self.amount < 0.01:
            raise Warning(_("Amount Should not be 0(Zero)."))


        statement_id = self.env['account.bank.statement'].create({
            'name': self.name,
            'journal_id': self.journal_id.id,
            'date': self.due_date,
            'po_ro_id': self.id,
        })

        self.write({'statement_id': statement_id.id})
        bsl_data = self.get_statement_data(statement_id)
        if self.type == 'receipt':
            bsl_data.update({'amount': self.amount})
        else:
            bsl_data.update({'amount': -self.amount})
        statement_line_id = bank_statement_pool.create(bsl_data)
        self.write({'statement_line_id': statement_line_id.id})
        # statement_id.line_ids.create(bsl_data)
        return statement_line_id

    def action_done(self):
        statement = self.create_statement()
        view_id = self.env.ref('account_accountant.view_bank_statement_line_tree_bank_rec_widget')

        values = {
            'name': _('Open Treasury'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.bank.statement.line',
            'res_id': statement.id,
            'view_id': view_id.id,
            'views': [(False, 'tree'),(False, 'kanban')],
            'target': 'current',
            'domain': [('id', '=', statement.id)]
            # 'context': {
            #     'default_done_qty': done_qty,
            #     'default_quality_check_id': self.id,
            # }
        }
        self.write({'state': 'done'})
        return values

    def action_approved(self):
        self.state = 'approved'

    def action_cancel(self):
        self.state = 'cancel'

    def action_reset(self):
        self.state = 'draft'


# class account_bank_statement_line(models.Model):
#     _inherit = 'account.bank.statement.line'
#
#     analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', ondelete='set null')
#     account_id = fields.Many2one('account.account', 'Account', ondelete='set null')
#     analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

    # def action_print_voucher(self):
    #     """ Print Receipt/Payment Vouchers """
    #     assert len(self) == 1, 'This option should only be used for a single id at a time.'
    #     return self.env.ref('elsaka_payment_order.receipt_payment_voucher').report_action(self)


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    po_ro_id = fields.Many2one('receipt.order', 'Receipt/Payment Order')

    # def action_bank_reconcile_bank_statements(self):
    #     res = super(AccountBankStatement, self).action_bank_reconcile_bank_statements()
    #     self.write({'state': 'confirm'})
    #     return res
