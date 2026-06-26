# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import fields, models


class CrmLeadReminder(models.Model):  # pylint: disable=too-few-public-methods
    _name = "crm.lead.reminder"
    _description = "CRM Lead Reminder"
    _order = "stage_id, days_on_stage, hours_on_stage"

    lead_id = fields.Many2one(
        string="Lead",
        comodel_name="crm.lead",
        required=True,
        ondelete="cascade",
    )
    stage_id = fields.Many2one(
        string="Stage",
        comodel_name="crm.stage",
        required=True,
        ondelete="restrict",
    )
    days_on_stage = fields.Integer(
        string="Days on Stage",
        default=0,
    )
    hours_on_stage = fields.Integer(
        string="Hours on Stage",
        default=0,
    )
    email_template_id = fields.Many2one(
        string="Email Template",
        comodel_name="mail.template",
        required=True,
        ondelete="restrict",
    )
    number_of_reminder = fields.Integer(
        string="Number of Reminder",
        default=1,
    )
    message_ids = fields.Many2many(
        string="Sent Messages",
        comodel_name="mail.message",
        relation="rel_lead_reminder_2_mail_message",
        column1="reminder_id",
        column2="message_id",
        readonly=True,
    )
    reminder_count = fields.Integer(
        string="Reminder Count",
        default=0,
        readonly=True,
        copy=False,
    )
    user_ids = fields.Many2many(
        string="Users",
        comodel_name="res.users",
        relation="rel_lead_reminder_2_res_users",
        column1="reminder_id",
        column2="user_id",
        required=True,
    )

    def _send_notification(self, lead):
        self.ensure_one()
        if not self.email_template_id or not self.user_ids:
            return
        mail_values = self.email_template_id.generate_email(
            lead.id, ["subject", "body_html"]
        )
        partner_ids = self.user_ids.mapped("partner_id").ids
        message = lead.message_post(
            body=mail_values.get("body_html", ""),
            subject=mail_values.get("subject", ""),
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            partner_ids=partner_ids,
        )
        if message:
            self.message_ids = [(4, message.id)]
            self.write({"reminder_count": self.reminder_count + 1})
