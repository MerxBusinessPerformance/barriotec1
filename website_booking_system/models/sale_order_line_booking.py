from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
from dateutil.relativedelta import relativedelta
import datetime
import pytz
from .days import Days


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    booking_slot_id = fields.Many2one("booking.slot", string="Booking Slot")
    booking_date = fields.Date(string="Booking Date")
    booking_date_out = fields.Date(string="Booking Out Date")
    booking_plan_price = fields.Float(string="Plan price")
    booking_base_price = fields.Float(string="Base price")
    booked_slot_id = fields.Many2one(
        related="booking_slot_id.time_slot_id", string="Booked Slot", store=True)
    booked_plan_id = fields.Many2one(
        related="booking_slot_id.plan_id", string="Booked Plan", store=True)
    booking_plan_line_id = fields.Many2one(
        string='Plan',
        comodel_name='pgmx.booking.product.plans'
    )

    @api.depends('product_id', 'booking_date', 'booking_slot_id')
    def compute_booking_line_name(self):
        for rec in self:
            rec.name = 'Hola mundo'
            product_obj = rec.product_id or False
            if product_obj and product_obj.is_booking_type:
                name = "Booking for " + product_obj.name
                if rec.booking_date:
                    name += " on " + str(rec.booking_date)
                if rec.booking_slot_id:
                    name += " (" + rec.booking_slot_id.name_get()[0][1] + ")"
                rec.name = name
        return

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        product_obj = res.product_id or False
        if product_obj and product_obj.is_booking_type:
            res.compute_booking_line_name()
        return res

    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        if vals.get('booking_date') or vals.get('booking_slot_id') or vals.get('product_id'):
            self.compute_booking_line_name()
        return res

    @api.onchange('product_id', 'booking_date', 'booking_slot_id')
    def booking_values_change(self):
        for rec in self:
            rec.compute_booking_line_name()
        return

    @api.onchange('booking_date')
    def is_booking_date_valid(self):
        for rec in self:
            if rec.booking_date:
                if not rec.product_id:
                    raise UserError(
                        _('Primero selecciona un producto para continuar.'))
                if not (rec.booking_date >= rec.product_id.br_start_date and rec.booking_date <= rec.product_id.br_end_date):
                    rec.booking_date = None
                    raise UserError(_('La fecha de booking debe estar entre %s y %s' % (
                        rec.product_id.br_start_date, rec.product_id.br_end_date)))
                day = rec.booking_date.weekday()
                # day_valid = rec.product_id.booking_day_slot_ids.filtered(
                #     lambda o: o.name == Days[int(day)] and o.booking_status == 'open')
                # if len(day_valid) == 0:
                #     raise UserError(
                #         _('Booking is closed on this day, please select a different date.'))
                if rec.product_uom_qty and rec.booking_slot_id:
                    avl_qty = rec.product_id.product_tmpl_id.get_bk_slot_available_qty(
                        rec.booking_date, rec.booking_slot_id.id)
                    if avl_qty < 1:
                        rec.booking_slot_id = None
                        raise UserError(
                            _("No quantity available for the selected slot, please select a different slot."))
                    if rec.product_uom_qty > avl_qty:
                        raise UserError(_('Available quantity on %s for %s(%s) is %s' % (
                            rec.booking_date, rec.booking_slot_id.time_slot_id.name_get()[0][1], rec.booking_slot_id.plan_id.name, avl_qty)))
                # domain = [('slot_config_id', '=', day_valid.id)]
                # return {
                #     'domain': {'booking_slot_id': domain}
                # }

    @api.onchange('booking_slot_id', 'product_uom_qty')
    def onchange_quantity_available(self):
        for rec in self:
            # if not rec.booking_date or not rec.product_id:
            #     raise UserError(_('Please first select the product and booking date then proceed further.'))
            if rec.product_uom_qty and rec.booking_slot_id:
                avl_qty = rec.product_id.product_tmpl_id.get_bk_slot_available_qty(
                    rec.booking_date, rec.booking_slot_id.id)
                if avl_qty < 1:
                    rec.booking_slot_id = None
                    raise UserError(
                        _("No quantity available for the selected slot, please select a different slot."))
                if rec.product_uom_qty > avl_qty:
                    raise UserError(_('Available quantity on %s for %s(%s) is %s' % (
                        rec.booking_date, rec.booking_slot_id.time_slot_id.name_get()[0][1], rec.booking_slot_id.plan_id.name, avl_qty)))
            if rec.booking_slot_id:
                rec.price_unit = rec.booking_slot_id.price

    def _get_display_price(self, product):
        for rec in self:
            if rec.booking_slot_id:
                return rec.booking_slot_id.with_context(pricelist=self.order_id.pricelist_id.id).price
        return super(SaleOrderLine, self)._get_display_price(product)

    @api.model
    def remove_booking_product_draft_order_lines(self):
        bk_orders = self.search(
            [('state', '=', 'draft'), ('booking_slot_id', '!=', None)])
        for so in bk_orders:
            sale_order = so.order_id
            payment_start_date = sale_order.payment_start_date
            rd = relativedelta(datetime.datetime.now(), so.create_date)
            if not payment_start_date:
                if rd.minutes > 5:
                    so.unlink()
            else:
                prd = relativedelta(
                    datetime.datetime.now(), payment_start_date)
                if prd.minutes > 10:
                    if not sale_order.check_active_bk_transactions():
                        so.unlink()
                        sale_order.compute_booking_type()
                        if not sale_order.is_booking_type:
                            sale_order.payment_start_date = None
