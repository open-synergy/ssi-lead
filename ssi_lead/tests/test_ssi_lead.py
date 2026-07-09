# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSsiLead(YamlTransactionCase):
    def test_ssi_lead(self):
        self.run_yaml_scenario("test_data_ssi_lead.yaml")

    def test_member_role_rejects_non_team_member(self):
        """A user who is not a member of the sales team must not be
        assignable to a crm.team.member_role line for that team.
        """
        member_user = self.env["res.users"].create(
            {
                "name": "Member Role Constraint Test - Member",
                "login": "member_role_constraint_member@example.com",
            }
        )
        outsider_user = self.env["res.users"].create(
            {
                "name": "Member Role Constraint Test - Outsider",
                "login": "member_role_constraint_outsider@example.com",
            }
        )
        team = self.env["crm.team"].create(
            {
                "name": "Member Role Constraint Test Team",
                "member_ids": [(6, 0, [member_user.id])],
            }
        )
        role = self.env["crm_team_role"].create(
            {"name": "Constraint Test Role", "code": "CTR"}
        )

        with self.assertRaises(ValidationError):
            self.env["crm.team.member_role"].create(
                {
                    "team_id": team.id,
                    "role_id": role.id,
                    "user_ids": [(6, 0, [member_user.id, outsider_user.id])],
                }
            )

    def test_reminder_count_persists_to_db(self):
        """reminder_count must be written to DB after _send_notification so that
        a fresh ORM env (simulating the next cron run) still sees the cap.

        The YAML scenario 'Reminder count caps notifications' passes even with
        the bug because all three _check_and_send_reminders calls share the same
        ORM cache — reminder_count stays correct in-memory even if it was never
        flushed to DB.  This test reproduces the cross-transaction failure by
        calling env.invalidate_all() between checks, forcing a DB read.
        """
        stage = self.env["crm.stage"].create(
            {"name": "DB Persist Reminder Stage", "sequence": 99}
        )
        model_id = self.env["ir.model"].search([("model", "=", "crm.lead")], limit=1).id
        tpl = self.env["mail.template"].create(
            {
                "name": "DB Persist Reminder Template",
                "model_id": model_id,
                "subject": "Reminder",
                "body_html": "<p>Reminder body.</p>",
            }
        )
        lead = self.env["crm.lead"].create(
            {"name": "DB Persist Lead", "stage_id": stage.id}
        )
        reminder = self.env["crm.lead.reminder"].create(
            {
                "lead_id": lead.id,
                "stage_id": stage.id,
                "days_on_stage": 0,
                "hours_on_stage": 0,
                "email_template_id": tpl.id,
                "number_of_reminder": 1,
                "user_ids": [(6, 0, [self.env.ref("base.user_admin").id])],
            }
        )

        # First check — threshold met immediately (0 hours), should send once.
        lead._check_and_send_reminders()

        # Simulate a fresh cron transaction: discard ORM cache so the next
        # read comes from DB, not from in-memory.
        # Note: invalidate_all() is Odoo 16+; in Odoo 14 use invalidate_cache()
        reminder.invalidate_cache(["reminder_count", "message_ids"])

        self.assertEqual(
            reminder.reminder_count,
            1,
            "reminder_count must be 1 in DB after the first send",
        )

        # Second check — cache was cleared, so guard reads reminder_count from
        # DB.  If the fix is correct, reminder_count == 1 >= number_of_reminder
        # == 1, so no notification is sent.
        lead._check_and_send_reminders()
        reminder.invalidate_cache(["reminder_count", "message_ids"])

        self.assertEqual(
            reminder.reminder_count,
            1,
            "reminder_count must NOT increase beyond number_of_reminder after "
            "the cache is cleared between checks",
        )

    def test_stage_restriction_blocks_specific_pair(self):
        """A restriction with both from_stage_id and to_stage_id set must
        block that exact stage pair transition.
        """
        stage_a = self.env["crm.stage"].create(
            {"name": "Stage Restriction Test - A", "sequence": 1}
        )
        stage_b = self.env["crm.stage"].create(
            {"name": "Stage Restriction Test - B", "sequence": 2}
        )
        team = self.env["crm.team"].create(
            {
                "name": "Stage Restriction Test Team - Pair",
                "stage_restriction_ids": [
                    (
                        0,
                        0,
                        {
                            "from_stage_id": stage_a.id,
                            "to_stage_id": stage_b.id,
                        },
                    )
                ],
            }
        )
        lead = self.env["crm.lead"].create(
            {
                "name": "Stage Restriction Lead - Pair",
                "team_id": team.id,
                "stage_id": stage_a.id,
            }
        )

        with self.assertRaises(UserError):
            lead.write({"stage_id": stage_b.id})

    def test_stage_restriction_blocks_from_stage_only(self):
        """A restriction with only from_stage_id set must block moving away
        from that stage to any destination.
        """
        stage_a = self.env["crm.stage"].create(
            {"name": "Stage Restriction Test - From Only A", "sequence": 1}
        )
        stage_c = self.env["crm.stage"].create(
            {"name": "Stage Restriction Test - From Only C", "sequence": 2}
        )
        team = self.env["crm.team"].create(
            {
                "name": "Stage Restriction Test Team - From Only",
                "stage_restriction_ids": [(0, 0, {"from_stage_id": stage_a.id})],
            }
        )
        lead = self.env["crm.lead"].create(
            {
                "name": "Stage Restriction Lead - From Only",
                "team_id": team.id,
                "stage_id": stage_a.id,
            }
        )

        with self.assertRaises(UserError):
            lead.write({"stage_id": stage_c.id})

    def test_stage_restriction_blocks_to_stage_only(self):
        """A restriction with only to_stage_id set must block moving into
        that stage from any origin.
        """
        stage_b = self.env["crm.stage"].create(
            {"name": "Stage Restriction Test - To Only B", "sequence": 1}
        )
        stage_c = self.env["crm.stage"].create(
            {"name": "Stage Restriction Test - To Only C", "sequence": 2}
        )
        team = self.env["crm.team"].create(
            {
                "name": "Stage Restriction Test Team - To Only",
                "stage_restriction_ids": [(0, 0, {"to_stage_id": stage_b.id})],
            }
        )
        lead = self.env["crm.lead"].create(
            {
                "name": "Stage Restriction Lead - To Only",
                "team_id": team.id,
                "stage_id": stage_c.id,
            }
        )

        with self.assertRaises(UserError):
            lead.write({"stage_id": stage_b.id})

    def test_stage_restriction_ignored_without_team(self):
        """A lead without a sales team must never be blocked, even if an
        identical restriction is configured on some sales team.
        """
        stage_a = self.env["crm.stage"].create(
            {"name": "Stage Restriction Test - No Team A", "sequence": 1}
        )
        stage_b = self.env["crm.stage"].create(
            {"name": "Stage Restriction Test - No Team B", "sequence": 2}
        )
        self.env["crm.team"].create(
            {
                "name": "Stage Restriction Test Team - No Team",
                "stage_restriction_ids": [
                    (
                        0,
                        0,
                        {
                            "from_stage_id": stage_a.id,
                            "to_stage_id": stage_b.id,
                        },
                    )
                ],
            }
        )
        lead = self.env["crm.lead"].create(
            {
                "name": "Stage Restriction Lead - No Team",
                "team_id": False,
                "stage_id": stage_a.id,
            }
        )

        lead.write({"stage_id": stage_b.id})

        self.assertEqual(lead.stage_id, stage_b)

    def test_stage_restriction_not_enforced_on_create(self):
        """A restriction must never block the initial stage set at
        creation time, even if that stage would be forbidden as a
        destination on write().
        """
        stage_b = self.env["crm.stage"].create(
            {"name": "Stage Restriction Test - Create B", "sequence": 1}
        )
        team = self.env["crm.team"].create(
            {
                "name": "Stage Restriction Test Team - Create",
                "stage_restriction_ids": [(0, 0, {"to_stage_id": stage_b.id})],
            }
        )

        lead = self.env["crm.lead"].create(
            {
                "name": "Stage Restriction Lead - Create",
                "team_id": team.id,
                "stage_id": stage_b.id,
            }
        )

        self.assertEqual(lead.stage_id, stage_b)

    def test_stage_restriction_allows_unlisted_transition(self):
        """A stage transition that matches no configured restriction rule
        must succeed as usual.
        """
        stage_a = self.env["crm.stage"].create(
            {"name": "Stage Restriction Test - Unlisted A", "sequence": 1}
        )
        stage_d = self.env["crm.stage"].create(
            {"name": "Stage Restriction Test - Unlisted D", "sequence": 2}
        )
        team = self.env["crm.team"].create(
            {"name": "Stage Restriction Test Team - Unlisted"}
        )
        lead = self.env["crm.lead"].create(
            {
                "name": "Stage Restriction Lead - Unlisted",
                "team_id": team.id,
                "stage_id": stage_a.id,
            }
        )

        lead.write({"stage_id": stage_d.id})

        self.assertEqual(lead.stage_id, stage_d)

    def test_stage_restriction_requires_from_or_to_stage(self):
        """crm.team.stage_restriction must reject a line where both
        from_stage_id and to_stage_id are empty.
        """
        team = self.env["crm.team"].create(
            {"name": "Stage Restriction Test Team - Constraint"}
        )

        with self.assertRaises(ValidationError):
            self.env["crm.team.stage_restriction"].create({"team_id": team.id})
