# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _name = "crm.lead"
    _inherit = [
        "crm.lead",
        "mixin.sequence",
    ]

    name = fields.Char(
        string="Opportunity",
        default="/",
        required=True,
        index=True,
        copy=False,
    )
    stage_log_ids = fields.One2many(
        string="Stage History",
        comodel_name="crm.lead.stage.log",
        inverse_name="lead_id",
    )
    reminder_ids = fields.One2many(
        string="Reminders",
        comodel_name="crm.lead.reminder",
        inverse_name="lead_id",
    )
    latest_stage_log_id = fields.Many2one(
        string="Latest Stage Log",
        comodel_name="crm.lead.stage.log",
        compute="_compute_latest_stage_log_id",
        store=True,
        compute_sudo=True,
    )
    latest_log_stage_id = fields.Many2one(
        string="Latest Log Stage",
        comodel_name="crm.stage",
        related="latest_stage_log_id.stage_id",
        store=True,
        compute_sudo=True,
    )
    latest_log_datetime = fields.Datetime(
        string="Latest Log Datetime",
        related="latest_stage_log_id.date",
        store=True,
        compute_sudo=True,
    )
    days_on_stage = fields.Float(
        string="Days on Stage",
        compute="_compute_days_hours_on_stage",
        store=True,
        compute_sudo=True,
    )
    hours_on_stage = fields.Float(
        string="Hours on Stage",
        compute="_compute_days_hours_on_stage",
        store=True,
        compute_sudo=True,
    )
    allowed_contact_contractor_ids = fields.Many2many(
        string="Allowed Contractor's Contact",
        comodel_name="res.partner",
        compute="_compute_allowed_contact_contractor_ids",
        store=False,
        compute_sudo=True,
    )
    contractor_id = fields.Many2one(
        string="Contractor",
        comodel_name="res.partner",
        domain=[
            ("parent_id", "=", False),
        ],
    )
    contact_contractor_id = fields.Many2one(
        string="Contact's Contact",
        comodel_name="res.partner",
        required=False,
    )
    reference_ids = fields.Many2many(
        string="References",
        comodel_name="res.partner",
        relation="rel_lead_reference_2_partner",
        column1="lead_id",
        column2="partner_id",
    )
    pricelist_id = fields.Many2one(
        string="Pricelist",
        comodel_name="product.pricelist",
    )
    product_ids = fields.Many2many(
        string="Products",
        comodel_name="product.product",
        relation="rel_lead_2_product",
        column1="lead_id",
        column2="product_id",
    )

    @api.depends(
        "stage_log_ids",
        "stage_log_ids.date",
    )
    def _compute_latest_stage_log_id(self):
        StageLog = self.env["crm.lead.stage.log"]  # pylint: disable=invalid-name
        for record in self:
            latest = StageLog.search(
                [("lead_id", "=", record.id)],
                order="date desc",
                limit=1,
            )
            record.latest_stage_log_id = latest or False

    @api.depends()
    def _compute_days_hours_on_stage(self):
        now = fields.Datetime.now()
        for record in self:
            if record.latest_log_datetime:
                delta = now - record.latest_log_datetime
                total_seconds = delta.total_seconds()
                total_hours = int(total_seconds // 3600)
                record.days_on_stage = total_hours // 24
                record.hours_on_stage = total_hours % 24
            else:
                record.days_on_stage = 0.0
                record.hours_on_stage = 0.0

    @api.model
    def _cron_check_send_reminders(self):
        records = self.search(
            [
                ("active", "=", True),
                ("stage_id.is_won", "=", False),
            ]
        )
        records._compute_days_hours_on_stage()
        records._check_and_send_reminders()

    def _check_and_send_reminders(self):
        for record in self:
            for reminder in record.reminder_ids:
                if reminder.reminder_count >= reminder.number_of_reminder:
                    continue
                if reminder.stage_id != record.stage_id:
                    continue
                lead_total_hours = record.days_on_stage * 24 + record.hours_on_stage
                threshold_total_hours = (
                    reminder.days_on_stage * 24 + reminder.hours_on_stage
                )
                if lead_total_hours >= threshold_total_hours:
                    reminder._send_notification(record)

    @api.depends(
        "contractor_id",
    )
    def _compute_allowed_contact_contractor_ids(self):
        Partner = self.env["res.partner"]  # pylint: disable=invalid-name
        for record in self:
            result = []
            if record.contractor_id:
                criteria = [
                    ("commercial_partner_id", "=", record.contractor_id.id),
                    ("id", "!=", record.contractor_id.id),
                    ("type", "=", "contact"),
                ]
                result = Partner.search(criteria).ids
            record.allowed_contact_contractor_ids = result

    def _check_stage_transition_restriction(self, values):
        new_stage_id = values.get("stage_id")
        for record in self:
            if not record.team_id:
                continue
            if new_stage_id == record.stage_id.id:
                continue
            from_stage = record.stage_id
            to_stage = (
                self.env["crm.stage"].browse(new_stage_id)
                if new_stage_id
                else self.env["crm.stage"]
            )
            restrictions = record.team_id.stage_restriction_ids.filtered(
                lambda r: (not r.from_stage_id or r.from_stage_id == from_stage)
                and (not r.to_stage_id or r.to_stage_id == to_stage)
            )
            if not restrictions:
                continue
            allowed_roles = restrictions.mapped("role_ids")
            user_roles = record.team_id.member_role_ids.filtered(
                lambda m: self.env.user in m.user_ids
            ).mapped("role_id")
            if allowed_roles & user_roles:
                continue
            error_message = _(
                """
Context: Change Opportunity Stage
Database ID: %s
Problem: Moving a lead of sales team "%s" from stage "%s" to stage "%s" is
restricted to role(s): %s. User "%s" holds none of those roles in this team.
Solution: Ask a user with one of the required roles to move the stage, or
update Member Roles / Stage Restrictions of sales team "%s".
"""
                % (
                    record.id,
                    record.team_id.name,
                    from_stage.name or "(none)",
                    to_stage.name or "(none)",
                    ", ".join(allowed_roles.mapped("name")) or "(none)",
                    self.env.user.name,
                    record.team_id.name,
                )
            )
            raise UserError(error_message)

    @api.model
    def create(self, values):
        _super = super(CrmLead, self)  # pylint: disable=super-with-arguments
        result = _super.create(values)
        try:
            result._create_sequence()
        except Exception:
            pass
        if result.stage_id:
            self.env["crm.lead.stage.log"].create(
                {
                    "lead_id": result.id,
                    "stage_id": result.stage_id.id,
                    "date": fields.Datetime.now(),
                    "user_id": self.env.user.id,
                }
            )
        if result.team_id and result.team_id.reminder_ids:
            for team_reminder in result.team_id.reminder_ids:
                self.env["crm.lead.reminder"].create(
                    {
                        "lead_id": result.id,
                        "stage_id": team_reminder.stage_id.id,
                        "days_on_stage": team_reminder.days_on_stage,
                        "hours_on_stage": team_reminder.hours_on_stage,
                        "email_template_id": team_reminder.email_template_id.id,
                        "number_of_reminder": team_reminder.number_of_reminder,
                        "user_ids": [(6, 0, team_reminder.user_ids.ids)],
                    }
                )
        return result

    def write(self, values):
        if "stage_id" in values:
            self._check_stage_transition_restriction(values)
        result = super(CrmLead, self).write(  # pylint: disable=super-with-arguments
            values
        )
        if "stage_id" in values:
            for record in self:
                self.env["crm.lead.stage.log"].create(
                    {
                        "lead_id": record.id,
                        "stage_id": values["stage_id"],
                        "date": fields.Datetime.now(),
                        "user_id": self.env.user.id,
                    }
                )
        return result
