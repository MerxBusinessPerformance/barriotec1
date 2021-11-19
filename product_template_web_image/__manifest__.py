# Copyright 2021 Munin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product Template Web Image',
    'description': """
        agregar campos en product template para usar en website""",
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Munin',
    'depends': [
        'website_sale'
    ],
    'data': [
        'views/product_template.xml',
    ],
    'demo': [
    ],
}
