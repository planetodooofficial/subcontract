from odoo import api, models


class DeliveryChallan(models.AbstractModel):
    _name = 'report.subcontract.report_deliveryslip'

    @api.model
    def get_report_values(self, docids, data):
        data = data if data is not None else {}
        return {
            'datas': data.get('values'),
            'product_datas': data.get('product_values'),
            'work_id': data.get('work_id')
        }
