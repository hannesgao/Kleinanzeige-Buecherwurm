#!/bin/bash
# Database setup and management script for Kleinanzeigen Crawler
# Handles database creation, user management, and migrations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default values
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="kleinanzeigen_crawler"
DB_USER="kleinanzeigen"
ACTION="setup"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Usage information
usage() {
    cat << EOF
Usage: $0 [OPTIONS] [ACTION]

Actions:
    setup       Create database and user (default)
    reset       Drop and recreate database
    backup      Backup database
    restore     Restore database from backup
    migrate     Run database migrations
    status      Check database status

Options:
    -h, --host      Database host (default: localhost)
    -p, --port      Database port (default: 5432)
    -d, --database  Database name (default: kleinanzeigen_crawler)
    -u, --user      Database user (default: kleinanzeigen)
    -f, --file      Backup file (for restore action)
    --help          Show this help message

Examples:
    $0 setup                    # Create database and user
    $0 backup                   # Backup database
    $0 restore -f backup.sql    # Restore from backup
    $0 reset                    # Reset database (CAUTION!)
    $0 status                   # Check database status
EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--host)
                DB_HOST="$2"
                shift 2
                ;;
            -p|--port)
                DB_PORT="$2"
                shift 2
                ;;
            -d|--database)
                DB_NAME="$2"
                shift 2
                ;;
            -u|--user)
                DB_USER="$2"
                shift 2
                ;;
            -f|--file)
                BACKUP_FILE="$2"
                shift 2
                ;;
            --help)
                usage
                exit 0
                ;;
            setup|reset|backup|restore|migrate|status)
                ACTION="$1"
                shift
                ;;
            *)
                error "Unknown option: $1"
                ;;
        esac
    done
}

# Check PostgreSQL installation
check_postgresql() {
    if ! command -v psql &> /dev/null; then
        error "PostgreSQL client not found. Please install PostgreSQL first."
    fi
    
    # Check if PostgreSQL is running
    if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" &> /dev/null; then
        error "PostgreSQL is not running on $DB_HOST:$DB_PORT"
    fi
}

# Generate secure password
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Setup database
setup_database() {
    log "Setting up database..."
    
    # Check if database already exists
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        warning "Database '$DB_NAME' already exists"
        read -p "Do you want to continue? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
        return
    fi
    
    # Generate password
    DB_PASSWORD=$(generate_password)
    
    # Create user and database
    log "Creating database user and database..."
    sudo -u postgres psql <<EOF
-- Create user
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Create database
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Connect to the database and set up extensions
\c $DB_NAME

-- Create schema if needed
CREATE SCHEMA IF NOT EXISTS public AUTHORIZATION $DB_USER;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO $DB_USER;
EOF
    
    # Save credentials
    cat > "$PROJECT_ROOT/.db_credentials" <<EOF
# Database credentials (generated $(date))
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
EOF
    chmod 600 "$PROJECT_ROOT/.db_credentials"
    
    # Update .env file if it exists
    if [[ -f "$PROJECT_ROOT/.env" ]]; then
        log "Updating .env file with database credentials..."
        sed -i "s/^DB_HOST=.*/DB_HOST=$DB_HOST/" "$PROJECT_ROOT/.env"
        sed -i "s/^DB_PORT=.*/DB_PORT=$DB_PORT/" "$PROJECT_ROOT/.env"
        sed -i "s/^DB_NAME=.*/DB_NAME=$DB_NAME/" "$PROJECT_ROOT/.env"
        sed -i "s/^DB_USER=.*/DB_USER=$DB_USER/" "$PROJECT_ROOT/.env"
        sed -i "s/^DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" "$PROJECT_ROOT/.env"
    fi
    
    log "Database setup complete. Credentials saved in .db_credentials"
    
    # Initialize tables
    init_tables
}

# Initialize database tables
init_tables() {
    log "Initializing database tables..."
    
    cd "$PROJECT_ROOT"
    
    # Check if main.py exists
    if [[ -f "main.py" ]]; then
        if python3 main.py --init-db; then
            log "Database tables initialized successfully"
        else
            warning "Failed to initialize tables. Please check your Python environment."
        fi
    else
        # Use SQL schema directly
        if [[ -f "database/schema.sql" ]]; then
            log "Applying schema.sql..."
            PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" < database/schema.sql
            log "Schema applied successfully"
        else
            warning "Neither main.py nor schema.sql found. Tables not initialized."
        fi
    fi
}

