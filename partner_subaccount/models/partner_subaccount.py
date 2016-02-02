# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 SimplERP srl (<http://www.simplerp.it>).
#    Copyright (c) 2014 Didotech SRL (info at didotech.com)
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

from openerp import models, fields, api, _
from openerp import SUPERUSER_ID
from openerp.exceptions import Warning


class res_partner(models.Model):
    _inherit = 'res.partner'

    property_supplier_ref = fields.Char(
        'Supplier Ref.', size=16,
        help="The reference attributed by the partner to the current company \
        as a supplier of theirs.")
    property_customer_ref = fields.Char(
        'Customer Ref.', size=16,
        help="The reference attributed by the partner to the current company \
        as a customer of theirs.")
    block_ref_customer = fields.Boolean('Block Reference')
    block_ref_supplier = fields.Boolean('Block Reference')
    selection_account_receivable = fields.Many2one(
        'account.account', 'Parent account', domain="[('type','=','view'),\
        ('user_type.code','=','account_type_view_assets')]")
    selection_account_payable = fields.Many2one(
        'account.account', 'Parent account', domain="[('type','=','view'),\
        ('user_type.code','=','account_type_view_liability')]")

    _sql_constraints = [
        ('property_supplier_ref', 'unique(property_supplier_ref)',
            'Codice Fornitore Univoco'),
        ('property_customer_ref', 'unique(property_customer_ref)',
            'Codice Cliente Univoco'),
    ]

    def _get_chart_template_property(
            self, cr, uid, property_chart=None, context=None):
        res = []
        chart_obj = self.pool['account.chart.template']
        chart_obj_ids = chart_obj.search(cr, SUPERUSER_ID, [])
        if len(chart_obj_ids) > 0:
            chart_templates = chart_obj.browse(
                cr, SUPERUSER_ID, chart_obj_ids, context)
            for chart_template in chart_templates:
                if property_chart:
                    property_chart_id = getattr(
                        chart_template, property_chart).id
                    # if it's not a view type code, it's a migration
                    if self.pool['account.account.template'].browse(
                            cr, SUPERUSER_ID,
                            property_chart_id).type != 'view':
                        continue
                    else:
                        res = property_chart_id
                        break
        if not res:
            raise Warning(_("Parent Account Type is not of type 'view'"))

        return res

    def get_create_supplier_partner_account(self, cr, uid, vals, context):
        return self.get_create_partner_account(
            cr, uid, vals, 'supplier', context)

    def get_create_customer_partner_account(self, cr, uid, vals, context):
        return self.get_create_partner_account(
            cr, uid, vals, 'customer', context)

    def get_create_partner_account(self, cr, uid, vals, account_type, context):
        account_obj = self.pool['account.account']
        account_type_obj = self.pool['account.account.type']

        if account_type == 'customer':
            property_account = 'property_account_receivable'
            type_account = 'receivable'
            property_ref = 'property_customer_ref'
        elif account_type == 'supplier':
            property_account = 'property_account_payable'
            type_account = 'payable'
            property_ref = 'property_supplier_ref'
        else:
            # Unknown account type
            return False

        if not vals.get(property_account, False):
            vals[property_account] = self._get_chart_template_property(
                cr, uid, property_account, context)

        property_account_id = vals.get(property_account, False)
        if property_account_id:
            property_account = account_obj.browse(
                cr, uid, property_account_id, context)

            account_ids = account_obj.search(
                cr, uid, [('code', '=', '{0}{1}'.format(
                    property_account.code, vals[property_ref]))])
            if account_ids:
                return account_ids[0]
            else:
                account_type_id = account_type_obj.search(
                    cr, uid, [('code', '=', type_account)], context=context)[0]

                return account_obj.create(cr, uid, {
                    'name': vals.get('name', ''),
                    'code': '{0}{1}'.format(
                        property_account.code, vals[property_ref]),
                    'user_type': account_type_id,
                    'type': type_account,
                    'parent_id': property_account_id,
                    'active': True,
                    'reconcile': True,
                    'currency_mode': property_account.currency_mode,
                }, context)
        else:
            return False

    @api.model
    def create(self, vals):
        company = self.env.user.company_id
        if not company.enable_partner_subaccount:
            return super(res_partner, self).create(vals)

        # 1 se marcato come cliente - inserire se non esiste
        if (vals.get('customer', False) or
            self._context.get('search_default_customer', False) or
            self._context.get('default_customer', False)) and not (
                vals.get('supplier', False) or
                self._context.get('search_default_supplier', False) or
                self._context.get('default_supplier', False)):
            vals['block_ref_customer'] = True
            if not vals.get('property_customer_ref', False):
                vals['property_customer_ref'] = self.pool['ir.sequence'].get(
                    self._cr, self._uid, 'SEQ_CUSTOMER_REF') or ''
            if vals.get('selection_account_receivable', False):
                vals['property_account_receivable'] = \
                    vals['selection_account_receivable']
            vals['property_account_receivable'] = \
                self.get_create_customer_partner_account(vals)

        # 2 se marcato come fornitore - inserire se non esiste
        if not (
            vals.get('customer', False) or
            self._context.get('search_default_customer', False) or
            self._context.get('default_customer', False)) and (
                vals.get('supplier', False) or
                self._context.get('search_default_supplier', False) or
                self._context.get('default_supplier', False)):
            vals['block_ref_supplier'] = True
            if not vals.get('property_supplier_ref', False):
                vals['property_supplier_ref'] = self.pool['ir.sequence'].get(
                    self._cr, self._uid, 'SEQ_SUPPLIER_REF') or ''
            if vals.get('selection_account_payable', False):
                vals['property_account_payable'] = \
                    vals['selection_account_payable']
            vals['property_account_payable'] = \
                self.get_create_supplier_partner_account(vals)

        # 3 se marcato come cliente e fornitore - inserire se non esiste
        if (vals.get('customer', False) or
            self._context.get('search_default_customer', False) or
            self._context.get('default_customer', False)) and (
                vals.get('supplier', False) or
                self._context.get('search_default_supplier', False) or
                self._context.get('default_supplier', False)):
            vals['block_ref_customer'] = True
            if not vals.get('property_customer_ref', False):
                vals['property_customer_ref'] = self.pool['ir.sequence'].get(
                    self._cr, self._uid, 'SEQ_CUSTOMER_REF') or ''
            vals['block_ref_supplier'] = True
            if not vals.get('property_supplier_ref', False):
                vals['property_supplier_ref'] = self.pool['ir.sequence'].get(
                    self._cr, self._uid, 'SEQ_SUPPLIER_REF') or ''
            if vals.get('selection_account_receivable', False):
                vals['property_account_receivable'] = \
                    vals['selection_account_receivable']
            if vals.get('selection_account_payable', False):
                vals['property_account_payable'] = \
                    vals['selection_account_payable']
            vals['property_account_receivable'] = \
                self.get_create_customer_partner_account(vals)
            vals['property_account_payable'] = \
                self.get_create_supplier_partner_account(vals)

        return super(res_partner, self).create(vals)

    def unlink(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        ids_account_payable = []
        ids_account_receivable = []
        for partner in self.pool['res.partner'].browse(cr, uid, ids, context):

            if partner.property_account_payable and \
                    partner.property_account_payable.type != 'view':
                if partner.property_account_payable.balance == 0.0:
                    ids_account_payable.append(
                        partner.property_account_payable.id)
                else:
                    ids.remove(partner.id)
            if partner.property_account_receivable and \
                    partner.property_account_receivable.type != 'view':
                if partner.property_account_receivable.balance == 0.0:
                    ids_account_receivable.append(
                        partner.property_account_receivable.id)
                else:
                    ids.remove(partner.id)

        res = super(res_partner, self).unlink(cr, uid, ids, context)
        ids_account = list(set(ids_account_payable + ids_account_receivable))

        if res and ids_account:
            self.pool['account.account'].unlink(
                cr, SUPERUSER_ID, ids_account, context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if not context:  # write is called from create, then skip
            context = {}
            return super(res_partner, self).write(
                cr, uid, ids, vals, context=context)
        company = self.pool['res.users'].browse(
            cr, uid, uid, context).company_id
        if not company.enable_partner_subaccount:
            return super(res_partner, self).write(
                cr, uid, ids, vals, context=context)
        if isinstance(ids, (int, long)):
            ids = [ids]
        account_obj = self.pool['account.account']
        if ids:
            partner = self.browse(cr, uid, ids[0], context)

            if partner.block_ref_customer or vals.get('customer', False):
                # already a customer or flagged as a customer
                vals['block_ref_customer'] = True
                if 'name' not in vals:
                    # if there isn't the name of partner - then it is not
                    # modified - so assign it
                    vals['name'] = partner.name

                if partner.property_account_receivable.type != 'view':
                    # there is already an account created for the partner
                    if partner.property_account_receivable.name \
                            != vals['name']:
                        # the account name if different from the partner name,
                        # so we must update the account name
                        account_obj.write(
                            cr, uid, partner.property_account_receivable.id,
                            {'name': vals['name']})
                else:
                    # the property_account_receivable is a view type,
                    # so we have to create the partner account
                    if 'property_customer_ref' not in vals:
                        # there isn't the partner code, so create it
                        vals['property_customer_ref'] = \
                            self.pool['ir.sequence'].get(
                                cr, uid, 'SEQ_CUSTOMER_REF') or ''
                    if vals.get('selection_account_receivable', False):
                        vals['property_account_receivable'] = \
                            vals['selection_account_receivable']
                    else:
                        vals['property_account_receivable'] = \
                            partner.property_account_receivable.id
                        # è il conto vista
                    vals['property_account_receivable'] = \
                        self.get_create_customer_partner_account(
                            cr, uid, vals, context)

            if partner.block_ref_supplier or vals.get('supplier', False):
                # already a supplier or flagged as a supplier
                vals['block_ref_supplier'] = True
                if 'name' not in vals:
                    vals['name'] = partner.name
                if partner.property_account_payable.type != 'view':
                    if partner.property_account_payable.name != vals['name']:
                        account_obj.write(
                            cr, uid, partner.property_account_payable.id,
                            {'name': vals['name']})
                else:
                    if 'property_supplier_ref' not in vals:
                        vals['property_supplier_ref'] = \
                            self.pool['ir.sequence'].get(
                                cr, uid, 'SEQ_SUPPLIER_REF') or ''
                    if vals.get('selection_account_payable', False):
                        vals['property_account_payable'] = \
                            vals['selection_account_payable']
                    else:
                        vals['property_account_payable'] = \
                            partner.property_account_payable.id
                    vals['property_account_payable'] = \
                        self.get_create_supplier_partner_account(
                            cr, uid, vals, context)

        return super(res_partner, self).write(
            cr, uid, ids, vals, context=context)

    def copy(self, cr, uid, partner_id, defaults, context=None):
        raise Warning(_('Duplication of a partner is not allowed'))
