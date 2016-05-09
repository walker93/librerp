# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    sale_journal_id = fields.Many2one(
        'account.journal', 'Default Sale Journal')
    purchase_journal_id = fields.Many2one(
        'account.journal', 'Default Purchase Journal')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('fiscal_position')
    def change_journal(self):
        if self.type in ['out_invoice']:
            self.journal_id = self.fiscal_position.sale_journal_id or False
        elif self.type in ['in_invoice']:
            self.journal_id = self.fiscal_position.purchase_journal_id or False