# Reset database
reset_database() {
    warning "This will DELETE all data in the database!"
    read -p "Are you sure you want to reset the database? (yes/NO) " -r
    if [[ ! $REPLY == "yes" ]]; then
        info "Reset cancelled"
        exit 0
    fi
    
    log "Resetting database..."
    
    # Drop and recreate database
    sudo -u postgres psql <<EOF
-- Terminate connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();

-- Drop database
DROP DATABASE IF EXISTS $DB_NAME;

-- Drop user
DROP USER IF EXISTS $DB_USER;
EOF
    
    # Run setup again
    setup_database
}

# Backup database
backup_database() {
    log "Backing up database..."
    
    # Create backup directory
    BACKUP_DIR="$PROJECT_ROOT/backups"
    mkdir -p "$BACKUP_DIR"
    
    # Generate backup filename
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/kleinanzeigen_backup_${TIMESTAMP}.sql"
    
    # Load credentials if available
    if [[ -f "$PROJECT_ROOT/.db_credentials" ]]; then
        source "$PROJECT_ROOT/.db_credentials"
    elif [[ -f "$PROJECT_ROOT/.env" ]]; then
        source "$PROJECT_ROOT/.env"
    else
        error "No credentials found. Please run setup first."
    fi
    
    # Perform backup
    PGPASSWORD="$DB_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --clean \
        --if-exists \
        > "$BACKUP_FILE"
    
    # Compress backup
    gzip "$BACKUP_FILE"
    
    log "Backup completed: ${BACKUP_FILE}.gz"
    
    # Clean old backups (keep last 7)
    log "Cleaning old backups..."
    find "$BACKUP_DIR" -name "kleinanzeigen_backup_*.sql.gz" -type f -mtime +7 -delete
}

# Restore database
restore_database() {
    if [[ -z "$BACKUP_FILE" ]]; then
        error "Please specify backup file with -f option"
    fi
    
    if [[ ! -f "$BACKUP_FILE" ]]; then
        error "Backup file not found: $BACKUP_FILE"
    fi
    
    warning "This will REPLACE all data in the database!"
    read -p "Are you sure you want to restore from backup? (yes/NO) " -r
    if [[ ! $REPLY == "yes" ]]; then
        info "Restore cancelled"
        exit 0
    fi
    
    log "Restoring database from $BACKUP_FILE..."
    
    # Load credentials
    if [[ -f "$PROJECT_ROOT/.db_credentials" ]]; then
        source "$PROJECT_ROOT/.db_credentials"
    elif [[ -f "$PROJECT_ROOT/.env" ]]; then
        source "$PROJECT_ROOT/.env"
    else
        error "No credentials found. Please run setup first."
    fi
    
    # Check if file is compressed
    if [[ "$BACKUP_FILE" == *.gz ]]; then
        log "Decompressing backup..."
        gunzip -c "$BACKUP_FILE" | PGPASSWORD="$DB_PASSWORD" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME"
    else
        PGPASSWORD="$DB_PASSWORD" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" \
            < "$BACKUP_FILE"
    fi
    
    log "Database restored successfully"
}

# Check database status
check_status() {
    log "Checking database status..."
    
    # Load credentials
    if [[ -f "$PROJECT_ROOT/.db_credentials" ]]; then
        source "$PROJECT_ROOT/.db_credentials"
    elif [[ -f "$PROJECT_ROOT/.env" ]]; then
        source "$PROJECT_ROOT/.env"
    else
        warning "No credentials found. Using defaults."
        DB_PASSWORD=""
    fi
    
    # Check connection
    if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c '\l' &> /dev/null; then
        info "✅ Database connection successful"
        
        # Get database size
        DB_SIZE=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT pg_database_size('$DB_NAME');")
        DB_SIZE_HR=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));")
        
        info "Database size: $DB_SIZE_HR"
        
        # Get table information
        log "Tables in database:"
        PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\dt"
        
        # Get row counts
        log "Row counts:"
        PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
SELECT 'book_listings' as table_name, COUNT(*) as row_count FROM book_listings
UNION ALL
SELECT 'crawl_sessions' as table_name, COUNT(*) as row_count FROM crawl_sessions;
EOF
        
    else
        error "❌ Cannot connect to database"
    fi
}

# Main function
main() {
    parse_args "$@"
    check_postgresql
    
    case $ACTION in
        setup)
            setup_database
            ;;
        reset)
            reset_database
            ;;
        backup)
            backup_database
            ;;
        restore)
            restore_database
            ;;
        status)
            check_status
            ;;
        *)
            error "Unknown action: $ACTION"
            ;;
    esac
}

# Run main function
main "$@"