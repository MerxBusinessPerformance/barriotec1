from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_booking_type = fields.Boolean(string="Booking Order")
    payment_start_date = fields.Datetime("Payment initiated time")
    plan = fields.Char(
        string="Booked Plan", store=True)

    partner_invoice_id = fields.Many2one(
        'res.partner', string='Invoice Address',
        readonly=True, required=False,
        states={'draft': [('readonly', False)], 'sent': [
            ('readonly', False)], 'sale': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Delivery Address', readonly=True, required=False,
        states={'draft': [('readonly', False)], 'sent': [
            ('readonly', False)], 'sale': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)

    def check_active_bk_transactions(self):
        self.ensure_one()
        active_trans = self.transaction_ids.filtered(
            lambda l: l.state in ['pending', 'authorized', 'done'])
        if active_trans:
            return True
        return False

    @api.onchange('order_line')
    def compute_booking_type(self):
        for rec in self:
            if rec.order_line:
                if any(line.product_id.is_booking_type == True for line in rec.order_line):
                    rec.is_booking_type = True
