# -*- coding: utf-8 -*-
# from odoo import http


# class GatesAccountCheck(http.Controller):
#     @http.route('/account_check_batch/account_check_batch/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_check_batch/account_check_batch/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_check_batch.listing', {
#             'root': '/account_check_batch/account_check_batch',
#             'objects': http.request.env['account_check_batch.account_check_batch'].search([]),
#         })

#     @http.route('/account_check_batch/account_check_batch/objects/<model("account_check_batch.account_check_batch"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_check_batch.object', {
#             'object': obj
#         })
