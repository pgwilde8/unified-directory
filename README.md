# 🏢 Business Directory

A modern business directory platform that allows business owners to create and manage their listings using Google OAuth authentication. Built with FastAPI, PostgreSQL, and modern web technologies.

## 🌟 Features

- **Google OAuth Authentication** - Secure login for business owners
- **Business Management** - Create, edit, and manage business listings
- **File Uploads** - Upload logos, images, and documents
- **Responsive Design** - Modern, mobile-friendly interface
- **RESTful API** - Complete API for business operations
- **Admin Dashboard** - System administration interface
- **Database Management** - PostgreSQL with Alembic migrations

## 🚀 Quick Start

### Access URLs
- **Main Site**: `http://24.144.67.150:9178/`
- **Login Page**: `http://24.144.67.150:9178/` (Google OAuth)
- **Dashboard**: `http://24.144.67.150:9178/dashboard` (after login)
- **API Documentation**: `http://24.144.67.150:9178/api/docs`
- **Health Check**: `http://24.144.67.150:9178/api/health`

### Default Credentials

#### Admin Access (Legacy System)
- **Username**: `admin`
- **Password**: `admin123`
- **Admin Panel**: `http://24.144.67.150:9178/admin.html`

#### Database Access
- **Host**: `localhost`
- **Username**: `adminwatch`
- **Password**: `adminwatch123`
- **Database**: `directory`

This way you have:
adminwatch user → directory database (legacy system)
dir-admin user → directories database (new multi-tenant platform)

## 🛠️ System Management

### Service Commands

```bash
# Service Management
sudo systemctl status directory          # Check service status
sudo systemctl start directory           # Start service
sudo systemctl stop directory            # Stop service
sudo systemctl restart directory         # Restart service
sudo systemctl enable directory          # Enable auto-start

# View Logs
sudo journalctl -u directory -f          # Follow logs in real-time
sudo journalctl -u directory --no-pager -n 50  # Last 50 log entries

# Service Installation (one-time setup)
sudo cp directory.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable directory
```

### Manual Development Server

```bash
# SSH into server
ssh -i ~/.ssh/id_ed25519_luckyclub camilo@24.144.67.150

# Navigate to project
cd /opt/webwise/directory/

# Activate virtual environment
source venv/bin/activate

# Start development server
uvicorn backend.main:app --host 0.0.0.0 --port 9178 --reload
```

## 🗄️ Database Management

### Connect to Database

```bash
# SSH into server first
ssh -i ~/.ssh/id_ed25519_luckyclub camilo@24.144.67.150

# Connect to PostgreSQL
psql -h localhost -U adminwatch -d directory
# Password: adminwatch123
```

### Database Migrations

```bash
# Navigate to project directory
cd /opt/webwise/directory/

# Activate virtual environment
source venv/bin/activate

# Run migrations
alembic upgrade head

# Create new migration (after model changes)
alembic revision --autogenerate -m "Description of changes"

# Check migration history
alembic history
```

### Database Schema

The system includes these main tables:
- **users** - Google OAuth authenticated users
- **businesses** - Business listings
- **business_reviews** - Customer reviews
- **business_claims** - Business ownership claims
- **business_analytics** - Business metrics
- **system_settings** - System configuration

## 🔧 Configuration

### Environment Variables

Key configuration in `.env` file:

```bash
# Database
DATABASE_URL=postgresql://adminwatch:adminwatch123@localhost/directory

# Application
APP_NAME="Business Directory"
DEBUG=False
HOST=0.0.0.0
PORT=9178

# Google OAuth (REQUIRED)
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://24.144.67.150:9178/api/auth/google/callback

# Security
SECRET_KEY=your_secret_key_here

# Business Settings
MAX_BUSINESS_LISTINGS_PER_USER=10
BUSINESS_APPROVAL_REQUIRED=True
ALLOWED_BUSINESS_CATEGORIES=restaurant,retail,service,healthcare,education,entertainment,automotive,professional
```

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select project
3. Enable Google Identity Toolkit API
4. Create OAuth 2.0 credentials
5. Set authorized redirect URI: `http://24.144.67.150:9178/api/auth/google/callback`
6. Update `.env` file with your credentials

## 📁 Project Structure

```
/opt/webwise/directory/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── routes/                 # API routes
│   │   ├── google_auth.py      # Google OAuth authentication
│   │   ├── businesses.py       # Business management
│   │   ├── auth.py             # Legacy admin auth
│   │   └── admin.py            # Admin functions
│   ├── core/
│   │   └── config.py           # Configuration settings
│   └── middleware.py           # Custom middleware
├── database/
│   ├── models.py               # Database models
│   ├── business_models.py      # Business-specific models
│   └── __init__.py             # Database connection
├── frontend/
│   ├── login.html              # Google OAuth login page
│   ├── dashboard.html          # Business owner dashboard
│   └── admin.html              # Admin dashboard
├── alembic/                    # Database migrations
├── venv/                       # Python virtual environment
├── directory.service           # Systemd service file
├── requirements.txt            # Python dependencies
└── .env                        # Environment configuration
```

## 🔐 Security

- **JWT Authentication** for API access
- **Google OAuth 2.0** for user authentication
- **HTTPS Ready** (configure nginx/SSL for production)
- **CORS Protection** configured
- **Rate Limiting** implemented
- **Input Validation** with Pydantic

## 🚀 Deployment

### Production Setup

1. **Update Google OAuth** redirect URI to your domain
2. **Configure SSL/HTTPS** with nginx
3. **Set up domain** (e.g., `directory.yourdomain.com`)
4. **Configure email** settings for notifications
5. **Set up backups** for database
6. **Configure monitoring** and logging

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name directory.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name directory.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:9178;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   sudo journalctl -u directory --no-pager -n 20
   ```

2. **Port already in use**
   ```bash
   sudo netstat -tlnp | grep 9178
   sudo kill <PID>
   ```

3. **Database connection issues**
   ```bash
   sudo systemctl status postgresql
   psql -h localhost -U adminwatch -d directory
   ```

4. **Google OAuth not working**
   - Check redirect URI in Google Console
   - Verify client ID/secret in `.env`
   - Check browser console for errors

### Logs Location

- **Service Logs**: `sudo journalctl -u directory -f`
- **Application Logs**: `logs/app.log`
- **Nginx Logs**: `/var/log/nginx/`

## 📞 Support

For technical support or issues:
- Check logs: `sudo journalctl -u directory -f`
- Verify service status: `sudo systemctl status directory`
- Test API: `curl http://localhost:9178/api/health`

## 🔄 Updates

To update the application:
```bash
cd /opt/webwise/directory/
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart directory
```

---

**Business Directory** - Empowering businesses worldwide with modern digital presence management.