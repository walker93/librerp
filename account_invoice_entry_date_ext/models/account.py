# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2016 SimplERP srl (<http://www.simplerp.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
import datetime
import time
from openerp import models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def action_move_create(self, cr, uid, ids, context=None):
        if not context:
            context = {}

        for inv in self.browse(cr, uid, ids):
            date_invoice = inv.date_invoice
            reg_date = inv.registration_date
            if not inv.registration_date:
                if not inv.date_invoice:
                    reg_date = time.strftime('%Y-%m-%d')
                else:
                    reg_date = inv.date_invoice

            if date_invoice and reg_date:
                if date_invoice > reg_date:
                    raise Warning(_("The invoice date cannot be later than the"
                                    " date of registration!"))

            date_start = inv.registration_date or inv.date_invoice \
                or time.strftime('%Y-%m-%d')
            date_stop = inv.registration_date or inv.date_invoice \
                or time.strftime('%Y-%m-%d')

            period_ids = self.pool.get('account.period').search(
                cr, uid,
                [
                    ('date_start', '<=', date_start),
                    ('date_stop', '>=', date_stop),
                    ('company_id', '=', inv.company_id.id)
                    ])
            if period_ids:
                period_id = period_ids[0]

            self.write(
                cr, uid, [inv.id], {
                    'registration_date': reg_date, 'period_id': period_id})

        super(AccountInvoice, self).action_move_create(
            cr, uid, ids, context=context)

        for inv in self.browse(cr, uid, ids):
            sql = "update account_move_line set ref = '" + (
                inv.supplier_invoice_number and
                inv.supplier_invoice_number or ''
                ) + "' where move_id = " + str(inv.move_id.id)
            cr.execute(sql)

            self.pool['account.move'].write(
                cr, uid, [inv.move_id.id], {
                    'ref': inv.supplier_invoice_number and
                    inv.supplier_invoice_number or ''})

        return True

    def onchange_registration_date(
            self, cr, uid, ids, date_invoice, registration_date, context=None):
        current_fy = self.pool['account.fiscalyear'].find(
            cr, uid, dt=datetime.datetime.now(), context=context)
        registration_fy = self.pool['account.fiscalyear'].find(
            cr, uid, dt=date_invoice, context=context)

        if current_fy != registration_fy and not registration_date:
            return {
                'value': {},
                'warning': {
                    'title': 'Period selected is not in current fy !',
                    'message': '''If the registration date is null,
                    it will be filled with invoice date and period of
                    registration will be on a different fiscal year.
                    If it is not intended to do so, please fix registration
                    date.'''
                }
            }
