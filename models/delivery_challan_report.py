from odoo import api, models


class DeliveryChallan(models.AbstractModel):
    _name = 'report.subcontract.report_material_issued_2'

    @api.model
    def get_report_values(self, docids, data):
        data = data if data is not None else {}
        return {
            'datas': data.get('list_vals'),
            'form_data': data.get('form_value')
        }
