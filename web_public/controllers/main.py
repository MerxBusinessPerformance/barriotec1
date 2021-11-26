from odoo import http
import json


class OdooController(http.Controller):

    def log_in(self):
        http.request.session.authenticate("test", "web", "12345")

    def log_out(self):
        http.request.session.logout(keep_db=True)

    def cargarDiccionario(self, productos):

        productos_dict = {
            'skus': []
        }

        for producto in productos:

            d = {
                "name": producto.name,
                # "categ_id": producto.categ_id,
                "booking_rom_num": producto.booking_rom_num,
                "booking_floor": producto.booking_floor,
                "booking_area": producto.booking_area,
                "booking_lookout_area": producto.booking_lookout_area,

                # ------------------------------
                "is_booking_type": producto.is_booking_type,
                "website_url": producto.website_url,
                # "booking_plan_ids": producto.booking_plan_ids,
                # "product_template_image_ids": producto.product_template_image_ids,
                # "image_1024": producto.image_1024,
                "description": producto.description,
                # "cost_currency_id": producto.cost_currency_id,
                "booking_area": producto.booking_area,
                "booking_lookout_area": producto.booking_lookout_area,
                "booking_rom_num": producto.booking_rom_num,
                "extra_image_data_uri": producto.extra_image_data_uri,
                "website_url": producto.website_url
            }
            productos_dict['skus'].append(d)

        return productos_dict

    @http.route("/barriotec/skus", auth="public", )
    def index(self, **kw):
        self.log_in()

        # public = http.request.env.ref('base.public_user')

        # print(http.request.env['ir.http'].session_info())
        # productos = http.request.env['product.template'].with_user(public).search([
        productos = http.request.env['product.template'].search([
            ["is_booking_type", "=", True],
            # ["categ_id", "=", categoriaId],
        ])
        self.log_out()
        return json.dumps(self.cargarDiccionario(productos))
    