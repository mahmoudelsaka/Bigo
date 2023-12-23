# -*- coding: utf-8 -*-
# from odoo import http


# class RtAddPoGroup(http.Controller):
#     @http.route('/rt_add_po_group/rt_add_po_group', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rt_add_po_group/rt_add_po_group/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('rt_add_po_group.listing', {
#             'root': '/rt_add_po_group/rt_add_po_group',
#             'objects': http.request.env['rt_add_po_group.rt_add_po_group'].search([]),
#         })

#     @http.route('/rt_add_po_group/rt_add_po_group/objects/<model("rt_add_po_group.rt_add_po_group"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rt_add_po_group.object', {
#             'object': obj
#         })
