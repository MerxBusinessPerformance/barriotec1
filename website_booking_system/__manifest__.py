# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
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
{
  "name"                 :  "Odoo Booking & Reservation Management",
  "summary"              :  """Booking & reservation management in Odoo allows users to take appointment and ticket booking facility in Odoo website.""",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Booking-Reservation-Management.html",
  "description"          :  """Odoo booking & reservation management
        Odoo Subscription Management
        Odoo Website Subscription Management
        Odoo appointment management
        Odoo website Appointment Management
        Schedule bookings
        Tickets
        Reservations
        Booking Facility in Odoo
        Website booking system
        Appointment management system in Odoo
        Booking & reservation management in Odoo
        Reservation management in Odoo
        Booking
        Reservation
        Booking and reservation""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=website_booking_system&custom_url=/shop",
  "depends"              :  ['website_sale'],
  "data"                 :  [
                             'security/ir.model.access.csv',
        'views/pgmx_booking_product_plans.xml',
                             'views/booking_config_view.xml',
                             'views/booking_sol_view.xml',
                             'wizard/bk_qty_available_wizard_view.xml',
                             'views/product_template_view.xml',
                             'views/booking_product_cart_temp.xml',
                             'views/booking_template.xml',
                             'views/snnipets.xml',
                             'views/ir_crons.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  149,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
