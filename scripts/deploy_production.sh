#!/bin/bash
# Production deployment script for Kleinanzeigen Crawler
# Handles systemd service, monitoring, and production setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
SERVICE_NAME="kleinanzeigen-crawler"
SERVICE_USER="$USER"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
LOG_FILE="$PROJECT_ROOT/deploy.log"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if installation was completed
    if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
        error "Installation not complete. Please run ./scripts/install_complete.sh first"
    fi
    
    # Check if database is accessible
    if ! python3 "$PROJECT_ROOT/main.py" --test-db 2>/dev/null; then
        warning "Cannot connect to database. Please check your .env configuration"
    fi
    
    # Check sudo access
    if ! sudo -n true 2>/dev/null; then
        warning "This script requires sudo access for systemd setup"
        sudo -v
    fi
}

# Create systemd service
create_systemd_service() {
    log "Creating systemd service..."
    
    # Create service file
    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Kleinanzeigen Book Crawler
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$PROJECT_ROOT
Environment="PATH=/usr/bin:/bin:$HOME/.local/bin"
Environment="PYTHONPATH=$PROJECT_ROOT"

# Main command
ExecStart=/usr/bin/python3 $PROJECT_ROOT/main.py --schedule --headless

# Pre-start command to ensure database is ready
ExecStartPre=/bin/sleep 10

# Restart policy
Restart=always
RestartSec=30
StartLimitInterval=600
StartLimitBurst=5

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=$PROJECT_ROOT/logs
ReadWritePaths=$PROJECT_ROOT/data

# Resource limits
MemoryMax=2G
CPUQuota=50%

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    sudo systemctl daemon-reload
    
    log "Systemd service created: $SERVICE_NAME"
}

# Setup log rotation
setup_log_rotation() {
    log "Setting up log rotation..."
    
    sudo tee "/etc/logrotate.d/$SERVICE_NAME" > /dev/null <<EOF
$PROJECT_ROOT/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0644 $SERVICE_USER $SERVICE_USER
    sharedscripts
    postrotate
        systemctl reload $SERVICE_NAME > /dev/null 2>&1 || true
    endscript
}
EOF
    
    log "Log rotation configured"
}

# Create monitoring script
create_monitoring_script() {
    log "Creating monitoring script..."
    
    cat > "$PROJECT_ROOT/scripts/monitor_health.sh" <<'EOF'
#!/bin/bash
# Health monitoring script for Kleinanzeigen Crawler

PROJECT_ROOT="$(dirname "$(dirname "$0")")"
WEBHOOK_URL="$1"  # Optional webhook URL for alerts

# Check if service is running
if systemctl is-active --quiet kleinanzeigen-crawler; then
    echo "✅ Service is running"
else
    echo "❌ Service is not running"
    
    # Send alert if webhook URL is provided
    if [[ -n "$WEBHOOK_URL" ]]; then
        curl -X POST "$WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d '{"text":"⚠️ Kleinanzeigen Crawler service is down!"}'
    fi
    
    # Try to restart
    sudo systemctl restart kleinanzeigen-crawler
fi

# Check database connectivity
if python3 "$PROJECT_ROOT/main.py" --test-db 2>/dev/null; then
    echo "✅ Database connection OK"
else
    echo "❌ Database connection failed"
fi

# Check disk space
DISK_USAGE=$(df -h "$PROJECT_ROOT" | awk 'NR==2 {print $5}' | sed 's/%//')
if [[ $DISK_USAGE -gt 90 ]]; then
    echo "⚠️ Disk usage critical: ${DISK_USAGE}%"
else
    echo "✅ Disk usage OK: ${DISK_USAGE}%"
fi

# Check recent errors
ERROR_COUNT=$(grep -c ERROR "$PROJECT_ROOT"/logs/crawler_*.log 2>/dev/null || echo 0)
if [[ $ERROR_COUNT -gt 100 ]]; then
    echo "⚠️ High error count: $ERROR_COUNT errors in logs"
else
    echo "✅ Error count normal: $ERROR_COUNT errors"
fi
EOF
    
    chmod +x "$PROJECT_ROOT/scripts/monitor_health.sh"
    log "Monitoring script created"
}

