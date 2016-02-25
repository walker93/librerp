# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2016 Sergio Corato - SimplERP srl (<http://www.simplerp.it>)
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
from openerp import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if 'country_id' in vals and not 'property_account_position' in vals:
            fp = self.env['account.fiscal.position'].search(
                [('country_id', '=', vals['country_id'])], limit=1)
            if fp:
                res.property_account_position = fp
        return res

    @api.model
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if 'country_id' in vals and not 'property_account_position' in vals:
            fp = self.env['account.fiscal.position'].search(
                [('country_id', '=', vals['country_id'])], limit=1)
            if fp:
                res.property_account_position = fp
        return res
