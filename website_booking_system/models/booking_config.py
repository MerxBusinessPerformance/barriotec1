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

import math
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

Days = [
    ('sun','Sunday'),
    ('mon','Monday'),
    ('tue','Tuesday'),
    ('wed','Wednesday'),
    ('thu','Thursday'),
    ('fri','Friday'),
    ('sat','Saturday'),
]

class BookingPlan(models.Model):
    _name = "booking.plan"
    _description = "Booking Plan"

    name = fields.Char(string="Name", required=True)
    discription = fields.Html(string="Description", help="Booking plan description.")
    sequence = fields.Integer(help="Determine the display order", default=1)

    _sql_constraints = [
        ('booking_plan_uniq', 'unique(name)', _('This booking plan is already exist!'))
    ]

class BookingTimeSlot(models.Model):
    _name = "booking.time.slot"
    _description = "Booking Time Slot"

    sequence = fields.Integer(help="Determine the display order", default=1)
    start_time = fields.Float(string="Start Time", required=True, help="Enter slot start time.")
    end_time = fields.Float(string="End Time", required=True, help="Enter slot end time.")

    # SQL Constraints
    _sql_constraints = [
        ('booking_time_slot_uniq', 'unique(start_time, end_time)', _('This time slot is already exist.'))
    ]

    def float_convert_in_time(self, float_val):
        """Convert any float value in 24 hrs time formate."""
        if float_val < 0:
            float_val = abs(float_val)
        hour = math.floor(float_val)
        min = round((float_val % 1) * 60)
        if min == 60:
            min = 0
            hour = hour + 1
        time = str(hour).zfill(2) + ":" + str(min).zfill(2)
        return time

    def time_convert_in_float(self, time_val):
        """Convert any 24 hrs time fomate value in float."""
        factor = 1;
        if time_val[0] == '-':
            time_val = time_val[1:]
            factor = -1
        float_time_pair = time_val.split(":")
        if len(float_time_pair) != 2:
            return factor*float(time_val)
        hours = int(float_time_pair[0])
        minutes = int(float_time_pair[1])
        return factor * round((hours + (minutes / 60)),2)

    def name_get(self):
        """Return: [(id, start_time-end_time)],
            e.g-[(1, 1:00-3:00)]"""
        result = []
        for rec in self:
            name = self.float_convert_in_time(rec.start_time) + '-' + self.float_convert_in_time(rec.end_time)
            result.append((rec.id, name))
        return result

    def check_time_values(self, vals):
        start_time = vals.get('start_time') if vals.get('start_time', None) != None else self.start_time
        end_time = vals.get('end_time') if vals.get('end_time', None) != None else self.end_time
        if start_time >= 24 or start_time < 0:
            raise UserError(_("Please enter a valid hour between 00:00 and 24:00"))
        if end_time >= 24 or end_time < 0:
            raise UserError(_("Please enter a valid hour between 00:00 and 24:00"))
        if start_time >= end_time:
            raise UserError(_("Please enter a valid start and end time."))
        same_objs = self.search([('start_time','=',start_time),('end_time','=',end_time)])
        if len(same_objs.ids) > 0:
            raise UserError(_("Record already exist with same timing."))

    @api.model
    def create(self, vals):
        self.check_time_values(vals)
        res = super(BookingTimeSlot, self).create(vals)
        return res

    def write(self, vals):
        if vals.get('start_time', None) != None and vals.get('end_time', None) != None:
            self.check_time_values(vals)
        elif vals.get('start_time', None) != None or vals.get('end_time', None) != None:
            for rec in self:
                rec.check_time_values(vals)
        res = super(BookingTimeSlot, self).write(vals)
        return res

class BookingSlotConfig(models.Model):
    _name = "day.slot.config"
    _description = "Day Slot Configuration"

    name = fields.Selection(selection=Days, string="Day", required=True)
    booking_status = fields.Selection(selection=[('open','Open'),('closed','Closed')], string="Status(Closed/Open)", required=True, help="Select booking status for the day(Closed/Open).", default="open")
    booking_slots_ids = fields.One2many("booking.slot", "slot_config_id", string="Booking Slots", help="Add booking slots for the day.")
    product_id = fields.Many2one("product.template", string="Product")

    # SQL Constraints
    _sql_constraints = [
        ('booking_day_uniq', 'unique(name, product_id)', _("Record already exist, you can't create multiple records for the same day."))
    ]

class BookingSlot(models.Model):
    _name = "booking.slot"
    _description = "Booking Slot"

    time_slot_id = fields.Many2one("booking.time.slot", required=True, string="Time Slot")
    plan_id = fields.Many2one("booking.plan", required=True, string="Booking Plan")
    quantity = fields.Integer(string="Quantity")
    price = fields.Float(string="Price", required=True)
    slot_config_id = fields.Many2one("day.slot.config", string="Day Slot Config")
    line_ids = fields.One2many("sale.order.line", "booking_slot_id", string="Booking Orders")

    @api.model
    def create(self,vals):
        time_slot = vals.get('time_slot_id')
        plan_id = vals.get('plan_id')
        saved_data = self.env['booking.slot'].search([('slot_config_id','=',vals.get('slot_config_id')),('time_slot_id','=',time_slot),('plan_id','=',plan_id)])
        if len(saved_data)>0:
            raise UserError(_('Record already exist for the selected booking slot & plan.'))
        return super(BookingSlot,self).create(vals)

    def name_get(self):
        result = []
        for rec in self:
            name = rec.time_slot_id.name_get()[0][1] + ',' + rec.plan_id.name
            result.append((rec.id, name))
        return result

    def _check_unique_slot_plan(self, context=None):
        for rec in self:
            recs = self.search_count([('time_slot_id', '=', rec.time_slot_id.id), ('plan_id', '=', rec.plan_id.id), ('slot_config_id', '=', rec.slot_config_id.id)])
            if recs > 1:
                return False
            return True

    # SQL Constraints
    _sql_constraints = [
        ('_check_unique_slot_plan', 'unique(time_slot_id, plan_id, slot_config_id)', _("This booking slot is already exist."))
    ]

    @api.onchange('time_slot_id','plan_id')
    def validate_slot_plan(self):
        for rec in self:
            if rec.time_slot_id and rec.plan_id:
                unique_records = rec.slot_config_id.booking_slots_ids
                if not rec._origin:
                    unique_records = unique_records - rec
                cur_rec = unique_records.filtered(lambda o:o.time_slot_id.id == rec.time_slot_id.id and o.plan_id.id == rec.plan_id.id)
                if len(cur_rec) > 1:
                    raise UserError(_("Record already exist with same time slot and plan."))

class BookingConfig(models.Model):
    _name = "booking.config"
    _description = "Booking Configuration"

    day = fields.Selection(selection=Days, string="Day")
    start_time = fields.Float("Start Time")
    end_time = fields.Float("End Time")
    time_slot = fields.Integer("Slot time duration")
    buffer_cache = fields.Integer("Buffer cache time after each booking")
    br_start_time = fields.Float("Break Start Time")
    br_end_time = fields.Float("Break End Time")
    product_id = fields.Many2one("product.template", string="Bookng Product")
