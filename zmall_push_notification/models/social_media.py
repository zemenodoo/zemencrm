# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class SocialMediathenewpushNotifications(models.Model):
    _inherit = 'social.media'

    media_type = fields.Selection(selection_add=[('thenewpush_notifications', 'The New Push Notification')])

    def action_add_account(self):
        self.ensure_one()

        if self.media_type != 'thenewpush_notifications':
            return super(SocialMediathenewpushNotifications, self).action_add_account()

        return None
