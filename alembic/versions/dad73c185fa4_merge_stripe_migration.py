"""merge_stripe_migration

Revision ID: dad73c185fa4
Revises: b12d095220a3, clean_multi_tenant
Create Date: 2025-09-24 12:41:09.075028

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dad73c185fa4'
down_revision = ('b12d095220a3', 'clean_multi_tenant')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
