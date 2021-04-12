# -*- coding: utf-8 -*-
{
    'name': "Dinamic Attachments to Mails",
    'summary': """
        Attach Report to Mail Composer dinamically.""",
    'description': """
    """,
    'author': "Alliantum",
    'website': "https://www.alliantum.com",
    'category': 'Technical',
    'version': '0.1',
    'depends': ['base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/manage_mail_attachments.xml',
        'views/res_config_settings.xml'
    ]
}
