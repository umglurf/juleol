# SPDX-FileCopyrightText: 2020 Håvard Moen <post@haavard.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""add tasting lock

Revision ID: c8fd9f1d6ba9
Revises: 8eb7162afee7
Create Date: 2020-11-08 10:13:30.894263

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8fd9f1d6ba9'
down_revision = '8eb7162afee7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('tastings', sa.Column('locked', sa.Boolean(), nullable=False, default=False))


def downgrade():
    op.drop_column('tastings', 'locked')
