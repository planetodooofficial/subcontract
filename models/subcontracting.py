# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class SubcontractingWorkCenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    is_subcontract = fields.Boolean('Subcontracting')
    subcontract_vendor = fields.Many2one('res.partner', 'Supplier')
    subcontract_product = fields.Many2one('product.template', 'Product')
    subcontract_service_cost = fields.Integer('Cost Per Unit')


class SubcontractingWorkOrder(models.Model):
    _name = 'mrp.subcontract.workorder'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    is_subcontracting = fields.Boolean('Subcontracting', default=False)
    subcontract_product_id = fields.Many2one('product.product', 'To Produce')
    name = fields.Char('Work Order')
    sub_workcenter_name = fields.Many2one('mrp.workcenter', 'Work Center')
    sub_production_id = fields.Many2one('mrp.production', 'Manufacturing Order')
    state = fields.Selection([('pending', 'Pending'), ('ready', 'Ready'), ('progress', 'Progress'), ('done', 'Done')], string='State')




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
                self.env['mrp.subcontract.workorder'].create({
                    'is_subcontracting': True,
                    'subcontract_product_id': self.product_id.id,
                    'name': rec.name,
                    'sub_workcenter_name': rec.workcenter_id.id,
                    'sub_production_id': self.id,
                    'subcontract_state': 'pending'
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
