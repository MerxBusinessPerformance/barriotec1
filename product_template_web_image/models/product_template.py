# Copyright 2021 Munin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.tools.image import image_data_uri


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    extra_image = fields.Binary(string="Extra Image", copy=False)

    extra_image_data_uri = fields.Char('Base 64 image', copy=False, compute="_compute_extra_image_base64", store=True)

    @api.depends('extra_image')
    def _compute_extra_image_base64(self):
        for record in self:
            record.extra_image_data_uri = record.extra_image and image_data_uri(record.extra_image)
