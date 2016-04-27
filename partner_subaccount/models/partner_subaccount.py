# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class ResPartner(models.Model):
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

    @api.one
    def _get_chart_template_property(self, property_chart=None):
        res = []
        chart_obj = self.env['account.chart.template']
        chart_obj_ids = chart_obj.sudo().search([])
        if len(chart_obj_ids) > 0:
            chart_templates = chart_obj.sudo().browse(chart_obj_ids)
            for chart_template in chart_templates:
                if property_chart:
                    property_chart_id = getattr(
                        chart_template, property_chart).id
                    # if it's not a view type code, it's a migration
                    if self.env['account.account.template'].sudo().browse(
                            property_chart_id).type != 'view':
                        continue
                    else:
                        res = property_chart_id
                        break
        if not res:
            raise Warning(_("Parent Account Type is not of type 'view'"))

        return res

    @api.multi
    def get_create_supplier_partner_account(self, vals):
        return self.get_create_partner_account(vals, 'supplier')

    @api.multi
    def get_create_customer_partner_account(self, vals):
        return self.get_create_partner_account(
            vals, 'customer')

    @api.multi
    def get_create_partner_account(self, vals, account_type):
        account_obj = self.env['account.account']
        account_type_obj = self.env['account.account.type']

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
                property_account)

        property_account_id = vals.get(property_account, False)
        if property_account_id:
            property_account = account_obj.browse(property_account_id)
            account_ids = account_obj.search(
                [('code', '=', '{0}{1}'.format(
                    property_account.code, vals[property_ref]))])
            if account_ids:
                return account_ids[0]
            else:
                account_type_id = account_type_obj.search(
                    [('code', '=', type_account)])[0]

                return account_obj.create({
                    'name': vals.get('name', ''),
                    'code': '{0}{1}'.format(
                        property_account.code, vals[property_ref]),
                    'user_type': account_type_id.id,
                    'type': type_account,
                    'parent_id': property_account_id,
                    'active': True,
                    'reconcile': True,
                    'currency_mode': property_account.currency_mode,
                })
        else:
            return False

    @api.model
    def create(self, vals):
        company = self.env.user.company_id
        if not company.enable_partner_subaccount:
            return super(ResPartner, self).create(vals)

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

        return super(ResPartner, self).create(vals)

    @api.multi
    def unlink(self):
        ids_account_payable = []
        ids_account_receivable = []
        for partner in self:
            if partner.property_account_payable and \
                    partner.property_account_payable.type != 'view':
                if partner.property_account_payable.balance == 0.0:
                    ids_account_payable.append(
                        partner.property_account_payable.id)
                else:
                    self.remove(partner)
            if partner.property_account_receivable and \
                    partner.property_account_receivable.type != 'view':
                if partner.property_account_receivable.balance == 0.0:
                    ids_account_receivable.append(
                        partner.property_account_receivable.id)
                else:
                    self.remove(partner)

        res = super(ResPartner, self).unlink()
        ids_account = list(set(ids_account_payable + ids_account_receivable))

        if res and ids_account:
            self.env['account.account'].sudo().browse(ids_account).unlink()
        return res

    @api.multi
    def write(self, vals):
        # write is called from create, then skip
        if not self._context or vals.get('child_ids', False):
            return super(ResPartner, self).write(vals)
        company = self.env.user.company_id
        for partner in self:
            if not company.enable_partner_subaccount or not partner.is_company:
                continue
            if partner.block_ref_customer or vals.get('customer', False):
                vals['block_ref_customer'] = True
                if 'name' not in vals:
                    vals['name'] = partner.name
                # if there is already an account we update account name
                if partner.property_account_receivable.type != 'view':
                    if partner.property_account_receivable.name \
                            != vals['name']:
                        partner.property_account_receivable.name = vals['name']
                else:  # view type so create partner account
                    if 'property_customer_ref' not in vals:
                        vals['property_customer_ref'] = \
                            self.env['ir.sequence'].get(
                                'SEQ_CUSTOMER_REF') or ''
                    if vals.get('selection_account_receivable', False):
                        vals['property_account_receivable'] = \
                            vals['selection_account_receivable']
                    else:
                        vals['property_account_receivable'] = \
                            partner.property_account_receivable.id
                        # è il conto vista
                    vals['property_account_receivable'] = \
                        self.get_create_customer_partner_account(vals)

            if partner.block_ref_supplier or vals.get('supplier', False):
                # already a supplier or flagged as a supplier
                vals['block_ref_supplier'] = True
                if 'name' not in vals:
                    vals['name'] = partner.name
                if partner.property_account_payable.type != 'view':
                    if partner.property_account_payable.name != vals['name']:
                        partner.property_account_payable.name = vals['name']
                else:
                    if 'property_supplier_ref' not in vals:
                        vals['property_supplier_ref'] = \
                            self.env['ir.sequence'].get(
                                'SEQ_SUPPLIER_REF') or ''
                    if vals.get('selection_account_payable', False):
                        vals['property_account_payable'] = \
                            vals['selection_account_payable']
                    else:
                        vals['property_account_payable'] = \
                            partner.property_account_payable.id
                    vals['property_account_payable'] = \
                        self.get_create_supplier_partner_account(vals)

        return super(ResPartner, self).write(vals)

    @api.one
    def copy(self, default=None):
        raise Warning(_('Duplication of a partner is not allowed'))
