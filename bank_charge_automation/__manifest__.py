{
    'name': 'Bank Charge Automation',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Automatically handle bank charges during payments',
    'depends': ['account'],
    'data': [
        'views/account_journal_view.xml',
        'views/account_payment_view.xml',
    ],
    'installable': True,
    'application': False,
}
