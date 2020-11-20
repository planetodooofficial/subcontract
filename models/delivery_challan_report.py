from odoo import api, models


class DeliveryChallan(models.AbstractModel):
    _name = 'report.subcontract.report_deliveryslip'

    @api.model
    def get_report_values(self, docids, data):
        data = data if data is not None else {}
        products = data.get('product_values')
        prod_len = len(products)
        max_len = 5
        return {
            'datas': data.get('values'),
            'products': data.get('product_values'),
            'prod_len' : prod_len,
            'max_len' : max_len
        }
