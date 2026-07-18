# -*- coding: utf-8 -*-
{
    'name': 'Delivery Courier Custom',
    'version': '18.0.2.7.0',
    'category': 'Inventory/Delivery',
    'summary': 'Custom delivery courier workflow with email notifications',
    'description': """
        Delivery Courier Custom Module
        ================================
        * Adds custom courier state to delivery orders
        * Simplified status bar (Draft → Waiting → Ready → Courier Assigned → Done)
        * Send Courier button with email notification
        * Single Validate button (removed duplicates)
        * Automatic status updates based on delivery state
        * Chatter integration for tracking
        * Automated email notifications with delivery details
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'stock',
        'delivery',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template_data.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
