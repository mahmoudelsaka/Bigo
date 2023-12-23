# -*- coding: utf-8 -*-
# from odoo import http


# class CurrencyUnrealizedReport(http.Controller):
#     @http.route('/currency_unrealized_report/currency_unrealized_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/currency_unrealized_report/currency_unrealized_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('currency_unrealized_report.listing', {
#             'root': '/currency_unrealized_report/currency_unrealized_report',
#             'objects': http.request.env['currency_unrealized_report.currency_unrealized_report'].search([]),
#         })

#     @http.route('/currency_unrealized_report/currency_unrealized_report/objects/<model("currency_unrealized_report.currency_unrealized_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('currency_unrealized_report.object', {
#             'object': obj
#         })
