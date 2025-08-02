"""Make user_pk UUID

Revision ID: 554c980de01f
Revises: ae1b6a06cfff
Create Date: 2025-02-02 07:08:19.097727

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import column, table

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "554c980de01f"
down_revision: Union[str, None] = "ae1b6a06cfff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_account",
        sa.Column("uuid_id", UUID(as_uuid=True), unique=True, nullable=True),
    )

    connection = op.get_bind()

    users_table = table(
        "user_account", column("id", sa.Integer), column("uuid_id", UUID(as_uuid=True))
    )

    connection.execute(
        users_table.update().values(uuid_id=sa.text("gen_random_uuid()"))
    )

    op.add_column(
        "user_preferences",
        sa.Column("user_uuid_id", UUID(as_uuid=True), index=True, nullable=True),
    )
    op.add_column(
        "reaction",
        sa.Column("from_user_uuid_id", UUID(as_uuid=True), index=True, nullable=True),
    )
    op.add_column(
        "reaction",
        sa.Column("to_user_uuid_id", UUID(as_uuid=True), index=True, nullable=True),
    )
    op.add_column(
        "report",
        sa.Column("from_user_uuid_id", UUID(as_uuid=True), index=True, nullable=True),
    )
    op.add_column(
        "report",
        sa.Column("to_user_uuid_id", UUID(as_uuid=True), index=True, nullable=True),
    )
    op.add_column(
        "user_media",
        sa.Column("user_uuid_id", UUID(as_uuid=True), index=True, nullable=True),
    )

    connection.execute(
        text(
            """
        UPDATE user_preferences
        SET user_uuid_id = user_account.uuid_id
        FROM user_account
        WHERE user_preferences.user_id = user_account.id
    """
        )
    )

    connection.execute(
        text(
            """
        UPDATE reaction
        SET from_user_uuid_id = user_account.uuid_id
        FROM user_account
        WHERE reaction.from_user_id = user_account.id 
    """
        )
    )

    connection.execute(
        text(
            """
        UPDATE reaction
        SET to_user_uuid_id = user_account.uuid_id
        FROM user_account
        WHERE reaction.to_user_id = user_account.id 
    """
        )
    )

    connection.execute(
        text(
            """
        UPDATE report
        SET from_user_uuid_id = user_account.uuid_id
        FROM user_account
        WHERE report.from_user_id = user_account.id 
    """
        )
    )

    connection.execute(
        text(
            """
        UPDATE report
        SET to_user_uuid_id = user_account.uuid_id
        FROM user_account
        WHERE report.to_user_id = user_account.id 
    """
        )
    )

    connection.execute(
        text(
            """
        UPDATE user_media
        SET user_uuid_id = user_account.uuid_id
        FROM user_account
        WHERE user_media.user_id = user_account.id 
    """
        )
    )

    op.drop_constraint(
        "fk_user_preferences_user_id_user_account",
        "user_preferences",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_reaction_from_user_id_user_account", "reaction", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_reaction_to_user_id_user_account", "reaction", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_report_from_user_id_user_account", "report", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_report_to_user_id_user_account", "report", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_user_media_user_id_user_account", "user_media", type_="foreignkey"
    )

    op.alter_column("user_account", "uuid_id", nullable=False)
    op.alter_column("user_preferences", "user_uuid_id", nullable=False)
    op.alter_column("reaction", "from_user_uuid_id", nullable=False)
    op.alter_column("reaction", "to_user_uuid_id", nullable=False)
    op.alter_column("report", "from_user_uuid_id", nullable=False)
    op.alter_column("report", "to_user_uuid_id", nullable=False)
    op.alter_column("user_media", "user_uuid_id", nullable=False)

    op.drop_column("user_account", "id")
    op.alter_column("user_account", "uuid_id", new_column_name="id")
    op.drop_column("user_preferences", "user_id")
    op.alter_column("user_preferences", "user_uuid_id", new_column_name="user_id")
    op.drop_column("reaction", "from_user_id")
    op.alter_column("reaction", "from_user_uuid_id", new_column_name="from_user_id")
    op.drop_column("reaction", "to_user_id")
    op.alter_column("reaction", "to_user_uuid_id", new_column_name="to_user_id")
    op.drop_column("report", "from_user_id")
    op.alter_column("report", "from_user_uuid_id", new_column_name="from_user_id")
    op.drop_column("report", "to_user_id")
    op.alter_column("report", "to_user_uuid_id", new_column_name="to_user_id")
    op.drop_column("user_media", "user_id")
    op.alter_column("user_media", "user_uuid_id", new_column_name="user_id")

    op.create_foreign_key(
        "fk_user_preferences_user_id_user_account",
        "user_preferences",
        "user_account",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_reaction_from_user_id_user_account",
        "reaction",
        "user_account",
        ["from_user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_reaction_to_user_id_user_account",
        "reaction",
        "user_account",
        ["to_user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_report_from_user_id_user_account",
        "report",
        "user_account",
        ["from_user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_report_to_user_id_user_account",
        "report",
        "user_account",
        ["to_user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_user_media_user_id_user_account",
        "user_media",
        "user_account",
        ["user_id"],
        ["id"],
    )

    op.create_primary_key("pk_user_account", "user_account", ["id"])


def downgrade() -> None:
    # Create temporary integer ID columns
    op.add_column(
        "user_account",
        sa.Column(
            "int_id", sa.Integer(), unique=True, autoincrement=True, nullable=True
        ),
    )

    # Create sequence for autoincrement
    # op.execute("CREATE SEQUENCE user_account_id_seq")

    # Add temporary integer columns to all related tables
    op.add_column(
        "user_preferences", sa.Column("user_int_id", sa.Integer(), nullable=True)
    )
    op.add_column(
        "reaction", sa.Column("from_user_int_id", sa.Integer(), nullable=True)
    )
    op.add_column("reaction", sa.Column("to_user_int_id", sa.Integer(), nullable=True))
    op.add_column("report", sa.Column("from_user_int_id", sa.Integer(), nullable=True))
    op.add_column("report", sa.Column("to_user_int_id", sa.Integer(), nullable=True))
    op.add_column("user_media", sa.Column("user_int_id", sa.Integer(), nullable=True))

    # Drop the primary key constraint
    op.drop_constraint("pk_user_account", "user_account", type_="primary")

    # Populate user_account with sequential IDs
    connection = op.get_bind()
    connection.execute(
        text(
            """
            UPDATE user_account
            SET int_id = nextval('user_account_id_seq')
        """
        )
    )

    # Update all foreign key references
    connection.execute(
        text(
            """
            UPDATE user_preferences up
            SET user_int_id = ua.int_id
            FROM user_account ua
            WHERE up.user_id = ua.id
        """
        )
    )

    connection.execute(
        text(
            """
            UPDATE reaction r
            SET from_user_int_id = ua.int_id,
                to_user_int_id = ua2.int_id
            FROM user_account ua, user_account ua2
            WHERE r.from_user_id = ua.id
            AND r.to_user_id = ua2.id
        """
        )
    )

    connection.execute(
        text(
            """
            UPDATE report r
            SET from_user_int_id = ua.int_id,
                to_user_int_id = ua2.int_id
            FROM user_account ua, user_account ua2
            WHERE r.from_user_id = ua.id
            AND r.to_user_id = ua2.id
        """
        )
    )

    connection.execute(
        text(
            """
            UPDATE user_media um
            SET user_int_id = ua.int_id
            FROM user_account ua
            WHERE um.user_id = ua.id
        """
        )
    )

    # Drop existing foreign key constraints
    op.drop_constraint(
        "fk_user_preferences_user_id_user_account",
        "user_preferences",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_reaction_from_user_id_user_account", "reaction", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_reaction_to_user_id_user_account", "reaction", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_report_from_user_id_user_account", "report", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_report_to_user_id_user_account", "report", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_user_media_user_id_user_account", "user_media", type_="foreignkey"
    )

    # Make integer columns not nullable
    op.alter_column("user_account", "int_id", nullable=False)
    op.alter_column("user_preferences", "user_int_id", nullable=False)
    op.alter_column("reaction", "from_user_int_id", nullable=False)
    op.alter_column("reaction", "to_user_int_id", nullable=False)
    op.alter_column("report", "from_user_int_id", nullable=False)
    op.alter_column("report", "to_user_int_id", nullable=False)
    op.alter_column("user_media", "user_int_id", nullable=False)

    # Drop UUID columns and rename integer columns
    op.drop_column("user_account", "id")
    op.alter_column("user_account", "int_id", new_column_name="id")
    op.drop_column("user_preferences", "user_id")
    op.alter_column("user_preferences", "user_int_id", new_column_name="user_id")
    op.drop_column("reaction", "from_user_id")
    op.alter_column("reaction", "from_user_int_id", new_column_name="from_user_id")
    op.drop_column("reaction", "to_user_id")
    op.alter_column("reaction", "to_user_int_id", new_column_name="to_user_id")
    op.drop_column("report", "from_user_id")
    op.alter_column("report", "from_user_int_id", new_column_name="from_user_id")
    op.drop_column("report", "to_user_id")
    op.alter_column("report", "to_user_int_id", new_column_name="to_user_id")
    op.drop_column("user_media", "user_id")
    op.alter_column("user_media", "user_int_id", new_column_name="user_id")

    # Set up autoincrement
    op.alter_column(
        "user_account",
        "id",
        server_default=sa.text("nextval('user_account_id_seq'::regclass)"),
    )

    # Create new primary key
    op.create_primary_key("pk_user_account", "user_account", ["id"])

    # Recreate foreign key constraints
    op.create_foreign_key(
        "fk_user_preferences_user_id_user_account",
        "user_preferences",
        "user_account",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_reaction_from_user_id_user_account",
        "reaction",
        "user_account",
        ["from_user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_reaction_to_user_id_user_account",
        "reaction",
        "user_account",
        ["to_user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_report_from_user_id_user_account",
        "report",
        "user_account",
        ["from_user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_report_to_user_id_user_account",
        "report",
        "user_account",
        ["to_user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_user_media_user_id_user_account",
        "user_media",
        "user_account",
        ["user_id"],
        ["id"],
    )
