# Unified Business Directory Platform - Port 9180

## Overview
This is the unified business directory platform that combines:
- **Legacy Google OAuth functionality** (originally port 9178)
- **Multi-tenant API capabilities** (originally port 9179)
- **Camilo's Stripe integration** and other enhancements

## Configuration

### Port: 9180
- **Legacy endpoints**: `/api/*` (Google OAuth based)
- **Multi-tenant endpoints**: `/v1/*` (API key based)

### Key Files
- `backend/main_unified.py` - Main unified application
- `.env.unified` - Environment configuration
- `start_unified.sh` - Startup script
- `unified-directory.service` - Systemd service file

## Running the System

### Manual Start
```bash
cd /opt/webwise/unified-directory
./start_unified.sh
```

### Using Systemd (Production)
```bash
# Install service
sudo cp unified-directory.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable unified-directory
sudo systemctl start unified-directory

# Check status
sudo systemctl status unified-directory
```

### Using Uvicorn Directly
```bash
cd /opt/webwise/unified-directory
source venv/bin/activate
uvicorn backend.main_unified:app --host 0.0.0.0 --port 9180 --reload
```

## Authentication Types

### 1. Google OAuth (Legacy)
- Endpoints: `/api/auth/google/*`
- Use for traditional web application login
- Supports business CRUD operations

### 2. API Key (Multi-tenant)
- Endpoints: `/v1/*`
- Header: `Authorization: Bearer sk_your_api_key`
- Use for tenant-specific API access

## Key Endpoints

### System Endpoints
- `GET /` - Root with system information
- `GET /api/health` - Health check
- `GET /info` - Detailed system info
- `GET /api/docs` - API documentation

### Legacy Endpoints (Google OAuth)
- `GET /api/auth/google/login` - Google OAuth login
- `GET /api/businesses` - Business listings
- `POST /api/businesses` - Create business

### Multi-tenant Endpoints (API Key)
- `POST /v1/auth/register` - Register tenant
- `GET /v1/listings` - Get tenant listings
- `POST /v1/listings` - Create listing

## Database Configuration
- **Database**: `unified_directory`
- **Connection**: `postgresql://adminwatch:adminwatch123@localhost:5432/unified_directory`
- **Features**: Multi-tenant isolation with `tenant_id`

## Testing
```bash
# Test the unified system
python3 test_unified.py

# Check if server is running
curl http://localhost:9180/
curl http://localhost:9180/api/health
```

## Features
- ✅ Dual authentication (Google OAuth + API keys)
- ✅ Multi-tenant isolation
- ✅ Stripe integration (from Camilo's work)
- ✅ File uploads
- ✅ Business directory functionality
- ✅ Endorsements system
- ✅ Usage tracking

## Migration from Legacy Systems
This unified system replaces:
- Port 9178 (directory) - Legacy Google OAuth system
- Port 9179 (multi-directory) - Multi-tenant API system

All functionality from both systems is preserved and accessible through the unified interface.