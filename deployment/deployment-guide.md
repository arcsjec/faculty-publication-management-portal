# SJEC Publications Portal - Ubuntu Deployment Guide

## ðŸ“‹ Overview
This guide covers deploying the SJEC Publications Portal on Ubuntu 24.04 LTS with:
- **Nginx** as reverse proxy
- **Gunicorn** as WSGI server
- **Auto-start** on boot via systemd
- **mDNS** for hostname access (`publications.local`)
- **SSH** access for remote management

---

## ðŸ–¥ï¸ Server Information
- **OS**: Ubuntu 24.04 LTS
- **IP**: 192.168.111.79
- **Hostname**: publications.local
- **User**: SJEC
- **App Directory**: /opt/sjec-publications

---

## ðŸš€ Initial Setup (One-time)

### Step 1: Prepare Ubuntu System

1. **Run the setup script on Ubuntu:**
   ```bash
   cd /tmp
   # Copy setup_ubuntu.sh to Ubuntu first
   sudo bash setup_ubuntu.sh
   ```

### Step 2: Transfer Application Files

From your Windows machine:
```powershell
# Using SCP (from Windows)
scp -r "C:\Users\shalt\.vscode\ProgramFiles\Faculty Publication Portal\*" SJEC@192.168.111.79:/tmp/portal/

# Then on Ubuntu, move to final location:
sudo mv /tmp/portal/* /opt/sjec-publications/
sudo chown -R SJEC:SJEC /opt/sjec-publications
```

### Step 3: Configure Services

On Ubuntu:
```bash
cd /opt/sjec-publications
sudo bash deployment/configure_services.sh
```

---

## ðŸ“ Deployment Files Explained

### Shell Scripts (`.sh` files)

1. **setup_ubuntu.sh**
   - One-time system setup
   - Installs: Python, Nginx, SSH, Gunicorn, Avahi
   - Configures firewall and hostname
   - Run with: `sudo bash setup_ubuntu.sh`

2. **configure_services.sh**
   - Configures Nginx and systemd
   - Sets up virtual environment
   - Initializes database
   - Run with: `sudo bash deployment/configure_services.sh`

3. **manage.sh**
   - Service management helper
   - Quick commands: start, stop, restart, status, logs
   - Run with: `bash deployment/manage.sh status`

4. **backup.sh**
   - Backs up database, uploads, config
   - Run daily via cron
   - Run with: `bash deployment/backup.sh`

5. **deploy.sh**
   - Quick deployment from Windows
   - Syncs files and restarts service
   - Run from Windows: `bash deployment/deploy.sh`

### Configuration Files

1. **nginx-sjecportal.conf**
   - Nginx reverse proxy config
   - Serves static files
   - Proxies requests to Gunicorn
   - Installed to: `/etc/nginx/sites-available/`

2. **sjecportal.service**
   - Systemd service file
   - Auto-starts portal on boot
   - Manages Gunicorn process
   - Installed to: `/etc/systemd/system/`

3. **gunicorn_config.py**
   - Gunicorn WSGI server settings
   - 3 workers, 2 threads per worker
   - Logging configuration
   - Used by systemd service

---

## ðŸ”§ Common Commands

### Service Management
```bash
# Check status
bash deployment/manage.sh status

# Restart portal
bash deployment/manage.sh restart

# View logs
bash deployment/manage.sh logs

# Start all services
bash deployment/manage.sh start

# Stop portal
bash deployment/manage.sh stop
```

### Manual Service Commands
```bash
# Portal service
sudo systemctl status sjecportal
sudo systemctl restart sjecportal
sudo systemctl stop sjecportal
sudo systemctl start sjecportal

# Nginx
sudo systemctl status nginx
sudo systemctl restart nginx

# View logs
sudo journalctl -u sjecportal -f
sudo tail -f /var/log/nginx/sjecportal_access.log
```

### Code Updates
```bash
# Method 1: Via SSH
ssh SJEC@192.168.111.79
cd /opt/sjec-publications
# Edit files
sudo systemctl restart sjecportal

# Method 2: From Windows (if deploy.sh configured)
bash deployment/deploy.sh
```

---

## ðŸŒ Accessing the Portal

### From Campus WiFi:
- `http://publications.local`
- `http://192.168.111.79`

### SSH Access:
```bash
ssh SJEC@192.168.111.79
```

