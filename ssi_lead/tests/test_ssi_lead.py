# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSsiLead(YamlTransactionCase):
    def test_ssi_lead(self):
        self.run_yaml_scenario("test_data_ssi_lead.yaml")

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
        self.env.invalidate_all()

        self.assertEqual(
            reminder.reminder_count,
            1,
            "reminder_count must be 1 in DB after the first send",
        )

        # Second check — cache was cleared, so guard reads reminder_count from
        # DB.  If the fix is correct, reminder_count == 1 >= number_of_reminder
        # == 1, so no notification is sent.
        lead._check_and_send_reminders()
        self.env.invalidate_all()

        self.assertEqual(
            reminder.reminder_count,
            1,
            "reminder_count must NOT increase beyond number_of_reminder after "
            "the cache is cleared between checks",
        )
