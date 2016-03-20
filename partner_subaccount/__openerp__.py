# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 SimplERP srl (<http://www.simplerp.it>).
#    Copyright (c) 2013-2014 Didotech SRL (info at didotech.com)
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

{
    'name': 'Create account for partner',
    'version': '8.1.0.6.2',
    'category': 'Generic Modules',
    'website': 'https://www.simplerp.it',
    "author": "Didotech SRL, Sergio Corato - SimplERP Srl",
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ref_sequences.xml',
        'views/partner_subaccount_view.xml',
        'views/company_view.xml',
        'views/partner_view.xml',
    ],
    'test': [
        'test/partner_create_modify.yml',
    ],
    'installable': True,
}
