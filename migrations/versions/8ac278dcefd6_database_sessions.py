"""database sessions

Revision ID: 8ac278dcefd6
Revises: c8fd9f1d6ba9
Create Date: 2021-09-05 10:53:23.470392

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = "8ac278dcefd6"
down_revision = "c8fd9f1d6ba9"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "flask_session",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(255), nullable=False),
        sa.Column("data", sa.LargeBinary()),
        sa.Column("expiry", sa.DateTime()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id"),
    )
    op.create_table(
        "flask_dance_oauthadmin",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("token", MutableDict.as_mutable(sa.JSON), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "flask_dance_oauthuser",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("token", MutableDict.as_mutable(sa.JSON), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("flask_session")
    op.drop_table("flask_dance_oauthadmin")
    op.drop_table("flask_dance_oauthuser")
