# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from . import models

import logging
from openerp import SUPERUSER_ID


def post_init_hook(cr, registry):
    account_journal_model = registry['account.journal']
    logging.getLogger('openerp.addons.l10n_it_account_ext').info(
        'Setting values for account.journal group_invoice_lines '
        'and update_posted')
    invoices_journal_ids = account_journal_model.search(cr, SUPERUSER_ID, [
        ('type', 'in', [
            'sale', 'sale_refund', 'purchase', 'purchase_refund', ]),
        ])
    account_journal_model.write(cr, SUPERUSER_ID, invoices_journal_ids, {
        'group_invoice_lines': True,
        'update_posted': True,
        })
    cash_bank_journal_ids = account_journal_model.search(cr, SUPERUSER_ID, [
        ('type', 'in', ['cash', 'bank', 'general', ]),
        ])
    account_journal_model.write(cr, SUPERUSER_ID, cash_bank_journal_ids, {
        'update_posted': True,
        'entry_posted': True,
        })
