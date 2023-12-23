# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import Warning
import base64, os
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import logging
import xlsxwriter
import time
from datetime import datetime


class PartnerStatementReport(models.TransientModel):
    _name = 'partner.statement.report'

    partner_id = fields.Many2one('res.partner', 'Partner')
    unit_id = fields.Many2one('crm.unit.state', 'Unit', required=1)
    excelfile = fields.Binary('Excel File')
    file_name = fields.Char('File Name')
    excel_flag = fields.Boolean('Show Excel File', default=lambda *a: False)

    def get_partner_data(self):
        res = self.read(['partner_id', 'unit_id'])
        res = res and res[0] or {}
        if not res['partner_id']:
            pids = self.env['res.partner'].search([('customer_rank', '>', 0)])
            res['partner_id'] = [x.id for x in pids]
        where = 0
        query = ('''
            SELECT ac.id,
            ac.amount,
            ac.payment_date,
            ac.installment_type,
            ac.state as  status,
            unit.name as unit,
            partner.name as partner,
            project.name as project
            FROM account_check as ac
            LEFT JOIN crm_unit_state as unit ON unit.id=ac.unit_id
            LEFT JOIN account_analytic_account as project ON project.id=ac.analytic_account_id
            LEFT JOIN res_partner as partner ON partner.id=ac.partner_id
            WHERE ac.unit_id=%s AND ac.state not in ('cancel', 'delivered')
            ''' % self.unit_id.id)

        if self.partner_id:
            where = "AND ac.partner_id=%s" % self.partner_id.id
        order = " ORDER BY ac.payment_date asc"

        if where:
            query += where
        query += order
        self.env.cr.execute(query)
        data = self.env.cr.dictfetchall()
        print('get_partner_data ============= ', data)
        return data

    def generate_check_excel_report(self):

        # Get today date to set it to report title
        today = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT).replace(':', '').replace(' ', '_').replace('-', '')
        filename = 'partner_statement_%s.xlsx' % today

        workbook = xlsxwriter.Workbook('/tmp/%s' % filename)
        worksheet = workbook.add_worksheet()

        # FORMATING PROPERTIES
        title_format = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#A9A9A9',  ##A9A9A9
            'underline': 2,
            'border': 1,
            'size': 14})
        total_format = workbook.add_format({'bold': 1, 'bg_color': '#ccccff', 'top': 1,
                                            'underline': 2, 'size': 10, 'align': 'center'})
        total_format.set_num_format('0.00')

        dateFormat = workbook.add_format({'num_format': 'dd/mm/yyyy',
                                          'size': 10, 'align': 'center', 'valign': 'vcenter'})

        td_left_bold = workbook.add_format({'size': 10, 'align': 'center', 'valign': 'vcenter', 'bold': 1})
        td_left = workbook.add_format({'size': 10, 'align': 'center', 'valign': 'vcenter'})

        float_format = workbook.add_format({'size': 10, 'align': 'center', 'valign': 'vcenter'})
        float_format.set_num_format('0,000.00')

        greyHeading = workbook.add_format({'bold': 1, 'align': 'center', 'valign': 'vcenter',
                                           'bg_color': '#A9A9A9', 'border': 1, 'size': 12})
        lightblueHeading = workbook.add_format({'bold': 1, 'align': 'center', 'valign': 'vcenter',
                                                'bg_color': '#B0C4DE', 'border': 1, 'size': 12})

        # Main Data Formating
        main_lightblueHeading = workbook.add_format({'bold': 1, 'align': 'left', 'valign': 'vcenter',
                                                'bg_color': '#B0C4DE', 'border': 1, 'size': 12})
        topLINE = workbook.add_format({'top': 6})
        # worksheet.right_to_left()

        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 25)
        worksheet.set_column('E:E', 25)
        worksheet.set_column('F:F', 25)
        worksheet.set_column('G:G', 25)
        worksheet.set_column('H:H', 25)

        worksheet.set_row(0, 30)

        # REPORT HEADING
        title = 'Partner Account Statement'
        worksheet.merge_range('A1:D1', title, title_format)

        # HEADINGS
        headings = [' ', 'Date', 'Desc.', 'Amount', 'Status']
        row = 2
        col = 0

        # Get Check Data
        data = self.get_partner_data()

        # Set Main Info in Excel Sheet
        sold_price = 0.0
        for unit in data:
            if unit['installment_type'] == 'unit':
                sold_price += unit['amount']

        discount = self.unit_id.unit_price - sold_price
        discount_percentage = 0.0
        if discount and self.unit_id.unit_price:
            discount_percentage = (discount / self.unit_id.unit_price) * 100
            if discount_percentage < 0:
                discount_percentage = discount_percentage * -1

        discount_percentage = str(round(discount_percentage, 2)) + ' %'

        # Calculate Total Down Payment amount
        # Calculate DownPayment Amount
        total_down_payment = 0.0
        for line in data:
            if line['installment_type'] == 'dp':
                total_down_payment += line['amount']

        # Partner Name
        partner_name = ''
        if self.partner_id:
            partner_name = self.partner_id.name

        worksheet.write(row, col, 'Customer', main_lightblueHeading)
        worksheet.write(row, col + 1, partner_name, td_left)
        # Project Name
        worksheet.write(row + 1, col, 'Project:', main_lightblueHeading)
        worksheet.write(row + 1, col + 1, self.unit_id.building_id.analytic_account_id.name, td_left)

        # Unit Name
        worksheet.write(row + 2, col, 'Unit No:', main_lightblueHeading)
        worksheet.write(row + 2, col + 1, self.unit_id.name, td_left)

        # Unit Price
        worksheet.write(row + 3, col, 'Origin Price', main_lightblueHeading)
        worksheet.write(row + 3, col + 1, self.unit_id.unit_price, float_format)
        # worksheet.write(row + 3, col + 2, 'EGP',td_left_bold )

        # Discount
        worksheet.write(row + 4, col, 'Discount Amount', main_lightblueHeading)
        worksheet.write(row + 4, col + 1, discount_percentage, td_left)
        worksheet.write(row + 4, col + 2, discount, float_format)

        # Sold Price
        worksheet.write(row + 5, col, 'Sold Price', main_lightblueHeading)
        worksheet.write(row + 5, col + 1, sold_price + total_down_payment, float_format)
        # worksheet.write(row + 5, col + 2, 'EGP', td_left_bold)

        row += 7
        # Set Heading

        for h in headings:
            worksheet.write(row, col, h, greyHeading)
            col += 1

        row += 1
        col = 0
        count = 1
        # Get Down Payment Data
        for line in data:
            if line['installment_type'] == 'dp':
                check = self.env['account.check'].browse(line['id'])
                status = check.get_status_value(check.state)
                worksheet.write(row, col + 1, line['payment_date'], dateFormat)
                worksheet.write(row, col + 2, 'Down Payment', td_left)
                worksheet.write(row, col + 3, total_down_payment, float_format)
                worksheet.write(row, col + 4, status, float_format)
        row += 1
        col = 0

        # Get Unit Data
        total_amount = 0.0
        for line in data:
            if line['installment_type'] == 'unit':
                check = self.env['account.check'].browse(line['id'])
                status = check.get_status_value(check.state)
                worksheet.write(row, col + 1, line['payment_date'], dateFormat)
                worksheet.write(row, col + 2, count, td_left)
                worksheet.write(row, col + 3, line['amount'], float_format)
                worksheet.write(row, col + 4, status, float_format)
                if check.state not in ['delivered']:
                    total_amount += line['amount']
                row += 1
                col = 0
                count += 1
        range_2 = 'A' + str(10) + ':' + 'A' + str(row)
        worksheet.merge_range(range_2, 'Payment Terms', greyHeading)
        total_range = 'A' + str(row + 1) + ':' + 'C' + str(row + 1)
        worksheet.merge_range(total_range, 'Total', lightblueHeading)
        worksheet.write(row, col + 3, total_amount + total_down_payment, lightblueHeading)
        worksheet.write(row, col + 4, ' ', lightblueHeading)
        row += 6
        col = 0

        maintenance_headings = ['Desc.', 'Date', 'Amount', 'Status']

        # Get Maintenance Data
        print('Row ======= ', row)
        range_1 = 'A' + str(row) + ':' + 'D' + str(row)
        print('range_1 ========== ', range_1)
        worksheet.merge_range(range_1, 'Maintenance', lightblueHeading)
        count = 1
        row += 1
        for h in maintenance_headings:
            worksheet.write(row, col, h, greyHeading)
            col += 1

        row += 1
        col = 0
        total_maintenance_amount = 0.0
        for rec in data:
            if rec['installment_type'] == 'main':
                check = self.env['account.check'].browse(rec['id'])
                status = check.get_status_value(check.state)
                main_desc = 'Maintenance' + str(count)
                worksheet.write(row, col, main_desc, td_left)
                worksheet.write(row, col + 1, rec['payment_date'], dateFormat)
                worksheet.write(row, col + 2, rec['amount'], float_format)
                worksheet.write(row, col + 3, status, float_format)
                row += 1
                col = 0
                count += 1
                total_maintenance_amount += rec['amount']

        # Total Amount For Maintenance
        total_range = 'A' + str(row + 1) + ':' + 'B' + str(row + 1)
        worksheet.merge_range(total_range, 'Total ', lightblueHeading)
        worksheet.write(row, col + 2, total_maintenance_amount, lightblueHeading)
        worksheet.write(row, col + 3, ' ', lightblueHeading)

        workbook.close()

        # FILE UPLOAD
        tf = open('/tmp/%s' % filename, 'rb')
        buf = tf.read()
        out = base64.encodebytes(buf)
        self.write({'excelfile': out, 'file_name': filename, 'excel_flag': True})
        tf.close()
        os.remove('/tmp/%s' % filename)
        return {'type': 'ir.actions.act_window',
                'res_model': 'partner.statement.report', 'view_mode': 'form',
                'view_type': 'form', 'res_id': self.id, 'target': 'new'}
