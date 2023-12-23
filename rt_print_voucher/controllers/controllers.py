# -*- coding: utf-8 -*-
# from odoo import http


# class RtPrintVoucher(http.Controller):
#     @http.route('/rt_print_voucher/rt_print_voucher/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rt_print_voucher/rt_print_voucher/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rt_print_voucher.listing', {
#             'root': '/rt_print_voucher/rt_print_voucher',
#             'objects': http.request.env['rt_print_voucher.rt_print_voucher'].search([]),
#         })

#     @http.route('/rt_print_voucher/rt_print_voucher/objects/<model("rt_print_voucher.rt_print_voucher"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rt_print_voucher.object', {
#             'object': obj
#         })
