from odoo import fields, models, api
# from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"

    name = fields.Char(translate=True)

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['received_third_check'] = {'mode': 'multi', 'domain': [('type', '=', 'bank')]}
        res['delivered_third_check'] = {'mode': 'multi', 'domain': [('type', '=', 'bank')]}
        res['issue_check'] = {'mode': 'multi', 'domain': [('type', '=', 'bank')]}
        return res


class AccountPayment(models.Model):
    # _name = "account.payment"
    _inherit = 'account.payment'

    payment_method_description = fields.Char(
        compute='_compute_payment_method_description',
        string='Payment Method',
    )

    def _compute_payment_method_description(self):
        for rec in self:
            rec.payment_method_description = rec.payment_method_id.display_name

    # nuevo campo funcion para definir dominio de los metodos
    payment_method_ids = fields.Many2many(
        'account.payment.method',
        compute='_compute_payment_methods'
    )
    journal_ids = fields.Many2many(
        'account.journal',
        compute='_compute_journals'
    )
    company_id = fields.Many2one(related='journal_id.company_id')

    def get_journals_domain(self):
        """
        We get domain here so it can be inherited
        """
        self.ensure_one()
        domain = [('type', 'in', ('bank', 'cash'))]
        # if self.payment_type == 'inbound':
        #     domain.append(('at_least_one_inbound', '=', True))
        # # Al final dejamos que para transferencias se pueda elegir
        # # cualquier sin importar si tiene outbound o no
        # # else:
        # elif self.payment_type == 'outbound':
        #     domain.append(('at_least_one_outbound', '=', True))
        return domain

    @api.depends(
        'payment_type',
    )
    def _compute_journals(self):
        for rec in self:
            rec.journal_ids = rec.journal_ids.search(rec.get_journals_domain())

    @api.depends(
        'journal_id.outbound_payment_method_line_ids',
        'journal_id.inbound_payment_method_line_ids',
        'payment_type',
    )
    def _compute_payment_methods(self):
        for rec in self:
            methods = []
            if rec.payment_type in ('outbound', 'transfer'):
                for outpay in rec.journal_id.outbound_payment_method_line_ids:
                    methods.append(outpay.payment_method_id.id)
            else:
                for inpay in rec.journal_id.inbound_payment_method_line_ids:
                    methods.append(inpay.payment_method_id.id)
            rec.payment_method_ids = methods

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        """
        Sobre escribimos y desactivamos la parte del dominio de la funcion
        original ya que se pierde si se vuelve a entrar
        """
        if not self.invoice_line_ids:
            # Set default partner type for the payment type
            if self.payment_type == 'inbound':
                self.partner_type = 'customer'
            elif self.payment_type == 'outbound':
                self.partner_type = 'supplier'
            else:
                self.partner_type = False
            # limpiamos journal ya que podria no estar disponible para la nueva
            # operacion y ademas para que se limpien los payment methods
            self.journal_id = False

    # @api.onchange('partner_type')
    def _onchange_partner_type(self):
        """
        Agregasmos dominio en vista ya que se pierde si se vuelve a entrar
        Anulamos funcion original porque no haria falta
        """
        return True

    def _onchange_amount(self):
        """
        Anulamos este onchange que termina cambiando el domain de journals
        y no es compatible con multicia y se pierde al guardar.
        TODO: ver que odoo con este onchange llama a
        _compute_journal_domain_and_types quien devolveria un journal generico
        cuando el importe sea cero, imagino que para hacer ajustes por
        diferencias de cambio
        """
        return True

    # @api.onchange('journal_id')
    # def _onchange_journal(self):
    #     """
    #     Sobre escribimos y desactivamos la parte del dominio de la funcion
    #     original ya que se pierde si se vuelve a entrar
    #     TODO: ver que odoo con este onchange llama a
    #     _compute_journal_domain_and_types quien devolveria un journal generico
    #     cuando el importe sea cero, imagino que para hacer ajustes por
    #     diferencias de cambio
    #     """
    #     if self.journal_id:
    #         self.currency_id = (
    #                 self.journal_id.currency_id or self.company_id.currency_id)
    #         # Set default payment method
    #         # (we consider the first to be the default one)
    #         payment_methods = []
    #         if self.payment_type == 'inbound':
    #             if self.journal_id.inbound_payment_method_line_ids:
    #                 for inpay in self.journal_id.inbound_payment_method_line_ids:
    #                     payment_methods.append(inpay.payment_method_id.id)
    #             if self.journal_id.outbound_payment_method_line_ids:
    #                 for outpay in self.journal_id.outbound_payment_method_line_ids:
    #                     payment_methods.append(outpay.payment_method_id.id)
    #         # payment_methods = (
    #         #         self.payment_type == 'inbound' and
    #         #         self.journal_id.inbound_payment_method_line_ids or
    #         #         self.journal_id.outbound_payment_method_line_ids)
    #         # si es una transferencia y no hay payment method de origen,
    #         # forzamos manual
    #         print('payment_methods ====== ', payment_methods)
    #         if not payment_methods and self.payment_type == 'transfer':
    #             payment_methods = self.env.ref(
    #                 'account.account_payment_method_manual_out')
    #         self.payment_method_id = (
    #                 p for p in payment_methods or False)

