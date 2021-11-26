from odoo import http
import json


class OdooController(http.Controller):


    @http.route("/barriotec/skus", auth="public", )
    def index(self, **kw):
        print('entro')
        self.auth()
        # public = self.env.ref('base.public_user')
        # print(self.env['ir.http'].session_info())
        # productos = self.env['product.template'].with_user(public).search([
    
        print('entro2')
        productos = http.request.env['product.template'].search([
            ["is_booking_type", "=", True],
            # ["categ_id", "=", categoriaId],
        ])
        print('entro3')
        self.auth(login=False)
        print('entro4')
        return json.dumps(self.cargarDiccionario(productos))

    def auth(self, login=True):

        uid = http.request.session.uid
        # Comprobamos que no haya ningún usuario autenticado.
        print('uid:', uid)
        if uid == None:
            print("no autenticado, ", login)
            if login:
                http.request.session.authenticate("test", "web", "12345")
            else:
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
