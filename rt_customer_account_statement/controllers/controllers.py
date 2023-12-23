# -*- coding: utf-8 -*-
# from odoo import http


# class RtCustomerAccountStatement(http.Controller):
#     @http.route('/rt_customer_account_statement/rt_customer_account_statement/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rt_customer_account_statement/rt_customer_account_statement/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rt_customer_account_statement.listing', {
#             'root': '/rt_customer_account_statement/rt_customer_account_statement',
#             'objects': http.request.env['rt_customer_account_statement.rt_customer_account_statement'].search([]),
#         })

#     @http.route('/rt_customer_account_statement/rt_customer_account_statement/objects/<model("rt_customer_account_statement.rt_customer_account_statement"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rt_customer_account_statement.object', {
#             'object': obj
#         })
