{
    'name': 'Website Age Verification (Odoo 18)',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'summary': 'Always-show age verification popup for website',
    'description': 'Display an age verification popup on all website pages.',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',

    'depends': ['website'],

    'data': [
        'views/age_verification_settings.xml',
        'views/age_verification_template.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'website_age_verification/static/src/scss/popup.scss',
            'website_age_verification/static/src/js/popup_frontend.js',
        ],
    },

    'installable': True,
    'application': False,
    'auto_install': False,
}