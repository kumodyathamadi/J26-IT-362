"""Add auditable Component 2 evaluation records.

Revision ID: 2026_10_14_0002
Revises: 2026_09_26_0001
Create Date: 2026-10-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "2026_10_14_0002"
down_revision: Union[str, None] = "2026_09_26_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    portable_json = sa.JSON().with_variant(
        postgresql.JSONB(astext_type=sa.Text()), "postgresql"
    )
    op.create_table(
        "compliance_evaluation_records",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("business_context", portable_json, nullable=False),
        sa.Column("result", portable_json, nullable=False),
        sa.Column("retrieval_mode", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_compliance_evaluation_records_created_at"),
        "compliance_evaluation_records",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_compliance_evaluation_records_created_at"),
        table_name="compliance_evaluation_records",
    )
    op.drop_table("compliance_evaluation_records")
