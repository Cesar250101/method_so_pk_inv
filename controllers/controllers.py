# -*- coding: utf-8 -*-
from odoo import http

# class MethodSoPkInv(http.Controller):
#     @http.route('/method_so_pk_inv/method_so_pk_inv/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/method_so_pk_inv/method_so_pk_inv/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('method_so_pk_inv.listing', {
#             'root': '/method_so_pk_inv/method_so_pk_inv',
#             'objects': http.request.env['method_so_pk_inv.method_so_pk_inv'].search([]),
#         })

#     @http.route('/method_so_pk_inv/method_so_pk_inv/objects/<model("method_so_pk_inv.method_so_pk_inv"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('method_so_pk_inv.object', {
#             'object': obj
#         })