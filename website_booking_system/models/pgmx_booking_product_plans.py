# -*- coding: utf-8 -*-
# © <2021> <otorresmx (otorres@proogeeks.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

class PgmxBookingProductPlans(models.Model):
    _name = 'pgmx.booking.product.plans'
    _description = 'PGMX BOOKING PRODUCT PLANS'

    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.template'
    )
    plan_id = fields.Many2one(
        string='Plan',
        comodel_name='booking.plan'
    )
    price = fields.Float(
        string='Precio'
    )