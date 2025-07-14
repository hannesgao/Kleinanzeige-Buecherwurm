#!/bin/bash
# Quick start script for Kleinanzeigen Crawler
# One-command setup for development/testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# ASCII Art Banner
show_banner() {
    echo -e "${PURPLE}"
    cat << "EOF"
    _  ___      _                           _                 
   | |/ / |    (_)                         (_)                
   | ' /| | ___ _ _ __   __ _ _ __  _______  __ _  ___ _ __  
   |  < | |/ _ \ | '_ \ / _` | '_ \|_  / _ \/ _` |/ _ \ '_ \ 
   | . \| |  __/ | | | | (_| | | | |/ /  __/ (_| |  __/ | | |
   |_|\_\_|\___|_|_| |_|\__,_|_| |_/___\___|\__, |\___|_| |_|
                                              __/ |           
       Bücherwurm - Book Crawler             |___/            
EOF
    echo -e "${NC}"
}

# Functions
log() {
    echo -e "${GREEN}[✓]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# Progress indicator
show_progress() {
    local pid=$1
    local delay=0.1
    local spinstr='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

# Check system
check_system() {
    echo -e "\n${BLUE}=== System Check ===${NC}\n"
    
    # Check OS
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        info "Operating System: $NAME $VERSION"
    fi
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log "Python $PYTHON_VERSION found"
    else
        error "Python 3 not found. Please install Python 3.8+"
    fi
    
    # Check PostgreSQL
    if command -v psql &> /dev/null; then
        log "PostgreSQL client found"
    else
        warning "PostgreSQL not found. Will install if needed."
    fi
    
    # Check Chrome
    if command -v google-chrome &> /dev/null || command -v chromium &> /dev/null; then
        log "Chrome/Chromium browser found"
    else
        warning "Chrome not found. Will install if needed."
    fi
}

# Quick install dependencies
quick_install_deps() {
    echo -e "\n${BLUE}=== Installing Dependencies ===${NC}\n"
    
    # Detect package manager
    if command -v apt &> /dev/null; then
        PKG_MANAGER="apt"
        info "Using apt package manager"
        
        # Update package list
        info "Updating package list..."
        sudo apt update -qq
        
        # Install essentials
        info "Installing essential packages..."
        sudo apt install -y -qq \
            python3 python3-pip python3-venv \
            postgresql postgresql-contrib \
            git curl wget build-essential
            
    elif command -v dnf &> /dev/null; then
        PKG_MANAGER="dnf"
        info "Using dnf package manager"
        
        sudo dnf install -y \
            python3 python3-pip \
            postgresql postgresql-server \
            git curl wget gcc
    else
        error "Unsupported package manager. Please install dependencies manually."
    fi
    
    log "System dependencies installed"
}

# Quick database setup
quick_db_setup() {
    echo -e "\n${BLUE}=== Database Setup ===${NC}\n"
    
    # Start PostgreSQL
    info "Starting PostgreSQL..."
    sudo systemctl start postgresql 2>/dev/null || true
    
    # Use simple password for quick start
    DB_PASSWORD="kleinanzeigen123"
    
    info "Creating database and user..."
    sudo -u postgres psql 2>/dev/null <<EOF || true
CREATE USER kleinanzeigen WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE kleinanzeigen_crawler OWNER kleinanzeigen;
GRANT ALL PRIVILEGES ON DATABASE kleinanzeigen_crawler TO kleinanzeigen;
EOF
    
    # Create .env file
    cat > "$PROJECT_ROOT/.env" <<EOF
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=kleinanzeigen_crawler
DB_USER=kleinanzeigen
DB_PASSWORD=$DB_PASSWORD

# Email Configuration (update these!)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFICATION_EMAIL=recipient@example.com

# Crawler Settings
DEBUG=False
EOF
    
    chmod 600 "$PROJECT_ROOT/.env"
    log "Database configured (password: $DB_PASSWORD)"
}

# Quick Python setup
quick_python_setup() {
    echo -e "\n${BLUE}=== Python Setup ===${NC}\n"
    
    cd "$PROJECT_ROOT"
    
    # Try to install Python packages
    info "Installing Python packages..."
    
    # First try without any flags
    if pip3 install -r requirements.txt &>/dev/null; then
        log "Python packages installed"
    else
        # Try with --user flag
        info "Trying user installation..."
        if pip3 install --user -r requirements.txt &>/dev/null; then
            log "Python packages installed (user)"
            export PATH="$HOME/.local/bin:$PATH"
        else
            # Try with break-system-packages
            info "Trying system installation..."
            pip3 install --break-system-packages -r requirements.txt &>/dev/null || \
            warning "Some packages may need manual installation"
        fi
    fi
}

# Initialize and test
initialize_and_test() {
    echo -e "\n${BLUE}=== Initialization ===${NC}\n"
    
    cd "$PROJECT_ROOT"
    
    # Create directories
    mkdir -p logs data
    
    # Initialize database
    info "Initializing database tables..."
    python3 main.py --init-db 2>/dev/null || warning "Database initialization needs manual setup"
    
    # Run a test
    info "Running test crawl..."
    if python3 main.py --test --headless 2>/dev/null; then
        log "Test crawl successful!"
    else
        warning "Test crawl failed. Please check configuration."
    fi
}

# Show next steps
show_next_steps() {
    echo -e "\n${GREEN}=== Quick Start Complete! ===${NC}\n"
    
    echo "Next steps:"
    echo ""
    echo "1. ${YELLOW}IMPORTANT:${NC} Edit .env file to add your email settings:"
    echo "   nano $PROJECT_ROOT/.env"
    echo ""
    echo "2. Test the crawler:"
    echo "   cd $PROJECT_ROOT"
    echo "   python3 main.py --test"
    echo ""
    echo "3. Run the crawler:"
    echo "   python3 main.py --schedule"
    echo ""
    echo "4. For production deployment:"
    echo "   ./scripts/deploy_production.sh"
    echo ""
    echo "5. Monitor the crawler:"
    echo "   python3 tools/monitor.py --stats"
    echo ""
    
    if [[ -f "$PROJECT_ROOT/.env" ]]; then
        echo -e "${YELLOW}Remember to update your email settings in .env!${NC}"
    fi
}

# Main quick start flow
main() {
    clear
    show_banner
    
    echo "Welcome to Kleinanzeigen Crawler Quick Start!"
    echo "This script will set up everything needed to run the crawler."
    echo ""
    
    read -p "Continue with quick setup? (Y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        exit 0
    fi
    
    # Run setup steps
    check_system
    
    # Ask about dependency installation
    read -p "Install system dependencies? (Y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        quick_install_deps
    fi
    
    quick_db_setup
    quick_python_setup
    initialize_and_test
    show_next_steps
}

# Run main function
main "$@"