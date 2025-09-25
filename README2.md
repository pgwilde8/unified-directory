# 🏢 White-label Multi-tenant Business Directory Platform

A production-ready, white-label business directory platform that allows customers to run their own directories on custom domains. Built with FastAPI, PostgreSQL, and modern web technologies following the master project specifications.

## 🌟 Platform Features

- **Multi-tenant Architecture** - Complete tenant isolation with row-level security
- **Custom Domain Support** - Each tenant can use their own domain
- **White-label API** - Complete RESTful API for tenant management
- **Stripe Billing Integration** - Subscription management and plan enforcement
- **S3-compatible Storage** - DigitalOcean Spaces for file uploads
- **PostGIS Support** - Geographic search and location-based queries
- **Role-based Access Control** - Owner, admin, and editor roles
- **Moderation System** - Content moderation and audit logging
- **Rate Limiting** - Per-tenant API rate limiting
- **Hosted Admin Portal** - Tenant management interface

## 🚀 Quick Start

### Access URLs
- **Platform API**: `http://24.144.67.150:9179/`
- **API Documentation**: `http://24.144.67.150:9179/api/docs`
- **Health Check**: `http://24.144.67.150:9179/api/health`
- **Platform Stats**: `http://24.144.67.150:9179/api/stats`

### Database Access
- **Host**: `localhost`
- **Username**: `adminwatch`
- **Password**: `adminwatch123`
- **Database**: `directory_tenant`

## 🛠️ System Management

### Service Commands

```bash
# Start Multi-tenant Platform
export DATABASE_URL="postgresql://adminwatch:adminwatch123@localhost:5432/directory_tenant"
uvicorn backend.main_tenant:app --host 0.0.0.0 --port 9179 --reload

# Or run directly
python -m backend.main_tenant
```

### Database Management

```bash
# Connect to Multi-tenant Database
psql -h localhost -U adminwatch -d directory_tenant
# Password: adminwatch123

# Run Migrations
export DATABASE_URL="postgresql://adminwatch:adminwatch123@localhost:5432/directory_tenant"
alembic upgrade head
```

## 📊 API Endpoints (v1)

### Authentication
- `POST /v1/auth/register` - Register new tenant owner
- `POST /v1/auth/login` - Login tenant owner
- `GET /v1/tenants/me` - Get current tenant information
- `POST /v1/tenants/{id}/apikey/rotate` - Rotate API key (owner only)

### Business Listings
- `POST /v1/listings` - Create business listing
- `GET /v1/listings` - Search listings with filters and geo search
- `GET /v1/listings/{id}` - Get specific listing
- `PUT /v1/listings/{id}` - Update listing
- `DELETE /v1/listings/{id}` - Delete listing

### Endorsements
- `POST /v1/endorsements` - Create customer endorsement
- `GET /v1/endorsements` - Get endorsements with filters

### Media & Billing
- `POST /v1/media/upload` - Upload media files (S3 signed URL)
- `POST /v1/billing/checkout-session` - Create Stripe checkout session
- `POST /v1/billing/webhook` - Handle Stripe webhooks
- `GET /v1/usage/me` - Get tenant usage metrics

### System
- `GET /v1/healthz` - Health check endpoint

## 🗄️ Database Schema

### Multi-tenant Tables
- **tenants** - Tenant organizations with custom domains and billing
- **users** - Users within tenants (owner, admin, editor roles)
- **listings** - Business listings with geo-location support
- **categories** - Hierarchical business categories
- **endorsements** - Customer endorsements with anti-spam
- **moderation_reports** - Content moderation system
- **audit_logs** - Complete audit trail
- **usage_meters** - Tenant usage tracking
- **members** - Optional member management
                List of relations
 Schema |        Name        | Type  |   Owner   
--------+--------------------+-------+-----------
 public | alembic_version    | table | dir-admin
 public | audit_logs         | table | dir-admin
 public | billing_events     | table | dir-admin
 public | categories         | table | dir-admin
 public | endorsements       | table | dir-admin
 public | listings           | table | dir-admin
 public | media_files        | table | dir-admin
 public | moderation_reports | table | dir-admin
 public | reviews            | table | dir-admin
 public | tenant_settings    | table | dir-admin
 public | tenants            | table | dir-admin
 public | usage_meters       | table | dir-admin
 public | users              | table | dir-admin
(13 rows)

### Key Features
- **Row-level Security** - All data scoped by tenant_id
- **Custom Domain Mapping** - Tenants can use custom domains
- **Plan-based Limits** - Enforced via Stripe subscriptions
- **Geographic Search** - PostGIS support for location queries
- **Anti-spam Protection** - Transaction hashing and IP tracking

## 🔧 Configuration

### Environment Variables

Key configuration in `env.tenant` file:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://adminwatch:adminwatch123@localhost:5432/directory_tenant

# Platform
APP_ENV=prod
SECRET_KEY=your_secret_key_here
BASE_DOMAIN=yourplatform.com

# Stripe Billing
STRIPE_SECRET=sk_live_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# S3 Storage (DigitalOcean Spaces)
STORAGE_BUCKET=labs-directory
STORAGE_REGION=us-east-1
STORAGE_ENDPOINT=https://white-label-club.sfo3.digitaloceanspaces.com
STORAGE_ACCESS_KEY=your_digitalocean_spaces_access_key
STORAGE_SECRET_KEY=your_digitalocean_spaces_secret_key

# Redis (Rate Limiting)
REDIS_URL=redis://localhost:6379/0

# PostGIS
POSTGIS_ENABLED=true

