# -*- coding: utf-8 -*-
# from odoo import http


# class ImportAccountGroup(http.Controller):
#     @http.route('/import_account_group/import_account_group/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/import_account_group/import_account_group/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('import_account_group.listing', {
#             'root': '/import_account_group/import_account_group',
#             'objects': http.request.env['import_account_group.import_account_group'].search([]),
#         })

#     @http.route('/import_account_group/import_account_group/objects/<model("import_account_group.import_account_group"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('import_account_group.object', {
#             'object': obj
#         })
