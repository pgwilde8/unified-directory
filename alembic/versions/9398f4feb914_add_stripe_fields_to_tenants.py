"""add_stripe_fields_to_tenants

Revision ID: 9398f4feb914
Revises: dad73c185fa4
Create Date: 2025-09-24 12:42:20.995473

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9398f4feb914'
down_revision = 'dad73c185fa4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add Stripe fields to tenants table
    op.add_column('tenants', sa.Column('stripe_customer_id', sa.String(255), nullable=True))
    op.add_column('tenants', sa.Column('subscription_id', sa.String(255), nullable=True))
    
    # Create indexes for Stripe fields
    op.create_index('idx_tenants_stripe_customer_id', 'tenants', ['stripe_customer_id'])
    op.create_index('idx_tenants_subscription_id', 'tenants', ['subscription_id'])


def downgrade() -> None:
    # Remove indexes
    op.drop_index('idx_tenants_subscription_id', table_name='tenants')
    op.drop_index('idx_tenants_stripe_customer_id', table_name='tenants')
    
    # Remove Stripe fields
    op.drop_column('tenants', 'subscription_id')
    op.drop_column('tenants', 'stripe_customer_id')
