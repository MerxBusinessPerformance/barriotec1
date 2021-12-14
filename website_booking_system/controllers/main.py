# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import api, http, tools, _
from odoo.http import request
from datetime import date, timedelta, datetime
from odoo.addons.website_sale.controllers.main import WebsiteSale

import ast
import json
import logging
_logger = logging.getLogger(__name__)

Days = {
    0: 'mon',
    1: 'tue',
    2: 'wed',
    3: 'thu',
    4: 'fri',
    5: 'sat',
    6: 'sun',
}


def diferencia_en_meses(d2, d1):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


class WebsiteSale(WebsiteSale):

    @http.route(['/booking/reservation/price_list_plus_plan'], type='json', auth="public", methods=['POST'], website=True)
    def price_list_plus_plan(self, **post):
        product_id = post.get('product_id', False)
        product_obj = request.env["product.template"].browse(int(product_id))

        resp = {

            'price': product_obj.list_price,
            'plans': [{
                'name': x.plan_id.name,
                'description': x.plan_id.discription
            } for x in product_obj.booking_plan_ids]

        }

        return resp

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, product_template_id, add_qty=1, set_qty=0, **kw):
        res = super(WebsiteSale, self).cart_update(
            product_id, add_qty, set_qty, **kw)
        bk_plan = kw.get('bk_plan', False)
        bk_date = kw.get('bk_date', False)
        bk_date_out = kw.get('bk_date_out', False)

        if bk_plan:
            product_obj = request.env['product.template'].browse(
                int(product_template_id))
            from_date = datetime.strptime(bk_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(bk_date_out, '%Y-%m-%d').date()

            month_diff = diferencia_en_meses(from_date, to_date)
            month_price = product_obj.list_price

            # if product_obj.bk_rent_mode == 'P':
            bk_slot_obj = request.env["pgmx.booking.product.plans"].browse([
                                                                           int(bk_plan)])
            line_values = {
                'booking_plan_line_id': bk_slot_obj.id,
                'price_unit': month_price + bk_slot_obj.price,
                'booking_date': bk_date,
                'booking_date_out': bk_date_out,
                'booked_plan_id': bk_slot_obj.id,
                'product_uom_qty': month_diff,
                'booking_plan_price': bk_slot_obj.price,
                'booking_base_price': month_price,
            }

            sale_order = request.website.sale_get_order()
            order_line = sale_order.order_line.filtered(
                lambda l: l.product_id.id == int(product_id))
            order_line.write(line_values)
            sale_order.write({
                'is_booking_type': True,
            })

        return res

    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):

        check = request.website.bk_products_validation()
        if not check:
            return request.redirect("/shop/cart")
        return super(WebsiteSale, self).checkout(**post)

    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        check = request.website.bk_products_validation()
        if not check:
            return request.redirect("/shop/cart")
        order = request.website.sale_get_order()
        if order:
            order.payment_start_date = datetime.now()
        return super(WebsiteSale, self).payment(**post)

    '''
    Esta función se sobrescribe para que no modifique el price_list que tiene
    el carrito y este se refleje igual en la sales order. 
    '''
    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True, sitemap=False)
    def confirm_order(self, **post):
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(
            order) or self.checkout_check_address(order)
        if redirection:
            return redirection
        order.onchange_partner_shipping_id()
        order.order_line._compute_tax_id()
        request.session['sale_last_order_id'] = order.id
        # Esta es la linea que eliminamos.
        # request.website.sale_get_order(update_pricelist=false)
        extra_step = request.website.viewref('website_sale.extra_info_option')
        if extra_step.active:
            return request.redirect("/shop/extra_info")
        return request.redirect("/shop/payment")


