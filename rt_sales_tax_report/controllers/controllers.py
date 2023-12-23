# -*- coding: utf-8 -*-
# from odoo import http


# class RtSalesTaxReport(http.Controller):
#     @http.route('/rt_sales_tax_report/rt_sales_tax_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rt_sales_tax_report/rt_sales_tax_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rt_sales_tax_report.listing', {
#             'root': '/rt_sales_tax_report/rt_sales_tax_report',
#             'objects': http.request.env['rt_sales_tax_report.rt_sales_tax_report'].search([]),
#         })

#     @http.route('/rt_sales_tax_report/rt_sales_tax_report/objects/<model("rt_sales_tax_report.rt_sales_tax_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rt_sales_tax_report.object', {
#             'object': obj
#         })
