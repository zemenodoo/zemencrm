# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.osv import expression


class UtmCampaign2(models.Model):
    _inherit = 'utm.campaign'

    social_post_ids = fields.One2many(compute="_compute_social_post_ids")
    social_thenewpush_notification_ids = fields.One2many("social.post", "utm_campaign_id", compute="_compute_social_post_ids", string="thenewpush Notifications")
    social_thenewpush_notifications_count = fields.Integer(compute='_compute_social_thenewpush_notifications_count', string='Number Of thenewpush Notifications')

    def _compute_social_post_ids(self):
        """social_post_ids has to contain every posts that have at least one 'real' social media
        like twitter or facebook. Posts that are nothing but thenewpush notifications are filtered out of social_post_ids
        and affected to social_thenewpush_notification_ids.
        Posts that are linked to real social media and thenewpush notifications will be present in both fields"""

        thenewpush_notification_media_id = self.env.ref('social_thenewpush_notifications.social_media_thenewpush_notifications').id
        for campaign in self:
            campaign.social_post_ids = self.env['social.post'].search([('utm_campaign_id', 'in', campaign.ids)])
            campaign.social_thenewpush_notification_ids = campaign.social_post_ids.filtered(lambda post: thenewpush_notification_media_id in post.media_ids.ids)
            # Filter out the posts who are only thenewpush notifications
            campaign.social_post_ids = campaign.social_post_ids - campaign.social_thenewpush_notification_ids.filtered(lambda thenewpush_notif: len(thenewpush_notif.media_ids) == 1)

    def _compute_social_thenewpush_notifications_count(self):
        thenewpush_notifications_data = self.env['social.post'].read_group(
            [('utm_campaign_id', 'in', self.ids), ('media_ids.media_type', '=', 'thenewpush_notifications')],
            ['utm_campaign_id'], ['utm_campaign_id'])
        mapped_data = {datum['utm_campaign_id'][0]: datum['utm_campaign_id_count'] for datum in thenewpush_notifications_data}
        for campaign in self:
            campaign.social_thenewpush_notifications_count = mapped_data.get(campaign.id, 0)

    def action_redirect_to_thenewpush_notifications(self):
            action = self.env["ir.actions.actions"]._for_xml_id("social.action_social_post")
            action['domain'] = [('utm_campaign_id', '=', self.id), ('media_ids.media_type', '=', 'thenewpush_notifications')]
            action['context'] = {
                "with_searchpanel": True,
                "searchpanel_default_state": "posted",
                "default_utm_campaign_id": self.id
            }
            return action

    def action_send_thenewpush_notification(self):
        thenewpush_media = self.env['social.media'].search([('media_type', '=', 'thenewpush_notifications')])
        action = self.env["ir.actions.actions"]._for_xml_id("social.action_social_post")
        action['views'] = [[False, 'form']]
        action['context'] = {
            'default_account_ids': thenewpush_media.account_ids.ids,
            'search_default_utm_campaign_id': self.id,
            'default_utm_campaign_id': self.id
        }
        return action

    def _get_campaign_social_posts_domain(self):
        domain = super(UtmCampaign2, self)._get_campaign_social_posts_domain()
        return expression.AND([domain, [('media_ids.media_type', '!=', 'thenewpush_notifications')]])

    def _get_social_media_accounts_domain(self):
        domain = super(UtmCampaign2, self)._get_social_media_accounts_domain()
        return expression.AND([domain, [('media_type', '!=', 'thenewpush_notifications')]])
