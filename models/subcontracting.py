# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, api, fields, _


class SubcontractingWorkCenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    is_subcontract = fields.Boolean('Subcontracting')
    subcontract_vendor = fields.Many2one('res.partner', 'Supplier')
    subcontract_product = fields.Many2one('product.product', 'Product')
    subcontract_service_cost = fields.Integer('Cost Per Unit')


class MRP(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def button_plan(self):
        """ Create work orders. And probably do stuff, like things. """
        orders_to_plan = self.filtered(lambda order: order.routing_id and order.state == 'confirmed')
        for order in orders_to_plan:
            quantity = order.product_uom_id._compute_quantity(order.product_qty,
                                                              order.bom_id.product_uom_id) / order.bom_id.product_qty
            boms, lines = order.bom_id.explode(order.product_id, quantity, picking_type=order.bom_id.picking_type_id)
            order._generate_workorders(boms)

        for operations in self.routing_id.operation_ids:
            self.env['mrp.workorder'].write({
                'is_subcontract': True,
                'subcontract_wo_vendor': operations.subcontract_vendor.id,
                'subcontract_wo_product': operations.subcontract_product.id,
                'subcontract_wo_service_cost': operations.subcontract_service_cost
            })
        return orders_to_plan.write({'state': 'planned'})


class SubcontractingWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    is_subcontract = fields.Boolean('Subcontracting', readonly=True, store=True)
    subcontract_wo_vendor = fields.Many2one('res.partner', 'Supplier', readonly=True, store=True)
    subcontract_wo_product = fields.Many2one('product.template', 'Product', readonly=True, store=True)
    subcontract_wo_service_cost = fields.Float('Cost Per Unit', readonly=True, store=True)

    is_rfq = fields.Boolean('RFQ', default=False)

    def create_rfq(self):

        receipt = self.env['stock.picking.type'].search([('name', '=', 'Receipts')], limit=1)
        product = self.env['product.product'].search([('name', '=', self.subcontract_wo_product.name)])

        for orders in self:
            rfq = self.env['purchase.order'].create({
                'partner_id': orders.subcontract_wo_vendor.id,
                'date_order': datetime.now(),
                'origin': self.name,
                'date_planned': datetime.now(),
                'picking_type_id': receipt.id
            })

            order_line = self.env['purchase.order.line'].create({
                'order_id': rfq.id,
                'product_id': product.id,
                'name': product.name,
                'date_planned': datetime.now(),
                'product_qty': 1,
                'product_uom': product.uom_po_id.id,
                'price_unit': orders.subcontract_wo_service_cost,
            })