# Setup cron jobs
setup_cron_jobs() {
    log "Setting up cron jobs..."
    
    # Create cron job for health monitoring
    CRON_CMD="*/30 * * * * $PROJECT_ROOT/scripts/monitor_health.sh >> $PROJECT_ROOT/logs/health.log 2>&1"
    
    # Add to crontab if not already present
    if ! crontab -l 2>/dev/null | grep -q "monitor_health.sh"; then
        (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
        log "Added health monitoring cron job"
    else
        info "Health monitoring cron job already exists"
    fi
    
    # Create cleanup cron job
    CLEANUP_CMD="0 3 * * 0 $PROJECT_ROOT/scripts/cleanup_old_data.sh >> $PROJECT_ROOT/logs/cleanup.log 2>&1"
    
    if ! crontab -l 2>/dev/null | grep -q "cleanup_old_data.sh"; then
        (crontab -l 2>/dev/null; echo "$CLEANUP_CMD") | crontab -
        log "Added cleanup cron job"
    fi
}

# Create cleanup script
create_cleanup_script() {
    log "Creating cleanup script..."
    
    cat > "$PROJECT_ROOT/scripts/cleanup_old_data.sh" <<EOF
#!/bin/bash
# Cleanup script for old data

PROJECT_ROOT="\$(dirname "\$(dirname "\$0")")"

# Clean up old logs (older than 30 days)
find "\$PROJECT_ROOT/logs" -name "*.log" -type f -mtime +30 -delete

# Clean up database (via Python script)
python3 "\$PROJECT_ROOT/tools/monitor.py" --cleanup 30

echo "Cleanup completed at \$(date)"
EOF
    
    chmod +x "$PROJECT_ROOT/scripts/cleanup_old_data.sh"
    log "Cleanup script created"
}

# Configure firewall
configure_firewall() {
    log "Checking firewall configuration..."
    
    # Check if ufw is installed and active
    if command -v ufw &> /dev/null && sudo ufw status | grep -q "Status: active"; then
        # PostgreSQL should only be accessible locally
        info "Firewall is active. PostgreSQL is configured for local access only."
    else
        info "Firewall not active. Consider enabling it for production."
    fi
}

# Optimize database
optimize_database() {
    log "Optimizing database..."
    
    # Run VACUUM and ANALYZE
    sudo -u postgres psql -d kleinanzeigen_crawler <<EOF
VACUUM ANALYZE;
EOF
    
    log "Database optimized"
}

# Start service
start_service() {
    log "Starting service..."
    
    # Enable service
    sudo systemctl enable "$SERVICE_NAME"
    
    # Start service
    sudo systemctl start "$SERVICE_NAME"
    
    # Wait a bit
    sleep 5
    
    # Check status
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        log "Service started successfully"
        sudo systemctl status "$SERVICE_NAME" --no-pager
    else
        error "Service failed to start. Check logs with: sudo journalctl -u $SERVICE_NAME -n 50"
    fi
}

# Create backup script
create_backup_script() {
    log "Creating backup script..."
    
    cat > "$PROJECT_ROOT/scripts/backup.sh" <<'EOF'
#!/bin/bash
# Backup script for Kleinanzeigen Crawler

PROJECT_ROOT="$(dirname "$(dirname "$0")")"
BACKUP_DIR="$PROJECT_ROOT/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Load database credentials
source "$PROJECT_ROOT/.env"

# Backup database
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    > "$BACKUP_DIR/db_backup_$DATE.sql"

# Compress backup
gzip "$BACKUP_DIR/db_backup_$DATE.sql"

# Backup configuration files
tar -czf "$BACKUP_DIR/config_backup_$DATE.tar.gz" \
    -C "$PROJECT_ROOT" \
    .env config.yaml

# Keep only last 7 backups
find "$BACKUP_DIR" -name "*.sql.gz" -type f -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/db_backup_$DATE.sql.gz"
EOF
    
    chmod +x "$PROJECT_ROOT/scripts/backup.sh"
    log "Backup script created"
}

# Main deployment flow
main() {
    echo "========================================"
    echo "Kleinanzeigen Crawler Production Deploy"
    echo "========================================"
    echo ""
    
    # Start logging
    echo "Deployment started at $(date)" > "$LOG_FILE"
    
    # Deployment steps
    check_prerequisites
    create_systemd_service
    setup_log_rotation
    create_monitoring_script
    create_cleanup_script
    create_backup_script
    setup_cron_jobs
    configure_firewall
    optimize_database
    start_service
    
    # Success message
    echo ""
    echo "========================================"
    log "Deployment completed successfully!"
    echo "========================================"
    echo ""
    echo "Service Management Commands:"
    echo "  Start:   sudo systemctl start $SERVICE_NAME"
    echo "  Stop:    sudo systemctl stop $SERVICE_NAME"
    echo "  Status:  sudo systemctl status $SERVICE_NAME"
    echo "  Logs:    sudo journalctl -u $SERVICE_NAME -f"
    echo ""
    echo "Monitoring Commands:"
    echo "  Health:  ./scripts/monitor_health.sh"
    echo "  Stats:   python3 tools/monitor.py --stats"
    echo "  Backup:  ./scripts/backup.sh"
    echo ""
    echo "The crawler is now running in production mode!"
    echo "Check status with: sudo systemctl status $SERVICE_NAME"
    echo ""
    echo "Deployment log saved to: $LOG_FILE"
}

# Run main function
main "$@"