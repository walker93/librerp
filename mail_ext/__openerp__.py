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
{
    'name': 'mail_ext',
    'version': '4.0.0.0',
    'category': 'Social Network',
    'description': """
Fix mail:
- delete access link
- delete sent by footer
""",
    'author': 'Ivan Yelizariev, SimplERP srl',
    'website': 'https://yelizariev.github.io, http://www.simplerp.it',
    'license': 'AGPL-3',
    "depends": [
        'mail',
    ],
    "data": [
        'views/mail_sent_views.xml',
    ],
    "active": False,
    "installable": True
}
