from odoo import models, api, fields, _


class UpdateLayerDate(models.TransientModel):
    _name = 'update.layer.date'

    date = fields.Datetime('Date')

    def update_layer_date(self):
        for rec in self.env['stock.valuation.layer'].browse(self._context.get('active_ids', [])):
            if self.date and rec.create_date:
                self._cr.execute("UPDATE stock_valuation_layer SET create_date='%s' WHERE id=%s"% (self.date, rec.id))
        return