class BookingReservation(http.Controller):

    def get_all_week_days(self, sel_date, product_obj):
        """Return all week day,date list for the selected date"""
        bk_open_days = product_obj.get_bk_open_closed_days("open")
        if not bk_open_days:
            return False
        week_days = [None]*7
        end_date = product_obj.br_end_date or datetime.today().date() + \
            timedelta(days=30)
        current_date = self.get_default_date(product_obj.id)
        day = sel_date.weekday()
        v_date = sel_date - timedelta(days=day)
        for w_day in week_days:
            day = v_date.weekday()
            week_days[day] = {
                "day": Days[day],
                "date_str": datetime.strftime(v_date, '%d %b %Y'),
                "date": datetime.strftime(v_date, '%Y-%m-%d'),
                "state": "active" if current_date <= v_date and v_date <= end_date and Days[day] in bk_open_days else "inactive",
            }
            v_date = v_date + timedelta(days=1)
        return week_days

    # Update slots on week day selection

    # @http.route(['/booking/reservation/update/slots'], type='json', auth="public", methods=['POST'], website=True)
    # def booking_reservation_update_slots(self, **post):
    #     w_day = post.get('w_day', False)
    #     w_date = post.get('w_date', False)
    #     w_date = datetime.strptime(w_date, '%Y-%m-%d').date()
    #     product_id = post.get('product_id', False)
    #     if not product_id:
    #         return False
    #     product_obj = request.env["product.template"].browse(product_id)
    #     current_day_slots = product_obj.get_booking_slot_for_day(w_date)
    #     values = {
    #         'day_slots': current_day_slots,
    #         'current_date': w_date,
    #         'product': product_obj,
    #     }
    #     return request.env.ref("website_booking_system.booking_modal_bk_slots_n_plans_div")._render(values, engine='ir.qweb')

    # # Update plans on slot selection
    # @http.route(['/booking/reservation/slot/plans'], type='json', auth="public", methods=['POST'], website=True)
    # def booking_reservation_slot_plans(self, **post):
    #     sel_date = post.get('sel_date', False)
    #     sel_date = datetime.strptime(sel_date, '%Y-%m-%d').date()
    #     time_slot_id = post.get('time_slot_id', False)
    #     slot_plans = post.get('slot_plans', False)
    #     product_id = post.get('product_id', False)
    #     product_obj = request.env["product.template"].browse(product_id)
    #     slot_plans = ast.literal_eval(slot_plans)
    #     values = {
    #         'd_plans': slot_plans,
    #         'current_date': sel_date,
    #         'product': product_obj,
    #     }
    #     return request.env.ref("website_booking_system.booking_sel_plans")._render(values, engine='ir.qweb')

    def get_default_date(self, product_id):
        product_obj = request.env["product.template"].browse(product_id)
        w_open_days = product_obj.get_bk_open_closed_days("open")
        if not w_open_days:
            return False
        current_date = date.today()

        if product_obj.bk_rent_mode != 'D':
            return current_date

        start_date = product_obj.br_start_date
        end_date = product_obj.br_end_date
        if end_date < current_date:
            return False
        elif current_date < start_date:
            current_date = start_date
        current_day = Days[current_date.weekday()]
        if current_day in w_open_days:
            return current_date
        while(current_day not in w_open_days):
            current_date = current_date + timedelta(days=1)
            current_day = Days[current_date.weekday()]
            if end_date < current_date:
                return False
        return current_date

    # Append booking Pop-Up modal
    @http.route(['/booking/reservation/modal'], type='json', auth="public", methods=['POST'], website=True)
    def booking_reservation_modal(self, **post):
        product_id = post.get('product_id', False)
        if not product_id:
            return False
        product_obj = request.env["product.template"].browse(product_id)

        values = {
            'booking_status': False
        }

        if product_obj.bk_rent_mode != 'D':
            current_date = date.today()
            end_date = product_obj.br_end_date
            values.update({
                'booking_status': True,
                'daily_mode': 0,
                'product': product_obj,
                'current_date': current_date,
                'end_date': current_date > end_date and current_date or end_date,
                'default_date': current_date,
                'plans': [{
                    'name': pl.plan_id.name,
                    'id': pl.id,
                    'qty': 1,
                    'price': pl.price,
                } for pl in product_obj.booking_plan_ids]
            })

            return request.env.ref("website_booking_system.booking_and_reservation_rent_mode_modal_temp")._render(values, engine='ir.qweb')

        current_date = self.get_default_date(product_id)
        if current_date:
            week_days = self.get_all_week_days(current_date, product_obj)
            current_day = Days[current_date.weekday()]
            end_date = product_obj.br_end_date
            current_day_slots = product_obj.get_booking_slot_for_day(
                current_date)
            w_closed_days = product_obj.get_bk_open_closed_days("closed")
            values.update({
                'booking_status': True,
                'daily_mode': 1,
                'product': product_obj,
                'week_days': week_days,
                'w_closed_days': json.dumps(w_closed_days),
                'current_day': current_day,
                'current_date': current_date,
                'day_slots': current_day_slots,
                'end_date': end_date,
                'default_date': current_date,
            })

        return request.env.ref("website_booking_system.booking_and_reservation_modal_temp")._render(values, engine='ir.qweb')

    # Update booking modal on date selection
    @http.route(['/booking/reservation/modal/update'], type='json', auth="public", methods=['POST'], website=True)
    def booking_reservation_modal_update(self, **post):
        product_id = post.get('product_id', False)
        new_date = post.get('new_date', False)
        if not product_id:
            return False
        product_obj = request.env["product.template"].browse(product_id)
        new_date = datetime.strptime(new_date, '%d/%m/%Y').date()
        end_date = product_obj.br_end_date

        week_days = self.get_all_week_days(new_date, product_obj)
        current_day = Days[new_date.weekday()]
        current_day_slots = product_obj.get_booking_slot_for_day(new_date)

        values = {
            'product': product_obj,
            'week_days': week_days if week_days else [],
            'current_day': current_day,
            'current_date': new_date,
            'day_slots': current_day_slots,
            'end_date': end_date,
        }
        return request.env.ref("website_booking_system.booking_modal_bk_slots_main_div")._render(values, engine='ir.qweb')

    # Update booking modal on date selection
    @http.route(['/booking/reservation/modal/update_price'], type='json', auth="public", methods=['POST'], website=True)
    def booking_reservation_modal_update_price(self, **post):
        product_id = post.get('product_id', False)
        str_from_date = post.get('from_date', False)
        str_to_date = post.get('to_date', False)
        plan_price = post.get('plan_proce', 0)
        if not product_id:
            return {}

        product_obj = request.env["product.template"].browse(product_id)
        from_date = datetime.strptime(str_from_date, '%d/%m/%Y').date()
        to_date = datetime.strptime(str_to_date, '%d/%m/%Y').date()
        month_diff = diferencia_en_meses(from_date, to_date)

        if month_diff <= 0:
            return {
                'price': 0
            }

        day_price = product_obj.list_price

        return {
            'price': (day_price + plan_price) * month_diff
        }

    @http.route(['/booking/reservation/cart/validate'], type='json', auth="public", methods=['POST'], website=True)
    def booking_reservation_cart_validate(self, **post):
        product_id = post.get('product_id', False)
        sale_order = request.website.sale_get_order()
        if sale_order:
            order_line = sale_order.order_line.filtered(
                lambda l: l.product_id.product_tmpl_id.id == int(product_id))
            return False if len(order_line) else True
        return True
