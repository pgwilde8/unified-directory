#!/bin/bash
# Directory Deployment Script

set -e

echo "🚀 Deploying Directory on port 9178..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please run as adminwatch user, not root"
    exit 1
fi

# Navigate to project directory
cd /opt/webwise/directory

# Activate virtual environment
source venv/bin/activate

echo "📦 Installing/updating dependencies..."
pip install -r requirements.txt

echo "🗄️ Running database migrations..."
alembic upgrade head

echo "🔧 Setting up systemd service..."
sudo cp directory.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable directory

echo "🌐 Setting up nginx configuration..."
echo "⚠️  IMPORTANT: Update the domain name in nginx-crimewatch.conf first!"
echo "   Replace 'crimewatch.yourdomain.com' with your actual domain"
echo ""
echo "Then run these commands:"
echo "   sudo cp nginx-crimewatch.conf /etc/nginx/sites-available/crimewatch.yourdomain.com"
echo "   sudo ln -s /etc/nginx/sites-available/crimewatch.yourdomain.com /etc/nginx/sites-enabled/"
echo "   sudo nginx -t"
echo "   sudo systemctl reload nginx"
echo ""
echo "🔒 Get SSL certificate:"
echo "   sudo certbot --nginx -d crimewatch.yourdomain.com -d www.crimewatch.yourdomain.com"
echo ""
echo "🚀 Start the service:"
echo "   sudo systemctl start directory"
echo "   sudo systemctl status directory"
echo ""
echo "✅ Deployment script completed!"
echo "📊 Service will be available at: https://crimewatch.yourdomain.com"
echo "🔑 Admin login: admin / admin123"
echo "⏰ Login hours: 6 AM - 10 PM EST"
