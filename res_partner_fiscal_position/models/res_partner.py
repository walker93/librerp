# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if vals.get('country_id', False) and not vals.get(
                'property_account_position', False):
            fp = self.env['account.fiscal.position'].search(
                [('country_id', '=', vals['country_id'])], limit=1)
            if not fp:
                country = self.env['res.country'].browse(vals['country_id'])
                if country.country_group_ids:
                    fp = self.env['account.fiscal.position'].search(
                        [('country_group_id', '=',
                          country.country_group_ids[0].id)], limit=1)
            if fp:
                res.property_account_position = fp
        return res

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if vals.get('country_id', False) and not vals.get(
                'property_account_position', False):
            fp = self.env['account.fiscal.position'].search(
                [('country_id', '=', vals['country_id'])], limit=1)
            if not fp:
                country = self.env['res.country'].browse(vals['country_id'])
                if country.country_group_ids:
                    fp = self.env['account.fiscal.position'].search(
                        [('country_group_id', '=',
                          country.country_group_ids[0].id)], limit=1)
            if fp:
                res.property_account_position = fp
        return res
