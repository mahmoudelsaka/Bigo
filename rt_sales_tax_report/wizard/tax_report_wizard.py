from odoo import models, fields, api
from io import BytesIO
import base64
from dateutil.relativedelta import relativedelta
import xlsxwriter
import logging
_logger = logging.getLogger(__name__)
import datetime



class PurchaseTaxWizard(models.TransientModel):
    _name = 'purchase.tax.wizard'

    from_date = fields.Date()
    to_date = fields.Date()
    tax_id = fields.Many2one(comodel_name="account.tax")
    document = fields.Binary()
    is_withholding = fields.Boolean(string="",)

    @api.onchange('tax_id')
    def set_value(self):
        self.to_date = fields.Date.today()
        self.from_date = fields.Date.today()


    @api.onchange('is_withholding')
    def onchange_check_box(self):
        taxes = []
        tax_not = []
        tax = self.env['account.tax'].sudo().search([('type_tax_use','=','purchase')])
        if self.is_withholding:
            for rec in tax:
                if rec.amount <= 0.0:
                   taxes.append(rec.id)
            if self.tax_id.id not in taxes:
                self.write({'tax_id': None})
            return {'domain': {'tax_id': [('id', 'in', taxes)]}}
        else:
             for rec in tax:
                if rec.amount > 0.0:
                   tax_not.append(rec.id)
             if self.tax_id.id not in tax_not:
                self.write({'tax_id': None})
             return {'domain': {'tax_id': [('id', 'in', tax_not)]}}           
            

    def get_data(self):
        cr = self.env.cr
        query = ('''
        SELECT am.name, am.invoice_date as inv_date,am.ref,am.move_type as move_type,
        am.id,am.doc_type,am.goods_type,am.tax_product,am.amount_tax,am.good_type,am.amount_untaxed,am.tax_type,am.tax_product,am.report_number,am.name,am.partner_id,
        partner.tax_file_number,partner.vat,partner.name as p_name,partner.city,partner.phone,
        mvl.tax_line_id,mvl.debit,mvl.move_id as move_id,mvl.credit,am.company_id,am.currency_id,mvl.amount_currency,mvl.move_id,mvl.company_id,at.id as tax_id,at.amount
        FROM account_move as am
        LEFT JOIN res_partner as partner ON partner.id=am.partner_id
        LEFT JOIN account_move_line as mvl ON mvl.move_id=am.id
        LEFT JOIN account_tax as  at ON at.id=mvl.tax_line_id
        WHERE am.invoice_date >='%s' AND am.invoice_date <='%s' And mvl.tax_line_id IS NOT NULL 
        AND am.move_type IN ('in_invoice','in_refund')
        AND am.state IN ('posted') AND am.company_id =%s AND at.id=%s
        ''' % (self.from_date, self.to_date, self.tax_id.company_id.id, self.tax_id.id))

        cr.execute(query)
        resault = cr.dictfetchall()
        temp = []
        data = []
        for rec in resault:
            dic = {
                'doc_type': rec['doc_type'],
                'tax_type': rec['tax_type'],
                'goods_type': rec['goods_type'],
                'ref': rec['ref'],
                'p_name': rec['p_name'],
                'id': rec['id'],
                'vat': rec['vat'],
                'tax_file_number': rec['tax_file_number'],
                'city': rec['city'],
                'company_id': rec['company_id'],
                'phone': rec['phone'],
                'inv_date': rec['inv_date'],
                'move_id': rec['move_id'],
                'tax_product': rec['tax_product'],
                'report_number': rec['report_number'],
                'good_type': rec['good_type'],
                'currency_id': rec['currency_id'],
                'tax_id': rec['tax_id'],
                'move_type':rec['move_type'],
                'debit': rec['debit'],
                'credit': rec['credit'],
                'amount_tax': rec['debit'] if rec['debit'] else rec['credit'],
                'amount_currency': rec['amount_currency'],
                'amount_untaxed': rec['amount_untaxed'],
                'is_withholding': self.is_withholding,

            }
            _logger.info("===========dic========== %s" %dic)    
            if [rec['id'], rec['tax_id']] in temp:
                for x in data:
                    if x['id'] == rec['id'] and x['tax_id'] == rec['tax_id']:
                        if rec['debit']:
                            x.update({'amount_tax': abs(x['amount_tax']) + abs(rec['debit'])})
                        else:
                            x.update({'amount_tax': x['amount_tax'] + rec['credit']})
                        x.update({'amount_currency': abs(x['amount_currency']) + abs(rec['amount_currency'])})
                        break
            else:
                temp.append([rec['id'], rec['tax_id']])
                data.append(dic)
            _logger.info("===========DATA========== %s" %data)    
        return data    

   
    def print_excel_report(self):
        file = BytesIO()
        workbook = xlsxwriter.Workbook(file, {'in_memory': True})
        format1 = workbook.add_format({'bold': True, 'color': 'white', 'bg_color': '#303233', 'align': 'center'})
        format2 = workbook.add_format({'color': '#303233', 'align': 'center'})
        sheet = workbook.add_worksheet()
        sheet.set_column('A1:A1', 55)
        sheet.set_column('B1:B1', 30)
        sheet.set_column('C1:C1', 30)
        sheet.set_column('D1:D1', 30)
        sheet.set_column('E1:E1', 30)
        sheet.set_column('F1:F1', 30)
        sheet.set_column('G1:G1', 30)
        sheet.set_column('H1:H1', 30)
        sheet.set_column('I1:I1', 30)
        sheet.set_column('J1:J1', 30)
        sheet.set_column('K1:K1', 30)
        sheet.set_column('L1:L1', 30)
        sheet.set_column('M1:M1', 30)
        sheet.set_column('N1:N1', 30)
        sheet.set_column('O1:O1', 30)
        sheet.set_column('P1:P1', 30)
        sheet.set_column('Q1:Q1', 30)
        sheet.set_column('R1:R1', 30)
        sheet.set_column('S1:S1', 30)
        sheet.right_to_left()
        date_from = self.from_date.strftime('%Y-%m-%d')
        date_to = self.to_date.strftime('%Y-%m-%d')

        sheet.write('B2', 'اقرار ضريبة القيمه المضافه', format1)
        sheet.write('A5',
                    'نوع المستند (فاتورة 1/ إشعار إضافة 2/إشعار خصم 3/إذن إفراج 4)',
                    format1)
        sheet.write('B5', 'نوع الضريبه(سلع عامه 1/سلع جدول 2)', format1)
        sheet.write('C5', 'نوع سلع الجدول(لا يوجد 0/جدول اولا 1/جدول ثانيا 2)', format1)
        sheet.write('D5', 'رقم الفاتورة', format1)
        sheet.write('E5', 'اسم المورد', format1)
        sheet.write('F5', 'رقم التسجيل الضريبي للعميل', format1)
        sheet.write('G5', 'رقم الملف الضريبي للعميل', format1)
        sheet.write('H5', 'العنوان', format1)
        sheet.write('I5', 'الرقم القومي/جواز السفر', format1)
        sheet.write('J5', 'رقم الموبايل', format1)
        sheet.write('K5', 'تاريخ الفاتوره', format1)
        sheet.write('L5', 'اسم المنتج', format1)
        sheet.write('M5', 'كود المنتج ', format1)
        sheet.write('N5', 'نوع البيان(سلعة 3/خدمه 4/تسويات 5)', format1)
        sheet.write('O5',
                    'نوع السلعه(محلي 1/صادرات 2/الات ومعدات 5/اجزاء الات 6/اعفاءات 7/سلع الجدول مراجعة الارشادات)',
                    format1)
        sheet.write('P5', 'وحدة قياس المنتج', format1)
        sheet.write('Q5', 'سعر الوحدة', format1)
        sheet.write('R5', 'فئة الضريبة', format1)
        sheet.write('S5', 'كمية المنتج', format1)
        sheet.write('T5', 'المبلغ الصافي', format1)
        sheet.write('U5', 'قيمة الضريبة', format1)
        sheet.write('V5', 'إجمالي', format1)

       
        col = 0
        row = 5
        data = self.get_data()
        total_amount = 0.0
        total_untax = 0.0
        total_tax_amount = 0.0
        amount = 0.0
        final_amount = 0.0
        _logger.info(f'Dattttttttttttttttttta ==========  {data}')
        line = []
        for rec in data:
            amount_tax = rec['amount_tax']
            invoice = rec['id']
            company = self.env['res.company'].sudo().search([('id', '=', rec['company_id'])], limit=1)
            name = rec['ref']
            if company.currency_id.id == rec['currency_id']:
                _logger.info(f'FF1111 final_amount$ ==========  {amount_tax},{name}')
                amount += abs(rec['amount_tax'])
                _logger.info("Payment Amount$$$ Remaining========== %s" % rec['amount_tax'])

            else:
                _logger.info(f'FF22222222 final_amount$ ==========  {final_amount},{name}')
                amount = abs(rec['amount_currency'])
                _logger.info("Payment Amount$$$ ========== %s" % amount)
            final_amount += amount
            # amount_tax = 0.0
            # if rec['is_withholding'] == True:
            #     amount_tax = -rec['amount_tax']
            # else:
            #     amount_tax = rec['amount_tax']
            
           

            _logger.info(f'FF333333333 final_amount$ ==========  {final_amount},{name}')
            tax_ammount = 0.0
            untax = rec['amount_untaxed']
            final_amount += amount
            if company.currency_id.id != rec['currency_id']:
                eg_currency = company.currency_id
                invoice_id = self.env['account.move'].browse(rec['id'])
                currency_id = invoice_id.currency_id.with_context(date=invoice_id.invoice_date)
                untax = currency_id._convert(rec['amount_untaxed'], eg_currency,
                                                         invoice_id.company_id,
                                                         invoice_id.invoice_date, round=True)


            amount_final = 0
            untax_amount = 0
            amount1 = rec['amount_tax']
            if rec['move_type'] == 'in_refund':
                amount_final = - amount1
                untax_amount = -untax
            else:
                untax_amount = untax
                amount_final = amount1

            tax_ammount +=  amount_final + untax_amount
            total_untax += untax
            print(rec['doc_type'])
            sheet.write(row, col, rec['doc_type'])
            sheet.write(row, col + 1, rec['tax_type'])
            sheet.write(row, col + 2, rec['goods_type'])
            sheet.write(row, col + 3, rec['ref'])
            sheet.write(row, col + 4, rec['p_name'])
            sheet.write(row, col + 5, rec['vat'])
            sheet.write(row, col + 6, rec['tax_file_number'])
            sheet.write(row, col + 7, rec['city'])
            sheet.write(row, col + 8, '')
            sheet.write(row, col + 9, rec['phone'])
            date_inv = rec['inv_date'].strftime('%Y-%m-%d')

            sheet.write(row, col + 10, date_inv)

            sheet.write(row, col + 11, rec['tax_product'])
            sheet.write(row, col + 12, 0)
            sheet.write(row, col + 13, rec['report_number'])
            sheet.write(row, col + 14, rec['good_type'])
            sheet.write(row, col + 15, 0)
            sheet.write(row, col + 16, untax_amount)
            sheet.write(row, col + 17, amount_final)
            # sheet.write(row, col + 17, rec['amount'])
            sheet.write(row, col + 18, 1)
            sheet.write(row, col + 19, untax_amount)
            sheet.write(row, col + 20, amount_final)

            # sheet.write(row, col + 20, amount)
            total_amount += amount
            sheet.write(row, col + 21, tax_ammount)
            total_tax_amount += tax_ammount
            row += 1

        sheet.write(row, col + 19, total_amount, format1)
        sheet.write(row, col + 20, total_untax, format1)
        sheet.write(row, col + 21, total_tax_amount, format1)
        sheet.merge_range(row, col, row, col + 18, 'المجموع', format1)

        workbook.close()
        file.seek(0)
        self.document = base64.encodebytes(file.getvalue())

        return {
            'type': 'ir.actions.act_url',
            'name': 'Consignment Sales',
            'url': '/web/content/%s/%s/document/%s .xlsx?download=true' % (
                self._name,
                self.id,
            str(datetime.datetime.now())),
            'target': 'new'
        }

