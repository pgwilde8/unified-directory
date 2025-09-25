"""Add multi-tenant models for white-label platform

Revision ID: b12d095220a3
Revises: 7dad4fa62aae
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b12d095220a3'
down_revision = '7dad4fa62aae'
branch_labels = None
depends_on = None


def upgrade():
    # Create tenants table
    op.create_table('tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('theme', sa.JSON(), nullable=True),
        sa.Column('plan', sa.String(length=50), nullable=True),
        sa.Column('plan_status', sa.String(length=20), nullable=True),
        sa.Column('api_key_hash', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tenants_domain_active', 'tenants', ['domain'], unique=False)
    op.create_index('idx_tenants_plan_status', 'tenants', ['plan', 'plan_status'], unique=False)
    op.create_index('idx_tenants_slug_active', 'tenants', ['slug'], unique=False)
    op.create_index(op.f('ix_tenants_api_key_hash'), 'tenants', ['api_key_hash'], unique=True)
    op.create_index(op.f('ix_tenants_domain'), 'tenants', ['domain'], unique=True)
    op.create_index(op.f('ix_tenants_id'), 'tenants', ['id'], unique=False)
    op.create_index(op.f('ix_tenants_name'), 'tenants', ['name'], unique=False)
    op.create_index(op.f('ix_tenants_slug'), 'tenants', ['slug'], unique=True)

    # Create categories table
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_categories_tenant_parent', 'categories', ['tenant_id', 'parent_id'], unique=False)
    op.create_index('idx_categories_tenant_slug', 'categories', ['tenant_id', 'slug'], unique=False)
    op.create_index('idx_categories_tenant_sort', 'categories', ['tenant_id', 'sort_order'], unique=False)
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=False)
    op.create_index(op.f('ix_categories_slug'), 'categories', ['slug'], unique=False)

    # Create members table
    op.create_table('members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('plan', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_members_tenant_email', 'members', ['tenant_id', 'email'], unique=False)
    op.create_index('idx_members_tenant_status', 'members', ['tenant_id', 'status'], unique=False)
    op.create_index(op.f('ix_members_email'), 'members', ['email'], unique=False)
    op.create_index(op.f('ix_members_id'), 'members', ['id'], unique=False)

    # Create usage_meters table
    op.create_table('usage_meters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('month', sa.String(length=7), nullable=False),
        sa.Column('api_calls', sa.Integer(), nullable=True),
        sa.Column('listings_count', sa.Integer(), nullable=True),
        sa.Column('members_count', sa.Integer(), nullable=True),
        sa.Column('storage_mb', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_usage_tenant_month', 'usage_meters', ['tenant_id', 'month'], unique=False)
    op.create_index(op.f('ix_usage_meters_id'), 'usage_meters', ['id'], unique=False)
    op.create_index(op.f('ix_usage_meters_month'), 'usage_meters', ['month'], unique=False)

    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('actor_user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('meta_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['actor_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_actor_created', 'audit_logs', ['actor_user_id', 'created_at'], unique=False)
    op.create_index('idx_audit_tenant_action', 'audit_logs', ['tenant_id', 'action'], unique=False)
    op.create_index('idx_audit_tenant_created', 'audit_logs', ['tenant_id', 'created_at'], unique=False)
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_audit_logs_target_id'), 'audit_logs', ['target_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_target_type'), 'audit_logs', ['target_type'], unique=False)

    # Create listings table
    op.create_table('listings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('addr_line1', sa.String(length=200), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('region', sa.String(length=100), nullable=True),
        sa.Column('postal', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=2), nullable=True),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lng', sa.Float(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('hours_json', sa.JSON(), nullable=True),
        sa.Column('images_json', sa.JSON(), nullable=True),
        sa.Column('featured_until', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_listings_geo', 'listings', ['lat', 'lng'], unique=False)
    op.create_index('idx_listings_tenant_category', 'listings', ['tenant_id', 'category_id'], unique=False)
    op.create_index('idx_listings_tenant_city', 'listings', ['tenant_id', 'city'], unique=False)
    op.create_index('idx_listings_tenant_slug', 'listings', ['tenant_id', 'slug'], unique=False)
    op.create_index('idx_listings_tenant_status', 'listings', ['tenant_id', 'status'], unique=False)
    op.create_index(op.f('ix_listings_city'), 'listings', ['city'], unique=False)
    op.create_index(op.f('ix_listings_country'), 'listings', ['country'], unique=False)
    op.create_index(op.f('ix_listings_id'), 'listings', ['id'], unique=False)
    op.create_index(op.f('ix_listings_lat'), 'listings', ['lat'], unique=False)
    op.create_index(op.f('ix_listings_lng'), 'listings', ['lng'], unique=False)
    op.create_index(op.f('ix_listings_name'), 'listings', ['name'], unique=False)
    op.create_index(op.f('ix_listings_postal'), 'listings', ['postal'], unique=False)
    op.create_index(op.f('ix_listings_region'), 'listings', ['region'], unique=False)
    op.create_index(op.f('ix_listings_slug'), 'listings', ['slug'], unique=False)

    # Create moderation_reports table
    op.create_table('moderation_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('reason_code', sa.String(length=50), nullable=False),
        sa.Column('evidence_urls', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_moderation_assigned', 'moderation_reports', ['assigned_to', 'status'], unique=False)
    op.create_index('idx_moderation_tenant_status', 'moderation_reports', ['tenant_id', 'status'], unique=False)
    op.create_index('idx_moderation_tenant_type', 'moderation_reports', ['tenant_id', 'target_type'], unique=False)
    op.create_index(op.f('ix_moderation_reports_id'), 'moderation_reports', ['id'], unique=False)
    op.create_index(op.f('ix_moderation_reports_reason_code'), 'moderation_reports', ['reason_code'], unique=False)
    op.create_index(op.f('ix_moderation_reports_target_id'), 'moderation_reports', ['target_id'], unique=False)
    op.create_index(op.f('ix_moderation_reports_target_type'), 'moderation_reports', ['target_type'], unique=False)

    # Create endorsements table
    op.create_table('endorsements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('listing_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('would_repeat', sa.Boolean(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('txn_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('ip_hash', sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(['listing_id'], ['listings.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_endorsements_tenant_created', 'endorsements', ['tenant_id', 'created_at'], unique=False)
    op.create_index('idx_endorsements_tenant_listing', 'endorsements', ['tenant_id', 'listing_id'], unique=False)
    op.create_index('idx_endorsements_txn_hash', 'endorsements', ['txn_hash'], unique=True)
    op.create_index(op.f('ix_endorsements_id'), 'endorsements', ['id'], unique=False)
    op.create_index(op.f('ix_endorsements_ip_hash'), 'endorsements', ['ip_hash'], unique=False)

    # Modify users table for multi-tenancy
    # First add columns as nullable
    op.add_column('users', sa.Column('pw_hash', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('role', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('tenant_id', sa.Integer(), nullable=True))
    
    # Create a default tenant for existing users
    op.execute("INSERT INTO tenants (slug, name, plan, plan_status, created_at) VALUES ('default', 'Default Tenant', 'free', 'active', NOW())")
    
    # Update existing users with default values
    op.execute("UPDATE users SET pw_hash = 'legacy_user', role = 'owner', tenant_id = (SELECT id FROM tenants WHERE slug = 'default') WHERE pw_hash IS NULL")
    
    # Now make columns NOT NULL
    op.alter_column('users', 'pw_hash', nullable=False)
    op.alter_column('users', 'tenant_id', nullable=False)
    op.create_foreign_key(None, 'users', 'tenants', ['tenant_id'], ['id'])
    op.create_index('idx_users_tenant_email', 'users', ['tenant_id', 'email'], unique=False)
    op.create_index('idx_users_tenant_role', 'users', ['tenant_id', 'role'], unique=False)
    op.drop_index('idx_users_email_active', table_name='users')
    op.drop_index('idx_users_google_id', table_name='users')
    op.drop_index('ix_users_google_id', table_name='users')
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.drop_column('users', 'name')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'phone')
    op.drop_column('users', 'profile_picture')
    op.drop_column('users', 'google_id')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'is_admin')

    # Drop old business tables
    op.drop_table('business_reviews')
    op.drop_table('system_settings')
    op.drop_table('business_claims')
    op.drop_table('business_analytics')
    op.drop_table('businesses')


def downgrade():
    # Recreate old business tables
    op.create_table('businesses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('address', sa.String(length=300), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=2), nullable=True),
        sa.Column('zip_code', sa.String(length=10), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('hours', sa.JSON(), nullable=True),
        sa.Column('price_range', sa.String(length=10), nullable=True),
        sa.Column('amenities', sa.JSON(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('images', sa.JSON(), nullable=True),
        sa.Column('documents', sa.JSON(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('slug', sa.String(length=200), nullable=True),
        sa.Column('meta_description', sa.String(length=300), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_businesses_approved_active', 'businesses', ['is_approved', 'is_active'], unique=False)
    op.create_index('idx_businesses_category_city', 'businesses', ['category', 'city'], unique=False)
    op.create_index('idx_businesses_featured', 'businesses', ['is_featured', 'is_approved', 'is_active'], unique=False)
    op.create_index('idx_businesses_owner_approved', 'businesses', ['owner_id', 'is_approved'], unique=False)
    op.create_index('idx_businesses_state_city', 'businesses', ['state', 'city'], unique=False)
    op.create_index(op.f('ix_businesses_category'), 'businesses', ['category'], unique=False)
    op.create_index(op.f('ix_businesses_city'), 'businesses', ['city'], unique=False)
    op.create_index(op.f('ix_businesses_id'), 'businesses', ['id'], unique=False)
    op.create_index(op.f('ix_businesses_name'), 'businesses', ['name'], unique=False)
    op.create_index(op.f('ix_businesses_slug'), 'businesses', ['slug'], unique=True)
    op.create_index(op.f('ix_businesses_state'), 'businesses', ['state'], unique=False)

    # Restore users table
    op.add_column('users', sa.Column('google_id', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('name', sa.String(length=200), nullable=True))
    op.add_column('users', sa.Column('profile_picture', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('phone', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_index('idx_users_tenant_email', table_name='users')
    op.drop_index('idx_users_tenant_role', table_name='users')
    op.create_index('idx_users_email_active', 'users', ['email', 'is_active'], unique=False)
    op.create_index('idx_users_google_id', 'users', ['google_id'], unique=False)
    op.create_index('ix_users_google_id', 'users', ['google_id'], unique=True)
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.drop_column('users', 'pw_hash')
    op.drop_column('users', 'role')
    op.drop_column('users', 'tenant_id')

    # Drop multi-tenant tables
    op.drop_table('endorsements')
    op.drop_table('moderation_reports')
    op.drop_table('listings')
    op.drop_table('audit_logs')
    op.drop_table('usage_meters')
    op.drop_table('members')
    op.drop_table('categories')
    op.drop_table('tenants')