### VS Code Remote SSH:
1. Install "Remote - SSH" extension
2. Add host configuration:
   ```
   Host sjec-portal
       HostName 192.168.111.79
       User SJEC
   ```
3. Connect via Command Palette: "Remote-SSH: Connect to Host"

---

## ðŸ” Security Checklist

- âœ… UFW firewall enabled (ports 22, 80, 8080)
- âœ… SSH with key-based auth recommended
- âœ… Gunicorn runs as non-root user (SJEC)
- âœ… Application in /opt (standard location)
- âœ… Nginx security headers configured
- âœ… Database and uploads have proper permissions

---

## ðŸ“Š Backup & Maintenance

### Manual Backup
```bash
bash deployment/backup.sh
```

### Automatic Daily Backup
Add to crontab:
```bash
sudo crontab -e
# Add this line:
0 2 * * * /opt/sjec-publications/deployment/backup.sh
```

### Restore from Backup
```bash
cd /opt/sjec-publications/backups
tar -xzf sjecportal_backup_YYYYMMDD_HHMMSS.tar.gz
# Manually restore database and uploads
```

---

## ðŸ› Troubleshooting

### Portal not accessible:
```bash
# Check service status
bash deployment/manage.sh status

# Check logs
sudo journalctl -u sjecportal -f

# Verify Nginx
sudo nginx -t
sudo systemctl status nginx
```

### Database issues:
```bash
cd /opt/sjec-publications
source venv/bin/activate
python3
>>> from app import db
>>> db.create_all()
```

### Permission issues:
```bash
sudo chown -R SJEC:SJEC /opt/sjec-publications
sudo chmod -R 755 /opt/sjec-publications
sudo chmod -R 775 /opt/sjec-publications/instance
sudo chmod -R 775 /opt/sjec-publications/uploads
```

---

## ðŸ“ File Structure on Ubuntu

```
/opt/sjec-publications/
â”œâ”€â”€ app.py                      # Main Flask application
â”œâ”€â”€ config.py                   # Configuration
â”œâ”€â”€ models.py                   # Database models
â”œâ”€â”€ forms.py                    # Forms
â”œâ”€â”€ venv/                       # Python virtual environment
â”œâ”€â”€ static/                     # Static files (CSS, JS, images)
â”œâ”€â”€ templates/                  # HTML templates
â”œâ”€â”€ uploads/                    # User uploads
â”œâ”€â”€ instance/                   # Database and instance files
â”‚   â””â”€â”€ publications.db
â”œâ”€â”€ deployment/                 # Deployment scripts
â”‚   â”œâ”€â”€ setup_ubuntu.sh
â”‚   â”œâ”€â”€ configure_services.sh
â”‚   â”œâ”€â”€ manage.sh
â”‚   â”œâ”€â”€ backup.sh
â”‚   â”œâ”€â”€ deploy.sh
â”‚   â”œâ”€â”€ nginx-sjecportal.conf
â”‚   â”œâ”€â”€ sjecportal.service
â”‚   â””â”€â”€ gunicorn_config.py
â””â”€â”€ backups/                    # Backup archives

/etc/nginx/sites-available/
â””â”€â”€ sjecportal                  # Nginx config (symlinked to sites-enabled)

/etc/systemd/system/
â””â”€â”€ sjecportal.service          # Systemd service

/var/log/
â”œâ”€â”€ nginx/
â”‚   â”œâ”€â”€ sjecportal_access.log
â”‚   â””â”€â”€ sjecportal_error.log
â””â”€â”€ gunicorn/
    â”œâ”€â”€ access.log
    â””â”€â”€ error.log
```

---

## âœ… Post-Deployment Checklist

- [ ] Ubuntu system updated
- [ ] All services installed (Nginx, Python, SSH, Avahi)
- [ ] Application files transferred
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Database initialized
- [ ] Nginx configured and running
- [ ] Systemd service enabled and running
- [ ] Firewall configured
- [ ] Hostname set to `publications`
- [ ] Accessible via `http://publications.local`
- [ ] SSH access working
- [ ] VS Code Remote SSH configured
- [ ] Backup script tested
- [ ] Daily backup cron job added

---

## ðŸ†˜ Support

For issues or questions:
- **Technical Support**: testpublicationportal@gmail.com
- **Developer (Shalton)**: 23g56.shalton@sjec.ac.in
- **Developer (Luke)**: 23g31.luke@sjec.ac.in

---

**Last Updated**: December 19, 2025

