from odoo import models, fields, api
from io import BytesIO
import base64
from dateutil.relativedelta import relativedelta
import xlsxwriter


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    tax_file_number = fields.Char(help="رقم الملف الضريبي للعميل")


class JournalInherit(models.Model):
    _inherit = 'account.journal'

    doc_type = fields.Char(
        help="نوع المستند(فاتوره 1/اشعار اضافه 2/اشعار خصم 3/مستهلك نهائي محلي 5/جهة حكومة 6/مستهلك نهائي اجنبي 7)")
    tax_type = fields.Char(help="سلع عامه 1/سلع جدول 2")
    goods_type = fields.Char(help="لا يوجد 0/جدول اولا 1/جدول ثانيا 2")
    good_type = fields.Char(help="محلي 1/صادرات 2/الات ومعدات 5/اجزاء الات 6/اعفاءات 7/سلع الجدول مراجعة الارشادات")
    tax_product = fields.Char(help="اسم المنتج")
    report_number = fields.Char(help="سلعة 3/خدمه 4/تسويات 5")


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    doc_type = fields.Char(
        help="نوع المستند(فاتوره 1/اشعار اضافه 2/اشعار خصم 3/مستهلك نهائي محلي 5/جهة حكومة 6/مستهلك نهائي اجنبي 7)")
    tax_type = fields.Char(help="سلع عامه 1/سلع جدول 2")
    goods_type = fields.Char(help="لا يوجد 0/جدول اولا 1/جدول ثانيا 2")
    tax_file_number = fields.Char(help="رقم الملف الضريبي للعميل")
    tax_product = fields.Char(help="اسم المنتج")
    report_number = fields.Char(help="سلعة 3/خدمه 4/تسويات 5")
    good_type = fields.Char(help="محلي 1/صادرات 2/الات ومعدات 5/اجزاء الات 6/اعفاءات 7/سلع الجدول مراجعة الارشادات")

    @api.onchange('partner_id')
    def set_default_value_file(self):
        for r in self:
            r.tax_file_number = r.partner_id.tax_file_number

    @api.onchange('journal_id')
    def _set_default_value(self):
        print('========== TEST =====')
        print('========== print =====')
        for rec in self:
            print(rec.journal_id)
            rec.doc_type = rec.journal_id.doc_type
            rec.tax_type = rec.journal_id.tax_type
            rec.goods_type = rec.journal_id.goods_type
            rec.good_type = rec.journal_id.good_type
            rec.tax_product = rec.journal_id.tax_product
            rec.report_number = rec.journal_id.report_number
