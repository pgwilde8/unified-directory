## **For Camilo - System Management Commands:**

### **Legacy Directory Service (Port 9178):**
```bash
# Service Management
sudo systemctl status directory          # Check service status
sudo systemctl start directory           # Start service
sudo systemctl stop directory            # Stop service
sudo systemctl restart directory         # Restart service
sudo systemctl enable directory          # Enable auto-start
# Check legacy service
sudo systemctl status directory

# Check multi-tenant service
sudo systemctl status multi-directory
# View Logs
sudo journalctl -u directory -f          # Follow logs in real-time
sudo journalctl -u directory --no-pager -n 50  # Last 50 log entries
```

### **Multi-Tenant Service (Port 9179):**
```bash
# Check if multi-tenant service is running
sudo netstat -tlnp | grep 9179
https://github.com/pgwilde8/multi-directory/

# Start multi-tenant service manually
cd /opt/webwise/directory
source venv/bin/activate
uvicorn backend.main_tenant:app --host 0.0.0.0 --port 9179 --reload

# Or create a systemd service for multi-tenant (optional)
sudo nano /etc/systemd/system/multi-directory.service
```

### **Database Management:**
```bash
# Connect to legacy database
psql -h localhost -U adminwatch -d directory
# Password: adminwatch123

# Connect to multi-tenant database
psql -h localhost -U dir-admin -d directories
# Password: Securepass
```

### **Test Services:**
```bash
# Test legacy system
curl http://localhost:9178/api/health

# Test multi-tenant system
curl http://localhost:9179/v1/healthz
```