# API Limits
API_RATE_LIMIT_PER_SECOND=10
API_RATE_LIMIT_BURST=100
```

## 📁 Project Structure

```
/opt/webwise/directory/
├── backend/
│   ├── main_tenant.py           # Multi-tenant FastAPI application
│   ├── routes/
│   │   └── tenant_api.py        # White-label API endpoints
│   ├── schemas/
│   │   └── tenant_schemas.py    # Pydantic models
│   ├── core/
│   │   └── config.py            # Configuration settings
│   └── middleware.py            # Custom middleware
├── database/
│   ├── tenant_models.py         # Multi-tenant database models
│   ├── business_models.py       # Legacy business models
│   ├── models.py                # Legacy models
│   └── database.py              # Database connection
├── alembic/                     # Database migrations
├── env.tenant                   # Multi-tenant environment config
├── env.tenant.example           # Environment template
└── requirements.txt             # Python dependencies
```

## 🔐 Security & Multi-tenancy

### Tenant Isolation
- **Database-level isolation** with tenant_id foreign keys
- **API key authentication** per tenant
- **Custom domain resolution** for tenant routing
- **Row-level security** enforced at application level

### Authentication & Authorization
- **JWT tokens** for user authentication
- **API keys** for tenant authentication
- **Role-based access control** (owner, admin, editor)
- **Rate limiting** per tenant (10 req/s, 100 burst)

### Data Protection
- **Input validation** with Pydantic
- **SQL injection protection** via SQLAlchemy ORM
- **CORS protection** configured per tenant
- **Audit logging** for all actions

## 💰 Billing & Subscriptions

### Subscription Plans
- **Free** - 50 businesses, basic features
- **Premium** - 200 businesses, advanced features  
- **Pro** - Unlimited businesses, white-label features

### Stripe Integration
- **Automatic billing** via Stripe subscriptions
- **Webhook handling** for plan changes
- **Usage tracking** and enforcement
- **Custom domain SSL** management

## 🌍 Geographic Features

### PostGIS Support
- **Location-based search** with radius queries
- **Distance sorting** and filtering
- **Geographic indexing** for performance
- **Coordinate validation** and storage

### Search Capabilities
- **Text search** across listings
- **Category filtering** with hierarchies
- **Geographic radius** search
- **Sorting options** (relevance, distance, name, date)

## 🚀 Deployment

### Production Setup

1. **Configure environment** variables in `env.tenant`
2. **Set up Stripe** products and webhooks
3. **Configure DigitalOcean Spaces** for storage
4. **Set up Redis** for rate limiting
5. **Enable PostGIS** extension in PostgreSQL
6. **Configure nginx** for custom domain routing
7. **Set up SSL certificates** for custom domains

### Nginx Configuration

```nginx
# Custom domain routing
server {
    listen 80;
    server_name *.yourplatform.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name *.yourplatform.com;
    
    # SSL configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:9179;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🧪 Testing

### API Testing

```bash
# Register new tenant
curl -X POST "http://24.144.67.150:9179/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "owner@example.com",
    "password": "securepassword",
    "tenant_name": "Example Directory",
    "tenant_slug": "example-dir"
  }'

# Login tenant
curl -X POST "http://24.144.67.150:9179/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "owner@example.com",
    "password": "securepassword"
  }'

# Create business listing
curl -X POST "http://24.144.67.150:9179/v1/listings" \
  -H "Authorization: Bearer sk_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example Business",
    "description": "A great business",
    "category_id": 1,
    "city": "New York",
    "state": "NY"
  }'
```

## 📈 Monitoring & Analytics

### Health Monitoring
- **Health check endpoint** at `/v1/healthz`
- **Platform statistics** at `/api/stats`
- **Database connectivity** monitoring
- **Redis connectivity** monitoring
- **Storage connectivity** monitoring

### Usage Tracking
- **API call counting** per tenant
- **Storage usage** tracking
- **Business listing** limits
- **User count** limits
- **Monthly usage** reports

## 🔄 Migration from Legacy

### Database Migration
The platform uses a separate database (`directory_tenant`) to avoid conflicts with the legacy system:

```bash
# Legacy system (port 9178)
DATABASE_URL=postgresql://adminwatch:adminwatch123@localhost:5432/directory

# Multi-tenant platform (port 9179)  
DATABASE_URL=postgresql://adminwatch:adminwatch123@localhost:5432/directory_tenant
```

### Data Migration
To migrate existing data from the legacy system:
1. Export data from legacy database
2. Transform data to multi-tenant format
3. Import into new database with tenant assignment
4. Update API endpoints to use new system

## 🐛 Troubleshooting

### Common Issues

1. **Database connection issues**
   ```bash
   psql -h localhost -U adminwatch -d directory_tenant
   ```

2. **Migration issues**
   ```bash
   export DATABASE_URL="postgresql://adminwatch:adminwatch123@localhost:5432/directory_tenant"
   alembic upgrade head
   ```

3. **Port conflicts**
   ```bash
   sudo netstat -tlnp | grep 9179
   ```

4. **API key issues**
   - Check tenant API key in database
   - Verify Authorization header format
   - Check rate limiting

### Logs Location
- **Application Logs**: `logs/app.log`
- **Database Logs**: PostgreSQL logs
- **Nginx Logs**: `/var/log/nginx/`

## 📞 Support

For technical support or issues:
- Check API documentation: `http://24.144.67.150:9179/api/docs`
- Test health endpoint: `curl http://24.144.67.150:9179/v1/healthz`
- Check platform stats: `curl http://24.144.67.150:9179/api/stats`

## 🔄 Updates

To update the multi-tenant platform:
```bash
cd /opt/webwise/directory/
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql://adminwatch:adminwatch123@localhost:5432/directory_tenant"
alembic upgrade head
# Restart the platform
```

---

**White-label Multi-tenant Business Directory Platform** - Empowering businesses worldwide with customizable, scalable directory solutions.
