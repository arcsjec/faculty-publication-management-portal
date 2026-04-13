#!/bin/bash
#################################################################
# Backup Script for SJEC Publications Portal
# Run this daily via cron: 0 2 * * * /opt/sjec-publications/deployment/backup.sh
#################################################################

# Configuration
APP_DIR="/opt/sjec-publications"
BACKUP_DIR="/opt/sjec-publications/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="sjecportal_backup_$DATE"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

echo "=========================================="
echo "SJEC Publications Portal - Backup"
echo "Date: $(date)"
echo "=========================================="
echo ""

#################################################################
# 1. Backup Database
#################################################################
echo "📊 Backing up database..."
mkdir -p $BACKUP_DIR/$BACKUP_NAME/database

if [ -f "$APP_DIR/instance/publications.db" ]; then
    cp $APP_DIR/instance/publications.db $BACKUP_DIR/$BACKUP_NAME/database/
    echo "   ✅ Database backed up"
else
    echo "   ⚠️  Database not found"
fi

#################################################################
# 2. Backup Uploads
#################################################################
echo ""
echo "📁 Backing up uploads..."
if [ -d "$APP_DIR/uploads" ]; then
    cp -r $APP_DIR/uploads $BACKUP_DIR/$BACKUP_NAME/
    echo "   ✅ Uploads backed up"
else
    echo "   ⚠️  Uploads directory not found"
fi

#################################################################
# 3. Backup Configuration
#################################################################
echo ""
echo "⚙️  Backing up configuration..."
mkdir -p $BACKUP_DIR/$BACKUP_NAME/config

# Copy important config files
[ -f "$APP_DIR/config.py" ] && cp $APP_DIR/config.py $BACKUP_DIR/$BACKUP_NAME/config/
[ -f "$APP_DIR/.env" ] && cp $APP_DIR/.env $BACKUP_DIR/$BACKUP_NAME/config/
[ -f "/etc/nginx/sites-available/sjecportal" ] && cp /etc/nginx/sites-available/sjecportal $BACKUP_DIR/$BACKUP_NAME/config/
[ -f "/etc/systemd/system/sjecportal.service" ] && cp /etc/systemd/system/sjecportal.service $BACKUP_DIR/$BACKUP_NAME/config/

echo "   ✅ Configuration backed up"

#################################################################
# 4. Create Compressed Archive
#################################################################
echo ""
echo "📦 Creating compressed archive..."
cd $BACKUP_DIR
tar -czf ${BACKUP_NAME}.tar.gz $BACKUP_NAME
rm -rf $BACKUP_NAME

echo "   ✅ Archive created: ${BACKUP_NAME}.tar.gz"

#################################################################
# 5. Cleanup Old Backups (keep last 7 days)
#################################################################
echo ""
echo "🧹 Cleaning up old backups..."
find $BACKUP_DIR -name "sjecportal_backup_*.tar.gz" -mtime +7 -delete
echo "   ✅ Old backups removed (kept last 7 days)"

#################################################################
# 6. Show Backup Info
#################################################################
echo ""
echo "=========================================="
echo "✅ BACKUP COMPLETE!"
echo "=========================================="
echo "Location: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
echo "Size: $(du -h $BACKUP_DIR/${BACKUP_NAME}.tar.gz | cut -f1)"
echo ""
echo "Available backups:"
ls -lh $BACKUP_DIR/*.tar.gz | tail -5
echo "=========================================="
