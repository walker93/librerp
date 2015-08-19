# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 SimplERP srl (<http://www.simplerp.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, models, fields


class mail_message(models.Model):
    _inherit = 'mail.message'

    @api.one
    @api.depends('author_id', 'notified_partner_ids')
    def _get_sent(self):
        self.sent = len(self.notified_partner_ids) > 1 or \
            len(self.notified_partner_ids) == 1 and \
            self.notified_partner_ids[0].id != self.author_id.id

    sent = fields.Boolean(
        'Sent', compute=_get_sent, help='Was message sent to someone',
        store=True)


class mail_notification(models.Model):
    _inherit = 'mail.notification'

    def _notify(self, cr, uid, message_id, **kwargs):
        super(mail_notification, self)._notify(
            cr, uid, message_id, **kwargs)
        self.pool['mail.message'].browse(cr, uid, message_id)._get_sent()
