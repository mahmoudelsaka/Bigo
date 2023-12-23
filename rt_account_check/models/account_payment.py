##############################################################################
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import logging

from odoo.exceptions import UserError

from odoo import fields, models, _, api

# import odoo.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    check_ids = fields.Many2many(
        'account.check',
        string='Checks',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
        auto_join=True,
    )
    # only for v8 comatibility where more than one check could be received
    # or issued
    check_ids_copy = fields.Many2many(
        related='check_ids',
        readonly=True,
    )
    readonly_currency_id = fields.Many2one(
        related='currency_id',
        readonly=True,
    )
    readonly_amount = fields.Monetary(
        related='amount',
        readonly=True,
    )
    # we add this field for better usability on issue checks and received
    # checks. We keep m2m field for backward compatibility where we allow to
    # use more than one check per payment
    check_id = fields.Many2one(
        'account.check',
        compute='_compute_check',
        string='Check',
    )

    @api.depends('check_ids')
    def _compute_check(self):
        for rec in self:
            # we only show checks for issue checks or received thid checks
            # if len of checks is 1
            if rec.payment_method_code in (
                    'received_third_check',
                    'issue_check',) and len(rec.check_ids) == 1:
                rec.check_id = rec.check_ids[0].id
            else:
                rec.check_id = False

    # check fields, just to make it easy to load checks without need to create
    # them by a m2o record
    check_name = fields.Char(
        'Check Name',
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]},
    )
    check_number1 = fields.Float(
        'Check Number',
        readonly=True,
        states={'draft': [('readonly', False)]},
        size=25, digits=(25, 0)
    )
    check_issue_date = fields.Date(
        'Check Issue Date',
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]},
        default=fields.Date.context_today,
    )
    check_payment_date = fields.Date(
        'Check Payment Date',
        readonly=True,
        help="Only if this check is post dated",
        states={'draft': [('readonly', False)]},
    )
    checkbook_id = fields.Many2one(
        'account.checkbook',
        'Checkbook',
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]},
        auto_join=True,
    )
    check_subtype = fields.Selection(
        related='checkbook_id.issue_check_subtype',
        readonly=True,
    )
    check_bank_id = fields.Many2one(
        'res.bank',
        'Check Bank',
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]},
        auto_join=True,
    )
    check_owner_vat = fields.Char(
        'Check Owner Vat',
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]}
    )
    check_owner_name = fields.Char(
        'Check Owner Name',
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]}
    )
    # this fields is to help with code and view
    check_type = fields.Char(
        compute='_compute_check_type',
    )
    checkbook_numerate_on_printing = fields.Boolean(
        related='checkbook_id.numerate_on_printing',
        readonly=True,
    )
    def action_draft(self):
        res = super(AccountPayment,self).action_draft()
        if self.check_ids:
            for rec in self.check_ids:
                if rec.state == 'holding':
                    rec.write({'state':'draft'})
                rec.unlink()
        return res 
    @api.depends('payment_method_code')
    def _compute_check_type(self):
        for rec in self:
            if rec.payment_method_code == 'issue_check':
                rec.check_type = 'issue_check'
            elif rec.payment_method_code in [
                'received_third_check',
                'delivered_third_check']:
                rec.check_type = 'third_check'
            else:
                rec.check_type = False

    def _compute_payment_method_description(self):
        check_payments = self.filtered(
            lambda x: x.payment_method_code in
                      ['issue_check', 'received_third_check', 'delivered_third_check'])
        for rec in check_payments:
            if rec.check_ids:
                checks_desc = ', '.join(rec.check_ids.mapped('name'))
            else:
                checks_desc = rec.check_name
            name = "%s: %s" % (rec.payment_method_id.display_name, checks_desc)
            rec.payment_method_description = name

            _logger.info('testttttttttttttttttttt====%s' % name)
        return super(AccountPayment, (self - check_payments))._compute_payment_method_description()

    # on change methods

    # @api.constrains('check_ids')
    @api.onchange('check_ids', 'payment_method_code')
    def onchange_checks(self):
        # we only overwrite if payment method is delivered
        if self.payment_method_code == 'delivered_third_check':
            self.amount = sum(self.check_ids.mapped('amount'))

    @api.onchange('check_number1')
    def change_check_number(self):
        # TODO make default padding a parameter
        def _get_name_from_number(number):
            padding = 8
            if len(str(number)) > padding:
                padding = len(str(number))
            return ('%%0%sd' % padding % number)

        for rec in self:
            if rec.payment_method_code in ['received_third_check']:
                if not rec.check_number1:
                    check_name = False
                else:
                    check_name = _get_name_from_number(rec.check_number1)
                rec.check_name = check_name
            elif rec.payment_method_code in ['issue_check']:
                sequence = rec.checkbook_id.sequence_id
                if not rec.check_number1:
                    check_name = False
                elif sequence:
                    if rec.check_number1 != sequence.number_next_actual:
                        # write with sudo for access rights over sequence
                        sequence.sudo().write(
                            {'number_next_actual': rec.check_number1})
                    check_name = rec.checkbook_id.sequence_id.next_by_id()
                else:
                    # in sipreco, for eg, no sequence on checkbooks
                    check_name = _get_name_from_number(rec.check_number1)
                rec.check_name = check_name

    @api.onchange('check_issue_date', 'check_payment_date')
    def onchange_date(self):
        if (
                self.check_issue_date and self.check_payment_date and
                self.check_issue_date > self.check_payment_date):
            self.check_payment_date = False
            raise UserError(
                _('Check Payment Date must be greater than Issue Date'))

    @api.onchange('check_owner_vat')
    def onchange_check_owner_vat(self):
        """
        We suggest owner name from owner vat
        """
        # if not self.check_owner_name:
        self.check_owner_name = self.search(
            [('check_owner_vat', '=', self.check_owner_vat)],
            limit=1).check_owner_name

    @api.onchange('partner_id', 'payment_method_code')
    def onchange_partner_check(self):
        commercial_partner = self.partner_id.commercial_partner_id
        if self.payment_method_code == 'received_third_check':
            self.check_bank_id = (
                    commercial_partner.bank_ids and
                    commercial_partner.bank_ids[0].bank_id or False)
            # en realidad se termina pisando con onchange_check_owner_vat
            # entonces llevamos nombre solo si ya existe la priemr vez
            # TODO ver si lo mejoramos o borramos esto directamente
            # self.check_owner_name = commercial_partner.name
            vat_field = 'vat'
            # to avoid needed of another module, we add this check to see
            # if l10n_ar cuit field is available
            if 'cuit' in commercial_partner._fields:
                vat_field = 'cuit'
            self.check_owner_vat = commercial_partner[vat_field]
        elif self.payment_method_code == 'issue_check':
            self.check_bank_id = self.journal_id.bank_id
            self.check_owner_name = False
            self.check_owner_vat = False
        # no hace falta else porque no se usa en otros casos

    @api.onchange('payment_method_code')
    def _onchange_payment_method_code(self):
        if self.payment_method_code == 'issue_check':
            checkbook = self.env['account.checkbook'].search([
                ('state', '=', 'active'),
                ('journal_id', '=', self.journal_id.id)],
                limit=1)
            self.checkbook_id = checkbook
        elif self.checkbook_id:
            # TODO ver si interesa implementar volver atras numeracion
            self.checkbook_id = False

    @api.onchange('checkbook_id')
    def onchange_checkbook(self):
        if self.checkbook_id and not self.checkbook_id.numerate_on_printing:
            self.check_number1 = self.checkbook_id.next_number
        else:
            self.check_number1 = False

    # post methods

    def check_vals(self):
        self.ensure_one()

        check_vals = {
            'bank_id': self.check_bank_id.id or False,
            'owner_name': self.check_owner_name,
            'owner_vat': self.check_owner_vat,
            'number': self.check_number1,
            'name': self.check_name or 'New',
            'checkbook_id': self.checkbook_id.id,
            'issue_date': self.check_issue_date,
            'type': self.check_type,

            'partner_id': self.partner_id.id,
            'journal_id': self.journal_id.id,
            'amount': self.amount,
            'state': 'holding',
            'payment_date': self.check_payment_date,
            # TODO arreglar que monto va de amount y cual de amount currency
            # 'amount_currency': self.amount,
            'currency_id': self.currency_id.id,
            'payment_id': self.id,
        }
        return check_vals

    def create_check(self):
        check = False
        for rec in self:
            check_vals = rec.check_vals()
            if rec.payment_method_code in ('issue_check', 'received_third_check', 'delivered_third_check'):
                check = self.env['account.check'].create(check_vals)
                if check.type == 'issue_check':
                    check.write({'state': 'handed'})
                else:
                    check.write({'state': 'holding'})
                self.check_ids = [(4, check.id, False)]
        return check

    def action_post(self):
        for pay in self:
            sequence = pay.move_id._set_next_sequence()
            print('sequence ===== ', sequence)
            pay.move_id.write({'name': sequence})
        for rec in self.filtered(
                lambda x: x.payment_method_code == 'issue_check'):
            if not rec.check_number1 or not rec.check_name:
                raise UserError(_(
                    'Para mandar a proceso de firma debe definir numero '
                    'de cheque en cada linea de pago.\n'
                    '* ID del pago: %s') % rec.id)
        self.create_check()
        return super(AccountPayment, self).action_post()

    # def _prepare_move_line_default_vals(self, write_off_line_vals=None):
    #     ''' Prepare the dictionary to create the default account.move.lines for the current payment.
    #     :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
    #         * amount:       The amount to be added to the counterpart amount.
    #         * name:         The label to set on the line.
    #         * account_id:   The account on which create the write-off.
    #     :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
    #     '''
    #     res = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals)
    #     new_check_id = self.create_check()
    #     _logger.info(f'new_check_id =========== {new_check_id}')
    #     return res

    def do_print_checks(self):
        # si cambiamos nombre de check_report tener en cuenta en sipreco
        checkbook = self.mapped('checkbook_id')
        # si todos los cheques son de la misma chequera entonces buscamos
        # reporte especifico para esa chequera
        report_name = len(checkbook) == 1 and \
                      checkbook.report_template.report_name \
                      or 'check_report'
        check_report = self.env['ir.actions.report'].search(
            [('report_name', '=', report_name)], limit=1).report_action(self)

        return check_report

    def print_checks(self):
        if len(self.mapped('checkbook_id')) != 1:
            raise UserError(_(
                "In order to print multiple checks at once, they must belong "
                "to the same checkbook."))
        # por ahora preferimos no postearlos
        # self.filtered(lambda r: r.state == 'draft').post()

        # si numerar al imprimir entonces llamamos al wizard
        if self[0].checkbook_id.numerate_on_printing:
            if all([not x.check_name for x in self]):
                next_check_number = self[0].checkbook_id.next_number
                return {
                    'name': _('Print Pre-numbered Checks'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'print.prenumbered.checks',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'payment_ids': self.ids,
                        'default_next_check_number': next_check_number,
                    }
                }
            # si ya estan enumerados mandamos a imprimir directamente
            elif all([x.check_name for x in self]):
                return self.do_print_checks()
            else:
                raise UserError(_(
                    'Esta queriendo imprimir y enumerar cheques que ya han '
                    'sido numerados. Seleccione solo cheques numerados o solo'
                    ' cheques sin numero.'))
        else:
            return self.do_print_checks()

    def _get_counterpart_move_line_vals(self, invoice=False):
        vals = super(AccountPayment, self)._get_counterpart_move_line_vals(
            invoice=invoice)
        force_account_id = self._context.get('force_account_id')
        if force_account_id:
            vals['account_id'] = force_account_id.id
        return vals
