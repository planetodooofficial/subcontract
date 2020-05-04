# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class SubcontractingWorkCenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    is_subcontract = fields.Boolean('Subcontracting')
    subcontract_vendor = fields.Many2one('res.partner', 'Supplier')
    subcontract_product = fields.Many2one('product.template', 'Product')
    subcontract_service_cost = fields.Integer('Cost Per Unit')


class SubcontractingWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    is_subcontracting = fields.Boolean('Subcontracting')


class SubcontractingPurchaseOrder(models.Model):
    _inherit = 'purchase.order'


class SubcontractingMrp(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def button_plan(self):
        """ Create work orders. And probably do stuff, like things. """

        operations = self.routing_id.operation_ids
        for rec in operations:
            if rec.is_subcontract is True:
                self.env['mrp.workorder'].create({
                    'is_subcontracting': True,
                    'product_id': self.product_id.id,
                    'name': rec.name,
                    'workcenter_id': rec.workcenter_id.id,
                    'production_id': self.id
                })
            else:
                orders_to_plan = self.filtered(lambda order: order.routing_id and order.state == 'confirmed')
                for order in orders_to_plan:
                    quantity = order.product_uom_id._compute_quantity(order.product_qty,
                                                                      order.bom_id.product_uom_id) / order.bom_id.product_qty
                    boms, lines = order.bom_id.explode(order.product_id, quantity, picking_type=order.bom_id.picking_type_id)
                    order._generate_workorders(boms)
                return orders_to_plan.write({'state': 'planned'})
        return self.write({'state': 'planned'})
