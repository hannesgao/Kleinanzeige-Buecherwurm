#!/bin/bash
# Complete installation script for Kleinanzeigen Crawler
# This script handles all dependencies and setup

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

# Log file
LOG_FILE="$PROJECT_ROOT/install.log"

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

# Detect OS
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        OS_VERSION=$VERSION_ID
    else
        error "Cannot detect OS. This script requires a Linux distribution with /etc/os-release"
    fi
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root. Please run as a regular user with sudo access."
    fi
}

# Check sudo access
check_sudo() {
    if ! sudo -n true 2>/dev/null; then
        warning "This script requires sudo access. Please enter your password when prompted."
        sudo -v
    fi
}

# Install system dependencies
install_system_deps() {
    log "Installing system dependencies..."
    
    case $OS in
        ubuntu|debian)
            sudo apt update
            sudo apt install -y \
                python3 python3-pip python3-dev python3-venv \
                postgresql postgresql-contrib libpq-dev \
                build-essential wget curl git \
                gnupg ca-certificates lsb-release
            ;;
        fedora|rhel|centos)
            sudo dnf install -y \
                python3 python3-pip python3-devel \
                postgresql postgresql-server postgresql-contrib postgresql-devel \
                gcc gcc-c++ make wget curl git \
                redhat-lsb-core
            ;;
        *)
            error "Unsupported OS: $OS"
            ;;
    esac
}

# Install Chrome
install_chrome() {
    log "Installing Google Chrome..."
    
    # Check if Chrome is already installed
    if command -v google-chrome &> /dev/null || command -v google-chrome-stable &> /dev/null; then
        info "Google Chrome is already installed"
        return
    fi
    
    case $OS in
        ubuntu|debian)
            # Add Chrome repository
            wget -qO - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
            echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
            sudo apt update
            sudo apt install -y google-chrome-stable
            ;;
        fedora)
            sudo dnf install -y fedora-workstation-repositories
            sudo dnf config-manager --set-enabled google-chrome
            sudo dnf install -y google-chrome-stable
            ;;
        rhel|centos)
            sudo wget -O /etc/yum.repos.d/google-chrome.repo https://dl.google.com/linux/chrome/rpm/stable/x86_64/google-chrome.repo
            sudo dnf install -y google-chrome-stable
            ;;
    esac
}

# Setup PostgreSQL
setup_postgresql() {
    log "Setting up PostgreSQL..."
    
    # Start and enable PostgreSQL
    case $OS in
        ubuntu|debian)
            sudo systemctl start postgresql
            sudo systemctl enable postgresql
            ;;
        fedora|rhel|centos)
            sudo postgresql-setup --initdb || true
            sudo systemctl start postgresql
            sudo systemctl enable postgresql
            ;;
    esac
    
    # Check if database already exists
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw kleinanzeigen_crawler; then
        info "Database 'kleinanzeigen_crawler' already exists"
        return
    fi
    
    # Create database and user
    log "Creating database and user..."
    
    # Generate a random password
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    
    sudo -u postgres psql <<EOF
CREATE USER kleinanzeigen WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE kleinanzeigen_crawler OWNER kleinanzeigen;
GRANT ALL PRIVILEGES ON DATABASE kleinanzeigen_crawler TO kleinanzeigen;
\q
EOF
    
    # Save credentials
    echo "DB_PASSWORD=$DB_PASSWORD" > "$PROJECT_ROOT/.db_credentials"
    chmod 600 "$PROJECT_ROOT/.db_credentials"
    
    log "Database created successfully. Password saved in .db_credentials"
}

# Install Python dependencies
install_python_deps() {
    log "Installing Python dependencies..."
    
    cd "$PROJECT_ROOT"
    
    # Detect Python environment type
    if python3 -m pip --version 2>&1 | grep -q "externally-managed-environment"; then
        warning "Detected externally-managed Python environment"
        
        # Try to install via system packages first
        case $OS in
            ubuntu|debian)
                info "Attempting to install Python packages via apt..."
                sudo apt install -y \
                    python3-selenium python3-bs4 python3-sqlalchemy \
                    python3-psycopg2 python3-requests python3-yaml \
                    python3-dotenv python3-pandas python3-schedule || true
                ;;
        esac
        
        # Install remaining packages with pip
        info "Installing remaining packages with pip..."
        pip3 install --user -r requirements.txt
        
        # Add local bin to PATH
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
            export PATH="$HOME/.local/bin:$PATH"
            info "Added ~/.local/bin to PATH"
        fi
    else
        # Standard pip installation
        pip3 install -r requirements.txt
    fi
}

# Setup environment file
setup_env_file() {
    log "Setting up environment configuration..."
    
    cd "$PROJECT_ROOT"
    
    if [[ -f .env ]]; then
        warning ".env file already exists. Backing up to .env.backup"
        cp .env .env.backup
    fi
    
    # Copy template
    cp .env.example .env
    
    # Load database password
    if [[ -f .db_credentials ]]; then
        source .db_credentials
    else
        DB_PASSWORD="your-secure-password"
    fi
    
    # Update .env with database credentials
    sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" .env
    
    # Set secure permissions
    chmod 600 .env
    
    log "Environment file created. Please edit .env to add email settings."
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    cd "$PROJECT_ROOT"
    mkdir -p logs data
    chmod 755 logs data
}

# Initialize database
init_database() {
    log "Initializing database tables..."
    
    cd "$PROJECT_ROOT"
    
    # Check if we can connect to database
    if python3 main.py --init-db; then
        log "Database initialized successfully"
    else
        warning "Database initialization failed. Please check your credentials in .env"
    fi
}

# Run verification
verify_installation() {
    log "Verifying installation..."
    
    cd "$PROJECT_ROOT"
    
    if python3 tools/check_setup.py; then
        log "Installation verification passed"
    else
        warning "Some verification checks failed. Please review the output above."
    fi
}

# Main installation flow
main() {
    echo "======================================"
    echo "Kleinanzeigen Crawler Installation"
    echo "======================================"
    echo ""
    
    # Start logging
    echo "Installation started at $(date)" > "$LOG_FILE"
    
    # Pre-flight checks
    check_root
    check_sudo
    detect_os
    
    log "Detected OS: $OS $OS_VERSION"
    
    # Installation steps
    install_system_deps
    install_chrome
    setup_postgresql
    install_python_deps
    setup_env_file
    create_directories
    init_database
    verify_installation
    
    # Success message
    echo ""
    echo "======================================"
    log "Installation completed successfully!"
    echo "======================================"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file to add your email settings"
    echo "2. Test the crawler: python3 main.py --test --headless"
    echo "3. Run the crawler: python3 main.py --schedule"
    echo ""
    echo "For production deployment, run: ./scripts/deploy_production.sh"
    echo ""
    echo "Installation log saved to: $LOG_FILE"
}

# Run main function
main "$@"