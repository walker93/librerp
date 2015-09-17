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
from openerp.addons.base.res.res_partner import format_address


class crm_lead(format_address, osv.osv):
    _inherit = 'crm.lead'

    def write(self, cr, uid, ids, vals, context=None):
        # TODO: self.ensure_one()
        lead = self.browse(cr, uid, ids)[0]
        if lead.section_id and lead.section_id.change_responsible:
            vals.update({'user_id': lead.section_id.user_id.id})
        return super(crm_lead, self).write(cr, uid, ids, vals, context=context)
