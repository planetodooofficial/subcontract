# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.exceptions import UserError, AccessError, ValidationError

from odoo import models, api, fields, _


class SubcontractingWorkCenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    is_subcontract = fields.Boolean('Subcontracting')
    subcontract_vendor = fields.Many2one('res.partner', 'Supplier')
    subcontract_product = fields.Many2one('product.template', 'Product')
    subcontract_service_cost = fields.Integer('Cost Per Unit')
    subcontract_location = fields.Many2one('stock.location', 'Supplier Location')

    @api.onchange('subcontract_vendor')
    def onchange_supplier_location(self):
        if self.subcontract_vendor.subcontracted_location:
            self.subcontract_location = self.subcontract_vendor.subcontracted_location.id
        else:
            self.subcontract_location = ''
            raise ValidationError(_("Please mention 'Subcontracted Location' for the selected Supplier."))


class VendorLocation(models.Model):
    _inherit = 'res.partner'

    subcontracted_location = fields.Many2one('stock.location', 'Subcontracted Location')


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    manufacturing_order_number = fields.Many2one('mrp.production', "Manufacturing Order", store=True)
    sale_order_number = fields.Many2one('sale.order', "Sale Order", store=True)


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
            for workorder in self.workorder_ids:
                if operations.name == workorder.name:
                    if operations.is_subcontract is True:
                        workorder.update({
                            'is_subcontract': True,
                            'subcontract_wo_vendor': operations.subcontract_vendor.id,
                            'subcontract_wo_product': operations.subcontract_product.id,
                            'subcontract_wo_service_cost': operations.subcontract_service_cost,
                            'subcontract_supplier_location': operations.subcontract_location.id
                        })
        return orders_to_plan.write({'state': 'planned'})


class SubcontractingWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    is_subcontract = fields.Boolean('Subcontracting', readonly=False, store=True, default=False)
    subcontract_wo_vendor = fields.Many2one('res.partner', 'Supplier', readonly=True, store=True)
    subcontract_wo_product = fields.Many2one('product.template', 'Product', readonly=True, store=True)
    subcontract_wo_service_cost = fields.Float('Cost Per Unit', readonly=True, store=True)
    subcontract_supplier_location = fields.Many2one('stock.location', "Supplier Location", readonly=True, store=True)

    is_rfq = fields.Boolean('RFQ', default=False)

    rfq_ids = fields.Many2one('purchase.order', 'RFQ')

    def create_rfq(self):
        receipt = self.env['stock.picking.type'].search([('name', '=', 'Receipts')], limit=1)
        product = self.env['product.product'].search([('name', '=', self.subcontract_wo_product.name)])
        sale_id = self.env['sale.order'].search([('name', '=', self.production_id.origin)])

        for orders in self:
            rfq = self.env['purchase.order'].create({
                'partner_id': orders.subcontract_wo_vendor.id,
                'date_order': datetime.now(),
                'origin': self.name,
                'date_planned': datetime.now(),
                'picking_type_id': receipt.id,
                'manufacturing_order_number': self.production_id.id,
                'sale_order_number': sale_id.id if sale_id.id else None
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

            self.update({
                'rfq_ids': rfq.id
            })

        self.update({'is_rfq': True})

    @api.multi
    def button_start(self):
        mrp = self.env['mrp.production'].search([('name', '=', self.production_id.name)])
        for workorder in mrp.workorder_ids:
            if workorder.state == 'progress':
                raise ValidationError(
                    _("Please finish the 'In Progress' Work Order first to proceed with the next one."))
            else:
                pass
        res = super(SubcontractingWorkOrder, self).button_start()
        return res

    def print_delivery_challan(self):
        print()
