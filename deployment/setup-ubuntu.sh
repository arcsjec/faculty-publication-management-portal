#!/bin/bash
#################################################################
# SJEC Publications Portal - Ubuntu 24.04 Setup Script
# This script installs all dependencies and configures the server
#################################################################

set -e  # Exit on any error

echo "=========================================="
echo "SJEC Publications Portal Setup"
echo "Ubuntu 24.04 LTS"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Get the actual user who invoked sudo
ACTUAL_USER=${SUDO_USER:-$USER}
USER_HOME=$(eval echo ~$ACTUAL_USER)

echo "📋 Installation Summary:"
echo "   User: $ACTUAL_USER"
echo "   Home: $USER_HOME"
echo "   IP: 192.168.111.79"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

#################################################################
# Step 1: Update System
#################################################################
echo ""
echo "🔄 Step 1: Updating system packages..."
apt update
apt upgrade -y

#################################################################
# Step 2: Install Required Packages
#################################################################
echo ""
echo "📦 Step 2: Installing required packages..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    openssh-server \
    ufw \
    git \
    avahi-daemon \
    curl \
    wget

#################################################################
# Step 3: Configure SSH
#################################################################
echo ""
echo "🔐 Step 3: Configuring SSH..."
systemctl enable ssh
systemctl start ssh

# Allow SSH through firewall
ufw allow OpenSSH

echo "✅ SSH enabled on port 22"

#################################################################
# Step 4: Configure Firewall
#################################################################
echo ""
echo "🔥 Step 4: Configuring firewall..."
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS (future)
ufw allow 8080/tcp  # Alternative port
ufw --force enable

echo "✅ Firewall configured"

#################################################################
# Step 5: Configure Avahi (hostname.local)
#################################################################
echo ""
echo "🌐 Step 5: Configuring mDNS (Avahi)..."
systemctl enable avahi-daemon
systemctl start avahi-daemon

# Set hostname to publications
hostnamectl set-hostname publications

echo "✅ Hostname set to: publications"
echo "   Access via: http://publications.local"

#################################################################
# Step 6: Create Application Directory
#################################################################
echo ""
echo "📁 Step 6: Creating application directory..."
APP_DIR="/opt/sjec-publications"
mkdir -p $APP_DIR
chown $ACTUAL_USER:$ACTUAL_USER $APP_DIR

echo "✅ Application directory: $APP_DIR"

#################################################################
# Step 7: Install Gunicorn
#################################################################
echo ""
echo "🐍 Step 7: Installing Gunicorn..."
pip3 install gunicorn --break-system-packages

echo "✅ Gunicorn installed"

#################################################################
# Final Instructions
#################################################################
echo ""
echo "=========================================="
echo "✅ SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Copy your application files to: $APP_DIR"
echo "   Example: scp -r /path/to/portal/* SJEC@192.168.111.79:$APP_DIR/"
echo ""
echo "2. Create Python virtual environment:"
echo "   cd $APP_DIR"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo ""
echo "3. Run the configuration script:"
echo "   sudo bash deployment/configure_services.sh"
echo ""
echo "4. Access your portal:"
echo "   - Local network: http://publications.local"
echo "   - By IP: http://192.168.111.79"
echo ""
echo "5. SSH Access:"
echo "   ssh SJEC@192.168.111.79"
echo ""
echo "=========================================="
