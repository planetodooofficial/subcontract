# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class Subcontracting(models.Model):
    _inherit = 'mrp.production'

    is_subcontract = fields.Boolean('Subcontracting')
