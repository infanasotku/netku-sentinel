"""Add subscribers table

Revision ID: f99599389652
Revises: 2a1d744fd0a6
Create Date: 2025-10-04 22:55:53.476149

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "f99599389652"
down_revision: Union[str, Sequence[str], None] = "2a1d744fd0a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "subscribers",
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("subscribers")
