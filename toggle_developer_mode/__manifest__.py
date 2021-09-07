# -*- coding: utf-8 -*-
##############################################################################
#
#    Part of cube48.de. See LICENSE file for full copyright and licensing details.
#
##############################################################################
{
    'name': "Toggle Debug Mode",

    'summary': """
        Toggle to debug mode in the top right user menu, just one click!""",

    'description': """
        Toggle to debug mode in the top right user menu, just one click!

    """,

    'author': "cube48 AG",
    'website': "https://www.cube48.de",
    'category': 'Tools',
    'version': '14.0',
    'depends': [
        'base',
    ],
    'data': [
        'views/views.xml',
    ],
    'qweb': ['static/src/xml/base.xml'],
    'images': ["static/description/banner.png"],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
}
