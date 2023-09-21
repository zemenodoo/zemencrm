# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
from binascii import Error as binascii_error

from odoo import models, fields, api, _
import requests
import logging
_logger = logging.getLogger(__name__)

class SocialPostthenewpushUSers(models.Model):
    _inherit = "res.users"

    thenewpush_notification = fields.One2many('social.post', 'sent_users', string="thenewpush Sent Users")


class SocialPostthenewpushNotifications(models.Model):
    _inherit = 'social.post'

    display_thenewpush_notification_attributes = fields.Boolean('Display thenewpush Notifications Attributes', compute="_compute_display_thenewpush_notification_attributes")
    thenewpush_notification_title = fields.Char('thenewpush Notification Title')
    thenewpush_notification_target_url = fields.Char('thenewpush Target URL')
    thenewpush_notification_image = fields.Binary("thenewpush Icon Image", help="This icon will be displayed in the browser notification")

    display_thenewpush_notifications_preview = fields.Boolean('Display thenewpush Notifications Preview', compute='_compute_display_thenewpush_notifications_preview')
    thenewpush_notifications_preview = fields.Html('thenewpush Notifications Preview', compute='_compute_thenewpush_notifications_preview')

    use_visitor_timezone = fields.Boolean("Send at Visitors' Timezone", default=True,
        help="e.g: If you post at 15:00, visitors will receive the post at 15:00 their time.")
    user_domain = fields.Char(string="User Domain", default=[['x_devicetoken', '!=', False]], help="Domain to send thenewpush notifications to visitors.")
    sent_users = fields.Many2many('res.users', string="Send To")
    notification_request_url = fields.Text(string="URL" , default="somethng2")
    @api.depends('message', 'account_ids.media_id.media_type')
    def _compute_display_thenewpush_notifications_preview(self):
        for post in self:
            post.display_thenewpush_notifications_preview = post.message \
                and ('thenewpush_notifications' in post.account_ids.media_id.mapped('media_type'))

    @api.depends('message', 'thenewpush_notification_title', 'thenewpush_notification_image')
    def _compute_thenewpush_notifications_preview(self):
        for post in self:
            icon = False
            icon_url = False
            if post.thenewpush_notification_image:
                try:
                    base64.b64decode(post.thenewpush_notification_image, validate=True)
                    icon = post.thenewpush_notification_image
                except binascii_error:
                    if post.id or (post._origin and post._origin.id):
                        icon_url = '/web/image/social.post/%s/thenewpush_notification_image' % (post.id if post.id else post._origin.id)

            post.thenewpush_notifications_preview = self.env.ref('zmall_push_notification.thenewpush_notifications_preview')._render({
                'title': post.thenewpush_notification_title or _('New Message'),
                'icon': icon,
                'icon_url': icon_url,
                'message': post.message,
                'host_name': self.env['ir.config_parameter'].sudo().get_param('web.base.url') or 'https://myapp.com'
            })

    @api.depends('account_ids.media_id.media_type')
    def _compute_display_thenewpush_notification_attributes(self):
        for post in self:
            post.display_thenewpush_notification_attributes = 'thenewpush_notifications' in post.account_ids.media_id.mapped('media_type')

    @api.model_create_multi
    def create(self, vals_list):
        """ Assign a default thenewpush_notification_target_url is none specified and we can extract one from the message """
        for i in range(len(vals_list)):
            if not vals_list[i].get('thenewpush_notification_target_url'):
                extracted_url = self._extract_url_from_message(vals_list[i]['message'])
                if extracted_url:
                    vals_list[i]['thenewpush_notification_target_url'] = extracted_url
        return super(SocialPostthenewpushNotifications, self).create(vals_list)

    def write(self, vals):
        """ Assign a default thenewpush_notification_target_url is none specified and we can extract one from the message """
        if not any(post.thenewpush_notification_target_url for post in self) and vals.get('message'):
            extracted_url = self._extract_url_from_message(vals['message'])
            if extracted_url:
                vals['thenewpush_notification_target_url'] = extracted_url
        return super(SocialPostthenewpushNotifications, self).write(vals)

    @api.model
    def _cron_publish_scheduled(self):
        """ This method is overridden to gather all pending thenewpush live.posts ('ready' state) and post them.
        This is done in the cron job instead of instantly to avoid blocking the 'Post' action of the user
        indefinitely.

        The related social.post will remain 'pending' until all live.posts are processed. """

        super(SocialPostthenewpushNotifications, self)._cron_publish_scheduled()

        ready_live_posts = self.env['social.live.post'].search([
            ('state', 'in', ['ready', 'posting'])
        ])
        thenewpush_notifications_live_posts = ready_live_posts.filtered(
            lambda post: post.account_id.media_type == 'thenewpush_notifications'
        )
        thenewpush_notifications_live_posts.write({
            'state': 'posting'
        })
        _logger.info(thenewpush_notifications_live_posts)
        thenewpush_notifications_live_posts._post_thenewpush_notifications()
