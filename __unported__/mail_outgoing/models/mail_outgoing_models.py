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

from openerp.osv import osv


class mail_message(osv.Model):
    _inherit = 'mail.message'

    def check_access_rule(self, cr, uid, ids, operation, context=None):
        group_all_emails = self.pool.get('ir.model.data').xmlid_to_object(
            cr, uid, 'mail_outgoing.group_all_emails', context=context)

        user = self.pool['res.users'].browse(cr, uid, uid, context)
        user_groups = set(user.groups_id)
        if user_groups.issuperset(group_all_emails):
            return

        return super(mail_message, self).check_access_rule(cr, uid, ids,
                                                           operation, context)


class mail_mail(osv.Model):
    _name = 'mail.mail'
    _inherit = ['mail.mail', 'ir.needaction_mixin']
    _needaction = True

    def _needaction_domain_get(self, cr, uid, context=None):
        return [('state', 'in', ['outgoing', 'exception'])]
