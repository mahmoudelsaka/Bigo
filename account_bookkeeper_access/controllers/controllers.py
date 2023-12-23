# -*- coding: utf-8 -*-
# from odoo import http


# class AccountBookkeeperAccess(http.Controller):
#     @http.route('/account_bookkeeper_access/account_bookkeeper_access', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_bookkeeper_access/account_bookkeeper_access/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_bookkeeper_access.listing', {
#             'root': '/account_bookkeeper_access/account_bookkeeper_access',
#             'objects': http.request.env['account_bookkeeper_access.account_bookkeeper_access'].search([]),
#         })

#     @http.route('/account_bookkeeper_access/account_bookkeeper_access/objects/<model("account_bookkeeper_access.account_bookkeeper_access"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_bookkeeper_access.object', {
#             'object': obj
#         })
