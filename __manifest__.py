{
    'name': 'Subcontracting through Work Orders',
    'version': '11.0.1.0',
    'summary': 'Subcontracting in Manufacturing Order',
    'description': """
    This module provides a subcontracting work orders for manufacturing order..
    """,
    'author': 'Planet-Odoo',
    'company': 'Planet-Odoo',
    'website': "https://planet-odoo.com/",
    'category': 'Manufacturing',
    'depends': ['base', 'mrp', 'sale', 'purchase', 'stock', 'contacts', 'product', 'mail'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/subcontracting_view.xml',
        'views/subcontracting_routing.xml',
        'views/subcontracting_workorder.xml',
        'views/partner_view.xml',
    ],
    'demo': [],
    'images': [],
    'license': 'LGPL-3',
    'installable': True,
    'application': False
}