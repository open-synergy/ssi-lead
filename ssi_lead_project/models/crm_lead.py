# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import fields, models


class CrmLead(models.Model):
    _name = "crm.lead"
    _inherit = [
        "crm.lead",
        "mixin.task",
    ]
    _task_create_page = True
    _task_page_xpath = "//page[1]"
    _task_template_position = "after"

    task_ids = fields.Many2many(
        relation="rel_lead_2_task",
        column1="lead_id",
        column2="task_id",
    )
