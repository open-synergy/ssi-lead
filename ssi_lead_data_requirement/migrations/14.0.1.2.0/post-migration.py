# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# Migration: 14.0.1.1.0 -> 14.0.1.2.0
#
# Changes: data_requirement_ids on crm.lead was a Many2many stored in
#          junction table rel_lead_2_data_requirement.
#          Migrate rows into data_requirement.document (table:
#          data_requirement_document).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

_OLD_JUNCTION_TABLE = "rel_lead_2_data_requirement"
_RES_MODEL = "crm.lead"


def _migrate_junction_table(cr):
    openupgrade.logged_query(
        cr,
        """
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = %s
        """,
        (_OLD_JUNCTION_TABLE,),
    )
    if not cr.fetchone():
        _logger.info(
            "Table %s does not exist, skipping migration.", _OLD_JUNCTION_TABLE
        )
        return

    openupgrade.logged_query(
        cr,
        f"""
        INSERT INTO data_requirement_document (res_model, res_id, data_requirement_id)
        SELECT %s, lead_id, data_requirement_id
        FROM {_OLD_JUNCTION_TABLE}
        ON CONFLICT DO NOTHING
        """,
        (_RES_MODEL,),
    )
    _logger.info(
        "Migrated rows from %s into data_requirement_document.", _OLD_JUNCTION_TABLE
    )


@openupgrade.migrate()
def migrate(env, version):
    _migrate_junction_table(env.cr)
