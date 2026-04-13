#!/bin/bash
#################################################################
# SJEC Publications Portal - Complete Setup on Ubuntu
# Run this script on the Ubuntu machine after connecting via SSH
#################################################################

set -e

echo "=========================================="
echo "SJEC Publications Portal - Ubuntu Setup"
echo "=========================================="
echo ""

# Step 1: Update system
echo "📦 Step 1: Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Step 2: Install required packages
echo ""
echo "📦 Step 2: Installing required packages..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    ufw \
    git \
    avahi-daemon \
    curl \
    wget

# Step 3: Configure firewall
echo ""
echo "🔥 Step 3: Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8080/tcp
echo "y" | sudo ufw enable

# Step 4: Configure Avahi (for .local hostname)
echo ""
echo "🌐 Step 4: Setting up hostname..."
sudo systemctl enable avahi-daemon
sudo systemctl start avahi-daemon
sudo hostnamectl set-hostname publications

# Step 5: Create application directory
echo ""
echo "📁 Step 5: Creating application directory..."
sudo mkdir -p /opt/sjec-publications
sudo chown -R sjec:sjec /opt/sjec-publications

# Step 6: Create log directories
echo ""
echo "📁 Step 6: Creating log directories..."
sudo mkdir -p /var/log/gunicorn
sudo chown -R sjec:sjec /var/log/gunicorn

echo ""
echo "=========================================="
echo "✅ INITIAL SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "📝 Next: Transfer files from Windows to /opt/sjec-publications"
echo ""
