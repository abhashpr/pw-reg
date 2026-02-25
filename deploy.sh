#!/bin/bash

# PWNSAT Registration System - Deployment Script
# Run this script on your AWS Lightsail instance to set up the entire system

set -e

echo "=========================================="
echo "PWNSAT Registration System - Setup"
echo "=========================================="

# Check if running as non-root
if [ "$EUID" -ne 0 ]; then 
   echo "This script must be run with sudo"
   exit 1
fi

# Update system
echo "[1/10] Updating system packages..."
apt update
apt upgrade -y

# Install dependencies
echo "[2/10] Installing system dependencies..."
apt install -y python3.11 python3.11-venv python3-pip nginx curl git nodejs npm supervisor

# Clone or navigate to project
if [ ! -d "/home/ubuntu/pw-reg" ]; then
    echo "[3/10] Cloning repository..."
    cd /home/ubuntu
    git clone https://github.com/yourusername/pw-reg.git
else
    echo "[3/10] Repository already exists, pulling latest..."
    cd /home/ubuntu/pw-reg
    git pull
fi

cd /home/ubuntu/pw-reg

# Setup backend
echo "[4/10] Setting up Python backend..."
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
deactivate

# Setup .env
echo "[5/10] Checking .env file..."
if [ ! -f "../.env" ]; then
    echo "Creating .env from template..."
    cp ../.env.example ../.env
    echo "⚠️  Please edit .env with your Gmail credentials and secret key"
    echo "   nano /home/ubuntu/pw-reg/.env"
    exit 1
fi

# Build frontend
echo "[6/10] Building frontend..."
cd ../frontend
npm install
npm run build

# Setup nginx
echo "[7/10] Configuring nginx..."
rm -f /etc/nginx/sites-enabled/default
cp /home/ubuntu/pw-reg/configs/nginx.conf /etc/nginx/sites-available/pwnsat
ln -sf /etc/nginx/sites-available/pwnsat /etc/nginx/sites-enabled/

# Test nginx config
nginx -t

# Setup systemd service
echo "[8/10] Setting up systemd service..."
cp /home/ubuntu/pw-reg/configs/pwnsat-api.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable pwnsat-api

# Fix permissions
echo "[9/10] Setting file permissions..."
chown -R ubuntu:ubuntu /home/ubuntu/pw-reg

# Start services
echo "[10/10] Starting services..."
systemctl restart nginx
systemctl restart pwnsat-api

# Firewall
echo "Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env with your Gmail credentials:"
echo "   sudo nano /home/ubuntu/pw-reg/.env"
echo ""
echo "2. Restart the API service:"
echo "   sudo systemctl restart pwnsat-api"
echo ""
echo "3. Check service status:"
echo "   sudo systemctl status pwnsat-api"
echo ""
echo "4. View logs:"
echo "   sudo journalctl -u pwnsat-api -f"
echo ""
echo "5. Setup SSL certificate (when ready):"
echo "   sudo certbot certonly --nginx -d yourdomain.com"
echo ""
echo "API Documentation: http://your-instance-ip/docs"
