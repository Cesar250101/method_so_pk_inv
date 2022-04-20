# -*- coding: utf-8 -*-

from unittest import case
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    facturacion_automatica = fields.Boolean(related="company_id.facturacion_automatica",string='Facturacion Automatica?' ,readonly=False)
    tipo_documento = fields.Selection(related="company_id.tipo_documento",readonly=False,string='Tipo de Documento', selection=[('boleta', 'Boleta'), ('factura', 'Factura'),])
    
class ResCompany(models.Model):
    _inherit = 'res.company'

    facturacion_automatica = fields.Boolean(string='Facturacion Automatica?')
    tipo_documento = fields.Selection(string='Tipo de Documento', selection=[('boleta', 'Boleta'), ('factura', 'Factura'),])


class PedidoVeta(models.Model):
    _inherit = 'sale.order'

    @api.model
    def valida_orden(self):
        company=self.env.user.company_id
        ordenes_sin_validar=self.search([('state','=','draft')],limit=1)
        configuracion=self.env['res.company'].search([('id','=',company.id)])
        order_line=[] 
        for orden in ordenes_sin_validar:
            orden.sudo().action_confirm()
            picking_id=self.env['stock.picking'].search([('sale_id','=',orden.id)],limit=1)
            stock_move_id=self.env['stock.move'].search([('picking_id','=',picking_id.id)])
            stock_move_uno_id=self.env['stock.move'].search([('picking_id','=',picking_id.id)],limit=1)
            stock_move_line_id=self.env['stock.move.line'].search([('picking_id','=',picking_id.id)]) 

            if stock_move_line_id:
                for sm in stock_move_id:
                    val={
                                'qty_done':sm.product_qty,
                                'location_id':stock_move_uno_id.location_id.id,
                                }
                    sm.sudo().write(val)
            else:                
                for sm in stock_move_id:
                    val={
                            'picking_id':picking_id.id,
                            'product_id':sm.product_id.id,
                            'move_id':sm.id,
                            'product_uom_id':sm.product_uom.id,
                            'qty_done':sm.product_qty,
                            'location_id':sm.location_id.id,
                            'location_dest_id':sm.location_dest_id.id
                            }   
                    stock_move_line_id.sudo().create(val)
            if len(picking_id)>0:
                picking_id.button_validate()
            if configuracion.facturacion_automatica==True:
                #Detalle de factura
                factura=self.env['account.invoice']
                for ol in orden.order_line:
                    order_line.append(
                                (0, 0, {
                                "product_id": ol.product_id.id,
                                "product_uom_qty":ol.product_uom_qty,
                                "price_unit": ol.price_unit,
                                "discount": ol.discount,
                                "product_uom":ol.product_id.product_tmpl_id.uom_id.id,
                                "name":ol.product_id.product_tmpl_id.name, 
                                "account_id":ol.product_id.categ_id.property_account_income_categ_id.id,
                                "invoice_line_tax_ids": [(6, 0, [x.id for x in ol.tax_id])],
                                        })) 
                #Encabezado de factura
                if configuracion.tipo_documento=="boleta":
                    tipodocto=self.env['sii.document_class'].search([('name','=','Boleta Electrónica')])
                elif configuracion.tipo_documento=="factura":
                    tipodocto=self.env['sii.document_class'].search([('name','=','Factura Electrónica')])
                document_class=self.env['account.journal.sii_document_class'].search([('sii_document_class_id','=',tipodocto.id)])

                values={
                        "journal_document_class_id":document_class.id,
                        "partner_id":orden.partner_id.id,
                        "origin":orden.name,
                        "team_id":orden.team_id.id,
                        "payment_term_id":orden.payment_term_id.id if orden.payment_term_id else False,
                        "invoice_line_ids":order_line,
                        "user_id":orden.user_id.id
                    }
                Factura_id=factura.sudo().create(values)        
                orden.write({'invoiced': True, 'invoice_line_id': Factura_id.id})    
                Factura_id=Factura_id.action_invoice_open()
                print(factura)
            

    