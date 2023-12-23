from odoo import http
from odoo.http import request
from datetime import datetime
from odoo import Command
import logging
from odoo.addons.portal.controllers import portal
from odoo.exceptions import UserError, ValidationError
import re
import base64, os

TAG_RE = re.compile(r'<[^>]+>')

_logger = logging.getLogger(__name__)


class PoOrders(http.Controller):
    @http.route('/po/orders', website=True, auth="public")
    def po_orders(self, **kw):
        user_id = request.env.user
        orders = request.env['purchase.request'].sudo().search([('requested_by', '=', user_id.id)])
        return request.render("rt_website_purchase_request.po_orders", {
            'orders': orders
        })


class PoWebsite(http.Controller):
    @http.route('/create_po_web_order', website=True, auth="user")
    def po_webform(self, **kw):
        vendors = False
        products = request.env['product.product'].sudo().search([('purchase_ok', '=', True)])
        user = request.env.user.id
        _logger.info(f'****** user  ttt ****** {user}')
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user)], limit=1)
        _logger.info(f'****** employee  ****** {employee}')
        if employee:
            vendors = employee.parent_id.user_id
            _logger.info(f'****** approve  ****** {vendors}')
        res_currency = request.env['res.currency'].sudo().search([])

        type = request.env['purchase.request.type'].sudo().search([])
        return http.request.render('rt_website_purchase_request.create_po_from_website', {
            'assigned_to': vendors,
            'currency_id': res_currency,
            'product_id': products,
            'type': type,
        })

    # this is for cancel purchase request order
    @http.route(['/cancel/pr/<int:id>'], website=True, auth="public")
    def cancel_purchase_request_order(self, id=None, **kw):
        print('=========== this is the cancel function ==========')
        print('=========== the id is =============', id)
        user_id = request.env.user
        print('=========== user_id =============', user_id)
        if id:
            purchase_request_order = request.env['purchase.request'].sudo().search([('id', '=', int(id))])
            if purchase_request_order:
                purchase_request_order.write({
                    'state': 'cancel'
                })
                orders = request.env['purchase.request'].sudo().search([('requested_by', '=', user_id.id)])
                return request.render("rt_website_purchase_request.po_orders", {
                    'orders': orders
                })

    # @http.route('/create/po_web', website=True, auth="user")
    # def create_po_webform(self, **kw):
    #     print('============ 1 ==========')
    #     gl_account_id = request.env['account.account'].sudo().search([('is_request', '=', True)])
    #     current_date_and_time = datetime.now()
    #
    #     user = request.env.user.id
    #     employee = request.env['hr.employee'].sudo().search([('user_id', '=', user)], limit=1)
    #     vendors = employee.parent_id.user_id
    #
    #     val = {
    #         'name': kw['name'],
    #         'assigned_to': vendors.id,
    #         'date_start': current_date_and_time,
    #         'note': kw['description'],
    #         'type': kw['type']
    #     }
    #     po = request.env['purchase.request'].sudo().create(val)
    #
    #     products = request.env['product.product'].sudo().search([])
    #     return http.request.render('rt_website_purchase_request.add_lines', {
    #         'id': po.id,
    #         'name': po.name,
    #         'assigned_to': po.assigned_to,
    #         'gl_account_id': gl_account_id,
    #         'product_id': products,
    #     })

    @http.route(['/create/po_web', '/create/po_web/<int:po_id>'], website=True, auth="public")
    def create_po_webform(self, po_id=None, **kw):
        products = request.env['product.product'].sudo().search([('purchase_ok', '=', True)])
        gl_account_id = request.env['account.account'].sudo().search([('is_request', '=', True)])
        user = request.env.user.id
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user)], limit=1)
        vendors = employee.parent_id.user_id
        current_date_and_time = datetime.now()
        if po_id != None:
            po_rec = request.env['purchase.request'].sudo().search([('id', '=', int(po_id))])
            if po_rec:
                return http.request.render('rt_website_purchase_request.add_lines', {
                    'id': po_rec[0].id,
                    'name': po_rec[0].name,
                    'assigned_to': po_rec[0].assigned_to,
                    'product_id': products,
                    'gl_account_id': gl_account_id,
                    'po_rec': po_rec,
                })
        if vendors:
            val = {
                'name': 'New',
                'assigned_to': vendors.id,
                'requested_by': request.env.user.id,
                'date_start': current_date_and_time,
                'note': kw['description'],
                'type': kw['type']
            }
            po = request.env['purchase.request'].sudo().create(val)
            products = request.env['product.product'].sudo().search([])
            po_obj = request.env['purchase.request']
            attachment = request.env['ir.attachment']
            files = request.httprequest.files.getlist('att[]')
            for file in files:
                file_name = file.filename
                attachment_id = attachment.create({
                    'name': file_name,
                    'type': 'binary',
                    'datas': base64.b64encode(file.read()),
                    'res_model': po_obj._name,
                    'res_id': po_obj.id
                })
                po.update({
                    'attachment': [(4, attachment_id.id)],
                })
            return http.request.render('rt_website_purchase_request.add_lines', {
                'id': po.id,
                'name': po.name,
                'assigned_to': po.assigned_to,
                'product_id': products,
                'gl_account_id': gl_account_id,
                'po_rec': po,
            })
        else:
            return http.request.render('rt_website_purchase_request.check_manager', {})

    @http.route('/create/po_line', website=True, auth="user")
    def create_po_line(self, **kw):
        id = int(kw['id'])
        product_id = int(kw['product_id'])
        product_obj = request.env['product.product'].sudo().search([('id', '=', product_id)])
        gl_account_id = request.env['account.account'].sudo().search([('is_request', '=', True)])
        product_qty = 0.0
        price_unit = 0.0
        descrption = kw['description']
        if kw['product_qty']:
            product_qty = float(kw['product_qty'])
        if kw['price_unit']:
            price_unit = float(kw['price_unit'])
        po = request.env['purchase.request'].sudo().search([('id', '=', id)])

        val_l = {
            'request_id': po.id,
            'name': descrption,
            'product_id': product_id,
            'product_qty': product_qty,
            'gl_account_id': int(kw['gl_account_id']),
            'estimated_cost': price_unit,
            'product_uom_id': product_obj.uom_id.id,
        }
        pol = request.env['purchase.request.line'].sudo().create(val_l)
        return request.redirect(f'/create/po_web/{po.id}')

    @http.route(['/po/info/<int:id>'], website=True, auth="public")
    def get_po_info(self, id=None, **kw):
        purchase_request = request.env['purchase.request'].sudo().search([('id', '=', int(id))])
        lines = purchase_request.line_ids
        return http.request.render('rt_website_purchase_request.get_po_info', {
            'purchase_request': purchase_request,
            'lines': lines,
        })

    @http.route(['/line/update/<int:id>'], website=True, auth="user")
    def update_line(self, id=None, **kw):
        purchase_request_line = request.env['purchase.request.line'].sudo().search([('id', '=', int(id))])

        products = request.env['product.product'].sudo().search([('purchase_ok', '=', True)])

        return http.request.render('rt_website_purchase_request.update_order_line', {
            'purchase_request_line': purchase_request_line,
            'products': products
        })

    @http.route(['/update/line'], website=True, auth="user")
    def update_line_data(self, **kw):
        line_id = kw['line_id']
        product_id = kw['product_id']
        product_qty = kw['product_qty']
        price_unit = kw['price_unit']
        purchase_line = request.env['purchase.request.line'].sudo().search([('id', '=', int(line_id))])
        gl_account_id = request.env['account.account'].sudo().search([('is_request', '=', True)])
        po = purchase_line.request_id
        products = request.env['product.product'].sudo().search([('purchase_ok', '=', True)])
        purchase_line.write({
            'product_id': int(product_id),
            'product_qty': int(product_qty),
            'estimated_cost': int(price_unit)
        })
        return http.request.render('rt_website_purchase_request.add_lines', {
            'id': po.id,
            'name': po.name,
            'assigned_to': po.assigned_to,
            'product_id': products,
            'gl_account_id': gl_account_id,
            'po_rec': po,
        })

    @http.route(['/submit_br'], website=True, auth="user")
    def submit_br_request(self, **kw):
        id = int(kw['id'])
        if id:
            pr = request.env['purchase.request'].sudo().search([('id', '=', id)])
            if pr.state != 'to_approve':
                pr.write({
                    'state': 'to_approve'
                })
                lines = pr.line_ids
                return http.request.render('rt_website_purchase_request.get_po_info', {
                    'purchase_request': pr,
                    'lines': lines,
                })
        else:
            print('========= there is not id here ==============')

    @http.route(['/edit/pr', '/edit/pr/<int:pr_id>'], website=True, auth="user")
    def edit_pr_webform(self, pr_id=None, **kw):
        pr_rec = request.env['purchase.request'].sudo().search([('id', '=', int(pr_id))])
        note = str(pr_rec.note)
        new_note = TAG_RE.sub('', note)
        print('=========== new note =============', new_note)
        user = request.env.user.id
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user)], limit=1)
        vendors = employee.parent_id.user_id
        type = request.env['purchase.request.type'].sudo().search([])
        return http.request.render('rt_website_purchase_request.edit_pr_from_website', {
            'approve_id': vendors,
            'type': type,
            'description': pr_rec.note,
            'test_desc': new_note,
            'pr_rec': pr_rec,
            'id': pr_rec.id,
        })

    @http.route('/edit/pr_web', website=True, auth="user")
    def edit_pr_web_form(self, sr_id=None, **kw):
        id = int(kw['id'])
        assigned_to = int(kw['approve_id'])
        type = int(kw['type'])
        description = kw['description']

        purchase_request_obj = request.env['purchase.request'].sudo().search([('id', '=', id)])
        print('========== HERE ==========')
        po_obj = request.env['purchase.request']
        attachment = request.env['ir.attachment']
        files = request.httprequest.files.getlist("att[]")
        print('========= files =========', files)
        purchase_request_obj.attachment = [(5, 0, 0)]
        for file in files:
            file_name = file.filename
            attachment_id = attachment.create({
                'name': file_name,
                'type': 'binary',
                'datas': base64.b64encode(file.read()),
                'res_model': po_obj._name,
                'res_id': po_obj.id
            })
            # purchase_request_obj.write({
            #     'attachment': (6, 0, []),
            # })
            purchase_request_obj.write({
                'attachment': [(4, attachment_id.id)],
            })
        sr = purchase_request_obj.write({
            'assigned_to': assigned_to,
            'type': type,
            'note': description,
        })
        company_id = request.env.company.id
        product = request.env['product.product'].sudo().search([('purchase_ok', '=', True)])
        uom = request.env['uom.uom'].sudo().search([])
        route = request.env['stock.route'].sudo().search([('company_id', '=', company_id)])
        print('============= TEST HERE ===========')
        return http.request.render('rt_website_purchase_request.add_lines', {
            'id': purchase_request_obj.id,
            'name': purchase_request_obj.name,
            'product': product,
            'uom': uom,
            'route': route,
            'company_id': company_id,
            'po_rec': purchase_request_obj,
        })

    @http.route(['/cancel/sr/<int:id>'], website=True, auth="public")
    def cancel_stock_request_order(self, id=None, **kw):
        print('=========== this is the cancel function ==========')
        print('=========== the id is =============', id)
        if id:
            stock_request_order = request.env['stock.request.order'].sudo().search([('id', '=', int(id))])
            if stock_request_order:
                stock_request_order.write({
                    'state': 'draft'
                })
                orders = request.env['stock.request.order'].sudo().search([])
                return request.render("rt_portal_stock_request.sr_orders", {
                    'orders': orders
                })

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        """Set the count as None"""

        if 'p_count' in counters:
            values['p_count'] = None
        return values


class CustomerPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        """Set the count as None"""

        if 'p_count' in counters:
            values['p_count'] = None
        return values

    @http.route('/product/search', type='json', auth="user", website=True)
    def search_product(self, **kw, ):
        """To get corresponding products"""
        product = kw.get('name')
        rec_id = kw.get('rec_id')
        print('========= rec id ==========', rec_id)
        if product:
            type = ''
            purchase_request = request.env['purchase.request'].sudo().search([('id', '=', rec_id)])
            if purchase_request:
                if purchase_request.type:
                    type = purchase_request.type.product_type
            if type:
                if type == 'storable':
                    res = request.env['product.product'].sudo().search_read(
                        [('name', 'ilike', product), ('purchase_ok', '=', True), ('detailed_type', '=', 'product')],
                        limit=50)
                    return res
                else:
                    res = request.env['product.product'].sudo().search_read(
                        [('name', 'ilike', product), ('purchase_ok', '=', True), ('detailed_type', '!=', 'product')],
                        limit=50)
                    return res
            else:
                res = request.env['product.product'].sudo().search_read(
                    [('name', 'ilike', product), ('purchase_ok', '=', True)],
                    limit=50)
                return res
        else:
            return False
