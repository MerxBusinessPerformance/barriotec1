from odoo import api, fields, models, _

class Website(models.Model):
    _inherit = 'website'

    @api.model
    def bk_products_validation(self):
        """"Check any sold out product of booking type is in the cart or not."""
        order = self.sale_get_order()
        if order:
            order_lines = order.website_order_line
            for line in order_lines:
                product_obj = line.product_id.product_tmpl_id
                if product_obj.is_booking_type:
                    av_qty = product_obj.get_bk_slot_available_qty(
                        line.booking_date, line.booking_slot_id.id)
                    if av_qty < 0:
                        break
            else:
                return True
        return False
