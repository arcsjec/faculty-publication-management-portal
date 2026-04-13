#!/bin/bash
#################################################################
# Service Management Helper Script
# Quick commands for managing the SJEC Publications Portal
#################################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}==========================================${NC}"
    echo -e "${BLUE}SJEC Publications Portal - Manager${NC}"
    echo -e "${BLUE}==========================================${NC}"
}

print_status() {
    print_header
    echo ""
    
    # Check Gunicorn
    if systemctl is-active --quiet sjecportal; then
        echo -e "${GREEN}✅ Portal Service: RUNNING${NC}"
    else
        echo -e "${RED}❌ Portal Service: STOPPED${NC}"
    fi
    
    # Check Nginx
    if systemctl is-active --quiet nginx; then
        echo -e "${GREEN}✅ Nginx: RUNNING${NC}"
    else
        echo -e "${RED}❌ Nginx: STOPPED${NC}"
    fi
    
    echo ""
    echo "Access URLs:"
    echo "  - http://publications.local"
    echo "  - http://192.168.111.79"
    echo ""
}

case "$1" in
    start)
        echo -e "${YELLOW}Starting services...${NC}"
        sudo systemctl start sjecportal
        sudo systemctl start nginx
        echo -e "${GREEN}✅ Services started${NC}"
        ;;
    
    stop)
        echo -e "${YELLOW}Stopping services...${NC}"
        sudo systemctl stop sjecportal
        echo -e "${GREEN}✅ Services stopped${NC}"
        ;;
    
    restart)
        echo -e "${YELLOW}Restarting portal service...${NC}"
        sudo systemctl restart sjecportal
        echo -e "${GREEN}✅ Portal restarted${NC}"
        ;;
    
    status)
        print_status
        ;;
    
    logs)
        echo -e "${YELLOW}Showing portal logs (Ctrl+C to exit)...${NC}"
        sudo journalctl -u sjecportal -f
        ;;
    
    nginx-logs)
        echo -e "${YELLOW}Showing Nginx logs (Ctrl+C to exit)...${NC}"
        sudo tail -f /var/log/nginx/sjecportal_access.log
        ;;
    
    backup)
        echo -e "${YELLOW}Starting backup...${NC}"
        bash /opt/sjec-publications/deployment/backup.sh
        ;;
    
    update)
        echo -e "${YELLOW}Updating from git...${NC}"
        cd /opt/sjec-publications
        git pull
        sudo systemctl restart sjecportal
        echo -e "${GREEN}✅ Updated and restarted${NC}"
        ;;
    
    shell)
        echo -e "${YELLOW}Opening Python shell...${NC}"
        cd /opt/sjec-publications
        source venv/bin/activate
        python3
        ;;
    
    *)
        print_header
        echo ""
        echo "Usage: $0 {command}"
        echo ""
        echo "Commands:"
        echo "  status       - Show service status"
        echo "  start        - Start all services"
        echo "  stop         - Stop portal service"
        echo "  restart      - Restart portal service"
        echo "  logs         - View portal logs (live)"
        echo "  nginx-logs   - View Nginx logs (live)"
        echo "  backup       - Create backup"
        echo "  update       - Pull from git and restart"
        echo "  shell        - Open Python shell"
        echo ""
        echo "Examples:"
        echo "  $0 status"
        echo "  $0 restart"
        echo "  $0 logs"
        echo ""
        ;;
esac
