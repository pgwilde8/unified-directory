"""Clean multi-tenant white-label directory platform

Revision ID: clean_multi_tenant
Revises: 
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'clean_multi_tenant'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create tenants table - Core multi-tenant organization
    op.create_table('tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column('subdomain', sa.String(length=100), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('favicon_url', sa.String(length=500), nullable=True),
        sa.Column('primary_color', sa.String(length=7), nullable=True),
        sa.Column('secondary_color', sa.String(length=7), nullable=True),
        sa.Column('custom_css', sa.Text(), nullable=True),
        sa.Column('theme', sa.JSON(), nullable=True),
        sa.Column('plan', sa.String(length=50), nullable=False, default='free'),
        sa.Column('plan_status', sa.String(length=20), nullable=False, default='active'),
        sa.Column('api_key_hash', sa.String(length=255), nullable=False),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('max_businesses', sa.Integer(), nullable=False, default=50),
        sa.Column('max_users', sa.Integer(), nullable=False, default=5),
        sa.Column('max_storage_mb', sa.Integer(), nullable=False, default=1024),
        sa.Column('trial_ends_at', sa.DateTime(), nullable=True),
        sa.Column('subscription_ends_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_suspended', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tenants_slug', 'tenants', ['slug'], unique=True)
    op.create_index('idx_tenants_domain', 'tenants', ['domain'], unique=True)
    op.create_index('idx_tenants_subdomain', 'tenants', ['subdomain'], unique=True)
    op.create_index('idx_tenants_api_key', 'tenants', ['api_key_hash'], unique=True)
    op.create_index('idx_tenants_plan_status', 'tenants', ['plan', 'plan_status'])
    op.create_index('idx_tenants_active', 'tenants', ['is_active', 'is_suspended'])

    # Create users table - Users within tenants
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False, default='member'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_users_tenant_email', 'users', ['tenant_id', 'email'], unique=True)
    op.create_index('idx_users_tenant_role', 'users', ['tenant_id', 'role'])
    op.create_index('idx_users_email', 'users', ['email'])

    # Create categories table - Business categories within tenants
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_categories_tenant_slug', 'categories', ['tenant_id', 'slug'], unique=True)
    op.create_index('idx_categories_tenant_parent', 'categories', ['tenant_id', 'parent_id'])
    op.create_index('idx_categories_tenant_sort', 'categories', ['tenant_id', 'sort_order'])

    # Create listings table - Business listings within tenants
    op.create_table('listings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('address_line1', sa.String(length=200), nullable=True),
        sa.Column('address_line2', sa.String(length=200), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=2), nullable=False, default='US'),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('business_hours', sa.JSON(), nullable=True),
        sa.Column('price_range', sa.String(length=10), nullable=True),
        sa.Column('amenities', sa.JSON(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('images', sa.JSON(), nullable=True),
        sa.Column('documents', sa.JSON(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_featured', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('featured_until', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, default='pending'),
        sa.Column('meta_title', sa.String(length=200), nullable=True),
        sa.Column('meta_description', sa.String(length=300), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_listings_tenant_slug', 'listings', ['tenant_id', 'slug'], unique=True)
    op.create_index('idx_listings_tenant_category', 'listings', ['tenant_id', 'category_id'])
    op.create_index('idx_listings_tenant_city', 'listings', ['tenant_id', 'city'])
    op.create_index('idx_listings_tenant_status', 'listings', ['tenant_id', 'status'])
    op.create_index('idx_listings_geo', 'listings', ['latitude', 'longitude'])
    op.create_index('idx_listings_featured', 'listings', ['is_featured', 'is_approved', 'is_active'])

    # Create reviews table - Customer reviews for listings
    op.create_table('reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('listing_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('reviewer_name', sa.String(length=100), nullable=True),
        sa.Column('reviewer_email', sa.String(length=255), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_approved', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_anonymous', sa.Boolean(), nullable=False, default=False),
        sa.Column('helpful_count', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['listing_id'], ['listings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_reviews_tenant_listing', 'reviews', ['tenant_id', 'listing_id'])
    op.create_index('idx_reviews_listing_rating', 'reviews', ['listing_id', 'rating'])
    op.create_index('idx_reviews_approved', 'reviews', ['is_approved'])

    # Create endorsements table - Customer endorsements
    op.create_table('endorsements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('listing_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('endorser_name', sa.String(length=100), nullable=True),
        sa.Column('endorser_email', sa.String(length=255), nullable=True),
        sa.Column('would_recommend', sa.Boolean(), nullable=False, default=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('transaction_hash', sa.String(length=255), nullable=False),
        sa.Column('ip_hash', sa.String(length=255), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_approved', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['listing_id'], ['listings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_endorsements_tenant_listing', 'endorsements', ['tenant_id', 'listing_id'])
    op.create_index('idx_endorsements_transaction', 'endorsements', ['transaction_hash'], unique=True)
    op.create_index('idx_endorsements_created', 'endorsements', ['created_at'])

    # Create moderation_reports table - Content moderation
    op.create_table('moderation_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('reporter_id', sa.Integer(), nullable=True),
        sa.Column('reason_code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('evidence_urls', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, default='pending'),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id']),
        sa.ForeignKeyConstraint(['reporter_id'], ['users.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_moderation_tenant_status', 'moderation_reports', ['tenant_id', 'status'])
    op.create_index('idx_moderation_target', 'moderation_reports', ['target_type', 'target_id'])
    op.create_index('idx_moderation_assigned', 'moderation_reports', ['assigned_to', 'status'])

    # Create audit_logs table - Complete audit trail
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=False),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_tenant_action', 'audit_logs', ['tenant_id', 'action'])
    op.create_index('idx_audit_tenant_created', 'audit_logs', ['tenant_id', 'created_at'])
    op.create_index('idx_audit_user_created', 'audit_logs', ['user_id', 'created_at'])

    # Create usage_meters table - Billing and usage tracking
    op.create_table('usage_meters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('month', sa.String(length=7), nullable=False),
        sa.Column('api_calls', sa.Integer(), nullable=False, default=0),
        sa.Column('listings_count', sa.Integer(), nullable=False, default=0),
        sa.Column('users_count', sa.Integer(), nullable=False, default=0),
        sa.Column('reviews_count', sa.Integer(), nullable=False, default=0),
        sa.Column('storage_mb', sa.Integer(), nullable=False, default=0),
        sa.Column('bandwidth_mb', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_usage_tenant_month', 'usage_meters', ['tenant_id', 'month'], unique=True)

    # Create billing_events table - Stripe webhook events
    op.create_table('billing_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('stripe_event_id', sa.String(length=255), nullable=False),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('event_data', sa.JSON(), nullable=False),
        sa.Column('processed', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_billing_tenant_type', 'billing_events', ['tenant_id', 'event_type'])
    op.create_index('idx_billing_stripe_event', 'billing_events', ['stripe_event_id'], unique=True)

    # Create tenant_settings table - Tenant-specific configuration
    op.create_table('tenant_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('value_type', sa.String(length=20), nullable=False, default='string'),
        sa.Column('is_public', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_settings_tenant_key', 'tenant_settings', ['tenant_id', 'key'], unique=True)
    op.create_index('idx_settings_public', 'tenant_settings', ['is_public'])

    # Create media_files table - File upload tracking
    op.create_table('media_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_url', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_media_tenant_type', 'media_files', ['tenant_id', 'file_type'])
    op.create_index('idx_media_uploaded_by', 'media_files', ['uploaded_by'])


def downgrade():
    # Drop tables in reverse order
    op.drop_table('media_files')
    op.drop_table('tenant_settings')
    op.drop_table('billing_events')
    op.drop_table('usage_meters')
    op.drop_table('audit_logs')
    op.drop_table('moderation_reports')
    op.drop_table('endorsements')
    op.drop_table('reviews')
    op.drop_table('listings')
    op.drop_table('categories')
    op.drop_table('users')
    op.drop_table('tenants')
