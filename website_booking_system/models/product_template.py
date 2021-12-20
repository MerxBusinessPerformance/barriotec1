# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2016-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# License URL :<https://store.webkul.com/license.html/>
##########################################################################

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
from dateutil.relativedelta import relativedelta
from odoo.addons.website.models.website_snippet_filter import WebsiteSnippetFilter
import datetime, pytz

from .days import Days

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_booking_type = fields.Boolean("Available for booking")
    br_start_date = fields.Date("Start Date")
    br_end_date = fields.Date("End Date")
    max_bk_qty = fields.Integer("Max Booking Qty", default=0)
    booking_day_slot_ids = fields.One2many("day.slot.config", "product_id", string="Configure Day Slots")

    bk_rent_mode = fields.Selection(
        string='Mode',
        default='D',
        selection=[
            ('D', 'Daily'),
            ('P', 'Period')
        ]
    )
    booking_rom_num = fields.Char(
        string='Número de cuartos'
    )
    booking_floor = fields.Char(
        string='Piso'
    )
    booking_area = fields.Char(
        string='Vista del departamento'
    )
    booking_lookout_area = fields.Char(
        string='Área del balcón'
    )
    booking_lookout = fields.Boolean(
        string='Vista a Calle'
    )
    booking_plan_ids = fields.One2many(
        string='Plans',
        comodel_name='pgmx.booking.product.plans',
        inverse_name='product_id'
    )

    def get_available_bk_qty(self):
        for rec in self:
            context = dict(rec._context) or {}
            context['active_id'] = rec.id
            return {
                'name':'Booking Available Quantity',
                'type':'ir.actions.act_window',
                'res_model':'booking.quantity.wizard',
                'view_mode':'form',
                'view_id':rec.env.ref('website_booking_system.booking_available_quantity_wizard_form_view').id,
                'context' : context,
                'target':'new',
            }

    @api.model
    def get_bk_slot_available_qty(self, bk_date, slot_plan_id):
        """ Return: Total quantity available on a particular date in a provided slot.
            bk_date: Date on with quantity will be calculated.
            slot_plan_id: Plan in any slot on with quantity will be calculated."""
        slot_plan_obj = self.env["booking.slot"].browse([int(slot_plan_id)])
        sol_objs = slot_plan_obj.line_ids.filtered(lambda line: line.booking_date == bk_date).mapped('product_uom_qty')
        return slot_plan_obj.quantity - sum(sol_objs)

    def get_bk_open_closed_days(self, state):
        """State : State of the booking product(open/closed).
            Return: List of days of the week on the basis of state.
            e.g.-['mon','tue','sun']"""

        if self.bk_rent_mode != 'D':
            return list(Days.values())

        bk_open_days = self.booking_day_slot_ids.filtered(lambda day_sl: day_sl.booking_status == 'open' and len(day_sl.booking_slots_ids)).mapped('name')
        if state == 'open':
            return bk_open_days
        else:
            bk_closed_days = list(set(Days.values()) - set(bk_open_days))
            return bk_closed_days

    @api.model
    def get_available_day_slots(self, slots, sel_date):
        av_slots = []
        if sel_date and slots:
            rd = relativedelta(datetime.date.today(), sel_date)
            if rd.days == 0 and rd.months == 0 and rd.years == 0:
                for slot in slots:
                    start_time = slot.start_time
                    start_time = slot.float_convert_in_time(start_time)
                    current_time = datetime.datetime.now().replace(microsecond=0).replace(second=0)
                    user_tz = pytz.timezone(self.env.user.tz or 'UTC')
                    current_time = pytz.utc.localize(current_time).astimezone(user_tz)
                    hour = int(start_time.split(":")[0])
                    min = int(start_time.split(":")[1])
                    if hour > current_time.hour or (hour == current_time.hour and min > current_time.minute):
                        av_slots.append(slot)
                return av_slots
        return slots

    def get_booking_slot_for_day(self, sel_date):
        """Return: List of slots and their plans with qty and price of a day"""
        self.ensure_one()
        day = Days[sel_date.weekday()]
        day_config = self.booking_day_slot_ids.filtered(lambda day_sl: day_sl.name == day and day_sl.booking_status == 'open')
        day_slots = day_config.booking_slots_ids
        time_slots = day_slots.mapped('time_slot_id')
        time_slots = self.get_available_day_slots(time_slots, sel_date)
        slots_plans_list = []
        for slot in time_slots:
            d1 = {}
            d2 = []
            d1['slot'] = {
                'name' : slot.name_get()[0][1],
                'id' : slot.id,
            }
            d_slots = day_slots.filtered(lambda r: r.time_slot_id.id == slot.id)
            for d in d_slots:
                d2.append({
                    'name' : d.plan_id.name,
                    'id' : d.id,
                    'qty' : d.quantity,
                    'price' : d.price,
                })
            d1['plans'] = d2
            slots_plans_list.append(d1)
        return slots_plans_list

    def get_booking_onwards_price(self):
        """Return: Minimum price of a booking product available in any slot."""
        self.ensure_one()

        if self.bk_rent_mode == 'P':
            return self.list_price

        prices = sorted(self.booking_day_slot_ids.mapped('booking_slots_ids.price'))
        return prices[0] if prices else 0

    @api.onchange('br_start_date')
    def booking_start_date_validation(self):
        self.validate_booking_dates(start_date=self.br_start_date)

    @api.onchange('br_end_date')
    def booking_end_date_validation(self):
        self.validate_booking_dates(end_date=self.br_end_date)

    @api.onchange('is_booking_type')
    def update_product_type_for_booking(self):
        if self.is_booking_type:
            self.type = 'service'

    def validate_booking_dates(self, start_date=None, end_date=None):
        if type(start_date) == str:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        if type(end_date) == str:
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        current_date = fields.Date.today()
        if start_date and end_date:
            if start_date < current_date:
                raise UserError(_("Please enter start date correctly. Start date should't be smaller then the current date."))
            if end_date < start_date:
                raise UserError(_("Please enter end date correctly. End date should't be smaller then the start date."))
            return True
        if start_date:
            if start_date < current_date:
                raise UserError(_("Please enter start date correctly. Start date should't be smaller then the current date."))
            if self.br_end_date and start_date > self.br_end_date:
                raise UserError(_("Please enter start date correctly. Start date should't be greater then the end date."))
            return True
        if end_date:
            if end_date < current_date:
                raise UserError(_("Please enter end date correctly. End date should't be smaller then the current date."))
            if self.br_start_date and end_date < self.br_start_date:
                raise UserError(_("Please enter end date correctly. End date should't be smaller then the start date."))
            return True

    @api.model
    def create(self, vals):
        self.validate_booking_dates(vals.get("br_start_date"), vals.get("br_end_date"))
        return super(ProductTemplate, self).create(vals)

    def write(self, vals):
        for rec in self:
            rec.validate_booking_dates(vals.get("br_start_date"), vals.get("br_end_date"))
        return super(ProductTemplate, self).write(vals)

class WebsiteSnippetFilterInh(models.Model):
    _inherit = 'website.snippet.filter'

    def _prepare_values(self, limit=None, search_domain=None):
        res = super(WebsiteSnippetFilterInh, self)._prepare_values(limit, search_domain)

        for item in res:

            product_id = [value for field, value in item['fields'].items() if field == 'id']
            product = product_id and self.env['product.product'].browse(int(product_id[0]))

            if product:
                item.update({
                    'extra_fields': {
                        'booking_rom_num': product.booking_rom_num,
                        'booking_floor': product.booking_floor,
                        'booking_area': product.booking_area,
                        'booking_lookout_area': product.booking_lookout_area,
                        'booking_lookout': product.booking_lookout and 'Si' or 'No'
                    }
                })
            else:
                item.update({
                    'extra_fields': {
                        'booking_rom_num': False,
                        'booking_floor': False,
                        'booking_area': False,
                        'booking_lookout_area': False,
                        'booking_lookout': False
                    }
                })

        return res
