#!/bin/bash
#################################################################
# Quick Deployment Script
# Use this to deploy code updates from your local machine
#################################################################

echo "=========================================="
echo "SJEC Publications Portal - Quick Deploy"
echo "=========================================="
echo ""

# Configuration
REMOTE_USER="SJEC"
REMOTE_HOST="192.168.111.79"
REMOTE_DIR="/opt/sjec-publications"
LOCAL_DIR="."

# Exclude patterns
EXCLUDE_PATTERNS=(
    "venv/"
    "__pycache__/"
    "*.pyc"
    ".git/"
    ".vscode/"
    "instance/*.db"
    "uploads/*"
    "*.log"
    "deployment/"
)

# Build rsync exclude options
EXCLUDE_OPTS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_OPTS="$EXCLUDE_OPTS --exclude=$pattern"
done

echo "📦 Syncing files to server..."
echo "   From: $LOCAL_DIR"
echo "   To:   $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR"
echo ""

# Sync files
rsync -avz --progress \
    $EXCLUDE_OPTS \
    --delete \
    $LOCAL_DIR/ \
    $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Files synced successfully!"
    echo ""
    echo "🔄 Restarting service..."
    
    # Restart the service
    ssh $REMOTE_USER@$REMOTE_HOST "sudo systemctl restart sjecportal"
    
    if [ $? -eq 0 ]; then
        echo "✅ Service restarted!"
        echo ""
        echo "🌐 Portal updated and running at:"
        echo "   http://publications.local"
        echo "   http://192.168.111.79"
    else
        echo "❌ Failed to restart service"
        exit 1
    fi
else
    echo "❌ File sync failed"
    exit 1
fi

echo ""
echo "=========================================="
