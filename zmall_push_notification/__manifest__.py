# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'The New Push Notifications',
    'category': 'Marketing/Social Marketing',
    'summary': 'Send live notifications to your web visitors',
    'version': '1.0',
    'description': """Send live notifications to your web visitors""",
    'depends': ['social', 'website'],
    'external_dependencies': {
        'python': ['google_auth'],
    },
    'data': [
        'security/ir.model.access.csv',
       # 'views/assets.xml',
        'views/social_post_views.xml',
       # 'views/res_config_settings_views.xml',
        'views/social_push_notifications_templates.xml',
       # 'views/website_visitor_views.xml',
       # 'views/utm_campaign_views.xml',
        'data/social_media_data.xml',
    ],
    'auto_install': True,
    'post_init_hook': '_create_social_accounts',
    'application': True,
}
