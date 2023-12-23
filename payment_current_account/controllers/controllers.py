# -*- coding: utf-8 -*-
# from odoo import http


# class PaymentCurrentAccount(http.Controller):
#     @http.route('/payment_current_account/payment_current_account', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payment_current_account/payment_current_account/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('payment_current_account.listing', {
#             'root': '/payment_current_account/payment_current_account',
#             'objects': http.request.env['payment_current_account.payment_current_account'].search([]),
#         })

#     @http.route('/payment_current_account/payment_current_account/objects/<model("payment_current_account.payment_current_account"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payment_current_account.object', {
#             'object': obj
#         })
