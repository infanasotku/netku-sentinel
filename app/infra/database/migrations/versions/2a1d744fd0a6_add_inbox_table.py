"""Add inbox table

Revision ID: 2a1d744fd0a6
Revises: 0761a4517a94
Create Date: 2025-10-04 22:17:07.365234

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "2a1d744fd0a6"
down_revision: Union[str, Sequence[str], None] = "0761a4517a94"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "inbox",
        sa.Column("message_id", sa.UUID(), nullable=False),
        sa.Column("received_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("message_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("inbox")
