#!/bin/bash
#################################################################
# SJEC Publications Portal - Service Configuration Script
# Run this AFTER copying application files to /opt/sjec-publications
#################################################################

set -e

echo "=========================================="
echo "SJEC Publications Portal"
echo "Service Configuration"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "âŒ Please run as root (use sudo)"
    exit 1
fi

APP_DIR="/opt/sjec-publications"

# Check if application directory exists
if [ ! -d "$APP_DIR" ]; then
    echo "âŒ Error: Application directory not found: $APP_DIR"
    echo "   Please copy your application files first!"
    exit 1
fi

#################################################################
# Step 1: Create Log Directories
#################################################################
echo "ðŸ“ Step 1: Creating log directories..."
mkdir -p /var/log/gunicorn
mkdir -p /var/run/gunicorn
chown SJEC:SJEC /var/log/gunicorn
chown SJEC:SJEC /var/run/gunicorn

echo "âœ… Log directories created"

#################################################################
# Step 2: Install Python Dependencies
#################################################################
echo ""
echo "ðŸ Step 2: Installing Python dependencies..."
cd $APP_DIR

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    sudo -u SJEC python3 -m venv venv
fi

# Activate and install requirements
sudo -u SJEC bash -c "source venv/bin/activate && pip install --upgrade pip"
sudo -u SJEC bash -c "source venv/bin/activate && pip install -r requirements.txt"
sudo -u SJEC bash -c "source venv/bin/activate && pip install gunicorn"

echo "âœ… Python dependencies installed"

#################################################################
# Step 3: Configure Nginx
#################################################################
echo ""
echo "ðŸŒ Step 3: Configuring Nginx..."

# Copy Nginx configuration
cp deployment/nginx-sjecportal.conf /etc/nginx/sites-available/sjecportal

# Enable site
ln -sf /etc/nginx/sites-available/sjecportal /etc/nginx/sites-enabled/

# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Restart Nginx
systemctl restart nginx
systemctl enable nginx

echo "âœ… Nginx configured"

#################################################################
# Step 4: Configure Systemd Service
#################################################################
echo ""
echo "âš™ï¸  Step 4: Configuring systemd service..."

# Copy service file
cp deployment/sjecportal.service /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable and start service
systemctl enable sjecportal
systemctl start sjecportal

echo "âœ… Systemd service configured"

#################################################################
# Step 5: Initialize Database
#################################################################
echo ""
echo "ðŸ—„ï¸  Step 5: Checking database..."

if [ -f "$APP_DIR/instance/publications.db" ]; then
    echo "   Database already exists"
else
    echo "   Initializing database..."
    cd $APP_DIR
    sudo -u SJEC bash -c "source venv/bin/activate && python3 -c 'from app import db; db.create_all()' 2>/dev/null || echo 'Database initialization skipped'"
fi

echo "âœ… Database ready"

#################################################################
# Step 6: Set Permissions
#################################################################
echo ""
echo "ðŸ” Step 6: Setting permissions..."

chown -R SJEC:SJEC $APP_DIR
chmod -R 755 $APP_DIR
chmod -R 775 $APP_DIR/instance
chmod -R 775 $APP_DIR/uploads

echo "âœ… Permissions set"

#################################################################
# Step 7: Verify Services
#################################################################
echo ""
echo "âœ… Step 7: Verifying services..."

sleep 2

# Check Nginx
if systemctl is-active --quiet nginx; then
    echo "   âœ… Nginx: Running"
else
    echo "   âŒ Nginx: Not running"
fi

# Check Gunicorn
if systemctl is-active --quiet sjecportal; then
    echo "   âœ… Gunicorn: Running"
else
    echo "   âŒ Gunicorn: Not running"
fi

#################################################################
# Final Output
#################################################################
echo ""
echo "=========================================="
echo "âœ… CONFIGURATION COMPLETE!"
echo "=========================================="
echo ""
echo "ðŸŒ Your portal is now accessible at:"
echo "   - http://publications.local"
echo "   - http://192.168.111.79"
echo ""
echo "ðŸ“Š Service Management:"
echo "   Status:  sudo systemctl status sjecportal"
echo "   Stop:    sudo systemctl stop sjecportal"
echo "   Start:   sudo systemctl start sjecportal"
echo "   Restart: sudo systemctl restart sjecportal"
echo "   Logs:    sudo journalctl -u sjecportal -f"
echo ""
echo "ðŸ”„ After code updates:"
echo "   sudo systemctl restart sjecportal"
echo ""
echo "ðŸ“ Nginx commands:"
echo "   Status:  sudo systemctl status nginx"
echo "   Restart: sudo systemctl restart nginx"
echo "   Logs:    sudo tail -f /var/log/nginx/sjecportal_access.log"
echo ""
echo "=========================================="

