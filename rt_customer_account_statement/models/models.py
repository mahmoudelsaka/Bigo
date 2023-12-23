# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountCheck(models.Model):
    _inherit = 'account.check'

    def get_status_value(self, state):
        status = 'Draft'
        for rec in self:
            if state == 'draft':
                status = 'Draft'

            if state == 'transfered':
                status = 'Under Collection'
            if state == 'holding':
                status = 'Holding'
            if state == 'deposited':
                status = 'Collected'
            if state == 'selled':
                status = 'Selled'
            if state == 'delivered':
                status = 'Replaced'
            if state == 'cashed':
                status = 'Cashed'
            if state == 'handed':
                status = 'Handed'
            if state == 'rejected':
                status = 'Rejected'
            if state == 'credited':
                status = 'Credited'
            if state == 'changed':
                status = 'Changed'

            if state == 'returned':
                status = 'Returned'
        return status

