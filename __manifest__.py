# -*- coding: utf-8 -*-
{
    'name': "Dynamic Attachments to Mails",
    'summary': """
        Attach Report to Mail Composer dynamically.""",
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
        'views/mail_attachment_line.xml',
        'views/res_config_settings.xml'
    ]
}
