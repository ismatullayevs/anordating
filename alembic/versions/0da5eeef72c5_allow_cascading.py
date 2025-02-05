"""Allow cascading

Revision ID: 0da5eeef72c5
Revises: 554c980de01f
Create Date: 2025-02-05 18:02:20.621684

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0da5eeef72c5"
down_revision: Union[str, None] = "554c980de01f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_reaction_from_user_uuid_id", table_name="reaction")
    op.drop_index("ix_reaction_to_user_uuid_id", table_name="reaction")
    op.drop_index("ix_report_to_user_uuid_id", table_name="report")
    op.drop_index("ix_report_from_user_uuid_id", table_name="report")
    op.drop_index("ix_user_preferences_user_uuid_id", table_name="user_preferences")
    op.drop_index("ix_user_media_user_uuid_id", table_name="user_media")

    op.drop_constraint("fk_reaction_from_user_id_user_account", "reaction")
    op.drop_constraint("fk_reaction_to_user_id_user_account", "reaction")
    op.drop_constraint("fk_report_to_user_id_user_account", "report")
    op.drop_constraint("fk_report_from_user_id_user_account", "report")
    op.drop_constraint("fk_user_media_user_id_user_account", "user_media")
    op.drop_constraint("fk_user_preferences_user_id_user_account", "user_preferences")

    op.drop_constraint("uq_user_account_uuid_id", table_name="user_account")


def downgrade() -> None:
    pass
