"""Add engine_subscriptions table

Revision ID: 41ad9e0c868a
Revises: f99599389652
Create Date: 2025-10-05 11:14:58.965175

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "41ad9e0c868a"
down_revision: Union[str, Sequence[str], None] = "f99599389652"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "engine_subscriptions",
        sa.Column("subscriber_id", sa.UUID(), nullable=False),
        sa.Column("channel", sa.String(), nullable=False),
        sa.Column("endpoint", sa.String(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("engine_host", sa.String(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["subscriber_id"],
            ["subscribers.id"],
        ),
        sa.PrimaryKeyConstraint("subscriber_id", "id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("engine_subscriptions")
