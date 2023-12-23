# -*- coding: utf-8 -*-
# from odoo import http


# class InvoiceArAp(http.Controller):
#     @http.route('/invoice_ar_ap/invoice_ar_ap', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_ar_ap/invoice_ar_ap/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_ar_ap.listing', {
#             'root': '/invoice_ar_ap/invoice_ar_ap',
#             'objects': http.request.env['invoice_ar_ap.invoice_ar_ap'].search([]),
#         })

#     @http.route('/invoice_ar_ap/invoice_ar_ap/objects/<model("invoice_ar_ap.invoice_ar_ap"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_ar_ap.object', {
#             'object': obj
#         })
