#!/bin/bash
# Automated Daily Database Backup Script
# Schedule this using cron on Ubuntu

cd "$(dirname "$0")"

echo "========================================"
echo "SJEC Publication Portal - Daily Backup"
echo "========================================"
echo ""

# Create backup with date in filename
python3 db_optimizer.py backup

# Clean up old backups (keep last 30 days)
python3 db_optimizer.py cleanup 30

echo ""
echo "Backup complete! Check backups/ folder."
echo ""