class SaleTaxWizard(models.TransientModel):
    _name = 'sale.tax.wizard'

    from_date = fields.Date(string="", required=False, )
    to_date = fields.Date(string="", required=False, )
    tax_id = fields.Many2one(comodel_name="account.tax")
    document = fields.Binary()

    @api.onchange('tax_id')
    def set_value(self):
        self.to_date = fields.Date.today()
        self.from_date = fields.Date.today()

    # def test(self):
    #     user = self.env.user
    #     moves = self.env['account.move'].search(
    #         [('invoice_date', '>=', date_from), ('invoice_date', '<=', date_to),
    #          ('company_id', '<=', user.company_id.id)])
    #     print(moves)
    #     if self.tax_ids:
    #         for move in moves:
    #             tax_amount = 0.0
    #             for tax in self.tax_ids:
    #
    #                 move_lines = self.env['account.move.line'].search(
    #                     [('move_id', '=', move.id), ('tax_ids', '=', tax.id)])
    #                 if len(move_lines) > 0:
    #                     print('move_lines=========', move_lines)
    #                     for line in move_lines:
    #                         print(line, 'tax_line========', line.tax_line_id)
    #
    #                         if len(line.tax_line_id) > 0:
    #                             print('yes')

    def get_data(self):
        cr = self.env.cr
        query = ('''
        SELECT am.name, am.invoice_date as inv_date,am.ref,am.move_type as move_type,
        am.id,am.doc_type,am.goods_type,am.tax_product,am.amount_tax,am.good_type,am.amount_untaxed,am.tax_type,am.tax_product,am.report_number,am.name,am.partner_id,
        partner.tax_file_number,partner.vat,partner.name as p_name,partner.city,partner.phone,
        mvl.tax_line_id,mvl.debit,mvl.move_id as move_id,mvl.credit,am.company_id,am.currency_id,mvl.amount_currency,mvl.move_id,mvl.company_id,at.id as tax_id,at.amount
        FROM account_move as am
        LEFT JOIN res_partner as partner ON partner.id=am.partner_id
        LEFT JOIN account_move_line as mvl ON mvl.move_id=am.id
        LEFT JOIN account_tax as  at ON at.id=mvl.tax_line_id
        WHERE am.invoice_date >='%s' AND am.invoice_date <='%s' And mvl.tax_line_id IS NOT NULL 
        AND am.move_type IN ('out_invoice','out_refund')
        AND am.state IN ('posted') AND am.company_id =%s AND at.id=%s
        ''' % (self.from_date, self.to_date, self.tax_id.company_id.id, self.tax_id.id))

        cr.execute(query)
        resault = cr.dictfetchall()
        temp = []
        data = []
        for rec in resault:
            dic = {
                'doc_type': rec['doc_type'],
                'tax_type': rec['tax_type'],
                'goods_type': rec['goods_type'],
                'name': rec['name'],
                'p_name': rec['p_name'],
                'id': rec['id'],
                'vat': rec['vat'],
                'tax_file_number': rec['tax_file_number'],
                'city': rec['city'],
                'company_id': rec['company_id'],
                'phone': rec['phone'],
                'inv_date': rec['inv_date'],
                'move_id': rec['move_id'],
                'tax_product': rec['tax_product'],
                'report_number': rec['report_number'],
                'good_type': rec['good_type'],
                'currency_id': rec['currency_id'],
                'tax_id': rec['tax_id'],
                'move_type':rec['move_type'],
                'debit': rec['debit'],
                'credit': rec['credit'],
                'amount_tax': rec['debit'] if rec['debit'] else rec['credit'],
                'amount_currency': rec['amount_currency'],
                'amount_untaxed': rec['amount_untaxed'],

            }
            _logger.info("===========dic========== %s" %dic)    
            if [rec['id'], rec['tax_id']] in temp:
                for x in data:
                    if x['id'] == rec['id'] and x['tax_id'] == rec['tax_id']:
                        if rec['debit']:
                            x.update({'amount_tax': abs(x['amount_tax']) + abs(rec['debit'])})
                        else:
                            x.update({'amount_tax': x['amount_tax'] + rec['credit']})
                        x.update({'amount_currency': abs(x['amount_currency']) + abs(rec['amount_currency'])})
                        break
            else:
                temp.append([rec['id'], rec['tax_id']])
                data.append(dic)
            _logger.info("===========DATA========== %s" %data)    
        return data    


    def print_excel_report(self):
        file = BytesIO()
        workbook = xlsxwriter.Workbook(file, {'in_memory': True})
        format1 = workbook.add_format({'bold': True, 'color': 'white', 'bg_color': '#303233', 'align': 'center'})
        format2 = workbook.add_format({'color': '#303233', 'align': 'center'})
        sheet = workbook.add_worksheet()
        sheet.set_column('A1:A1', 55)
        sheet.set_column('B1:B1', 30)
        sheet.set_column('C1:C1', 30)
        sheet.set_column('D1:D1', 30)
        sheet.set_column('E1:E1', 30)
        sheet.set_column('F1:F1', 30)
        sheet.set_column('G1:G1', 30)
        sheet.set_column('H1:H1', 30)
        sheet.set_column('I1:I1', 30)
        sheet.set_column('J1:J1', 30)
        sheet.set_column('K1:K1', 30)
        sheet.set_column('L1:L1', 30)
        sheet.set_column('M1:M1', 30)
        sheet.set_column('N1:N1', 30)
        sheet.set_column('O1:O1', 30)
        sheet.set_column('P1:P1', 30)
        sheet.set_column('Q1:Q1', 30)
        sheet.set_column('R1:R1', 30)
        sheet.set_column('S1:S1', 30)
        sheet.right_to_left()
        date_from = self.from_date.strftime('%Y-%m-%d')
        date_to = self.to_date.strftime('%Y-%m-%d')

        sheet.write('B2', 'اقرار ضريبة القيمه المضافه', format1)
        sheet.write('A5',
                    'نوع المستند (فاتورة 1/ إشعار إضافة 2/إشعار خصم 3/إذن إفراج 4)',
                    format1)
        sheet.write('B5', 'نوع الضريبه(سلع عامه 1/سلع جدول 2)', format1)
        sheet.write('C5', 'نوع سلع الجدول(لا يوجد 0/جدول اولا 1/جدول ثانيا 2)', format1)
        sheet.write('D5', 'رقم الفاتورة', format1)
        sheet.write('E5', 'اسم المورد', format1)
        sheet.write('F5', 'رقم التسجيل الضريبي للعميل', format1)
        sheet.write('G5', 'رقم الملف الضريبي للعميل', format1)
        sheet.write('H5', 'العنوان', format1)
        sheet.write('I5', 'الرقم القومي/جواز السفر', format1)
        sheet.write('J5', 'رقم الموبايل', format1)
        sheet.write('K5', 'تاريخ الفاتوره', format1)
        sheet.write('L5', 'اسم المنتج', format1)
        sheet.write('M5', 'كود المنتج ', format1)
        sheet.write('N5', 'نوع البيان(سلعة 3/خدمه 4/تسويات 5)', format1)
        sheet.write('O5',
                    'نوع السلعه(محلي 1/صادرات 2/الات ومعدات 5/اجزاء الات 6/اعفاءات 7/سلع الجدول مراجعة الارشادات)',
                    format1)
        sheet.write('P5', 'وحدة قياس المنتج', format1)
        sheet.write('Q5', 'سعر الوحدة', format1)
        sheet.write('R5', 'فئة الضريبة', format1)
        sheet.write('S5', 'كمية المنتج', format1)
        sheet.write('T5', 'المبلغ الصافي', format1)
        sheet.write('U5', 'قيمة الضريبة', format1)
        sheet.write('V5', 'إجمالي', format1)

       
        col = 0
        row = 5
        data = self.get_data()
        total_amount = 0.0
        total_untax = 0.0
        total_tax_amount = 0.0
        amount = 0.0
        final_amount = 0.0
        _logger.info(f'Dattttttttttttttttttta ==========  {data}')
        line = []
        for rec in data:
            amount_tax = rec['amount_tax']
            invoice = rec['id']
            company = self.env['res.company'].sudo().search([('id', '=', rec['company_id'])], limit=1)
            name = rec['name']
            if company.currency_id.id == rec['currency_id']:
                _logger.info(f'FF1111 final_amount$ ==========  {amount_tax},{name}')
                amount += abs(rec['amount_tax'])
                _logger.info("Payment Amount$$$ Remaining========== %s" % rec['amount_tax'])

            else:
                _logger.info(f'FF22222222 final_amount$ ==========  {final_amount},{name}')
                amount = abs(rec['amount_currency'])
                _logger.info("Payment Amount$$$ ========== %s" % amount)
            final_amount += amount
            # amount_tax = 0.0
            # if rec['is_withholding'] == True:
            #     amount_tax = -rec['amount_tax']
            # else:
            #     amount_tax = rec['amount_tax']
            
           

            _logger.info(f'FF333333333 final_amount$ ==========  {final_amount},{name}')
            tax_ammount = 0.0
            untax = rec['amount_untaxed']
            final_amount += amount
            if company.currency_id.id != rec['currency_id']:
                eg_currency = company.currency_id
                invoice_id = self.env['account.move'].browse(rec['id'])
                currency_id = invoice_id.currency_id.with_context(date=invoice_id.invoice_date)
                untax = currency_id._convert(rec['amount_untaxed'], eg_currency,
                                                         invoice_id.company_id,
                                                         invoice_id.invoice_date, round=True)


            amount_final = 0
            untax_amount = 0
            amount1 = rec['amount_tax']
            if rec['move_type'] == 'out_refund':
                amount_final = - amount1
                untax_amount = -untax
            else:
                untax_amount = untax
                amount_final = amount1
            tax_ammount +=  amount_final + untax_amount
            total_untax += untax
            print(rec['doc_type'])
            sheet.write(row, col, rec['doc_type'])
            sheet.write(row, col + 1, rec['tax_type'])
            sheet.write(row, col + 2, rec['goods_type'])
            sheet.write(row, col + 3, rec['name'])
            sheet.write(row, col + 4, rec['p_name'])
            sheet.write(row, col + 5, rec['vat'])
            sheet.write(row, col + 6, rec['tax_file_number'])
            sheet.write(row, col + 7, rec['city'])
            sheet.write(row, col + 8, '')
            sheet.write(row, col + 9, rec['phone'])
            date_inv = rec['inv_date'].strftime('%Y-%m-%d')

            sheet.write(row, col + 10, date_inv)

            sheet.write(row, col + 11, rec['tax_product'])
            sheet.write(row, col + 12, 0)
            sheet.write(row, col + 13, rec['report_number'])
            sheet.write(row, col + 14, rec['good_type'])
            sheet.write(row, col + 15, 0)
            sheet.write(row, col + 16, untax_amount)
            sheet.write(row, col + 17, amount_final)
            # sheet.write(row, col + 17, rec['amount'])
            sheet.write(row, col + 18, 1)
            sheet.write(row, col + 19, untax_amount)
            sheet.write(row, col + 20, amount_final)

            # sheet.write(row, col + 20, amount)
            total_amount += amount
            sheet.write(row, col + 21, tax_ammount)
            total_tax_amount += tax_ammount
            row += 1

        sheet.write(row, col + 19, total_amount, format1)
        sheet.write(row, col + 20, total_untax, format1)
        sheet.write(row, col + 21, total_tax_amount, format1)
        sheet.merge_range(row, col, row, col + 18, 'المجموع', format1)

        workbook.close()
        file.seek(0)
        self.document = base64.encodebytes(file.getvalue())

        return {
            'type': 'ir.actions.act_url',
            'name': 'Consignment Sales',
            'url': '/web/content/%s/%s/document/%s .xlsx?download=true' % (
                self._name,
                self.id,
            str(datetime.datetime.now())),
            'target': 'new'
        }

