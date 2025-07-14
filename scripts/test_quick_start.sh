#!/bin/bash
# Test version of quick_start.sh - non-interactive for testing

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

echo -e "${PURPLE}=== Quick Start Script Test ===${NC}\n"

# Test 1: Check system detection
echo "Test 1: System Detection"
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    log "OS detected: $NAME $VERSION"
else
    error "Cannot detect OS"
fi

# Test 2: Check Python
echo -e "\nTest 2: Python Check"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log "Python $PYTHON_VERSION found at $(which python3)"
else
    error "Python 3 not found"
fi

# Test 3: Check PostgreSQL
echo -e "\nTest 3: PostgreSQL Check"
if command -v psql &> /dev/null; then
    log "PostgreSQL client found at $(which psql)"
else
    warning "PostgreSQL client not found"
fi

# Test 4: Check Chrome
echo -e "\nTest 4: Chrome Check"
if command -v google-chrome &> /dev/null; then
    log "Google Chrome found at $(which google-chrome)"
elif command -v chromium &> /dev/null; then
    log "Chromium found at $(which chromium)"
else
    warning "Chrome/Chromium not found"
fi

# Test 5: Check project structure
echo -e "\nTest 5: Project Structure Check"
required_files=("requirements.txt" "main.py" "config.yaml" ".env.example")
missing_files=()

for file in "${required_files[@]}"; do
    if [[ -f "$PROJECT_ROOT/$file" ]]; then
        log "Found: $file"
    else
        missing_files+=("$file")
        warning "Missing: $file"
    fi
done

if [[ ${#missing_files[@]} -eq 0 ]]; then
    log "All required files present"
else
    error "Missing ${#missing_files[@]} required files"
fi

# Test 6: Check if .env exists
echo -e "\nTest 6: Environment Configuration"
if [[ -f "$PROJECT_ROOT/.env" ]]; then
    log ".env file exists"
    # Check if it has required variables
    if grep -q "DB_PASSWORD" "$PROJECT_ROOT/.env"; then
        log "Database configuration found in .env"
    else
        warning "Database configuration missing in .env"
    fi
else
    warning ".env file not found (would be created by script)"
fi

# Test 7: Check directories
echo -e "\nTest 7: Directory Check"
dirs=("logs" "data" "scripts" "src" "tests")
for dir in "${dirs[@]}"; do
    if [[ -d "$PROJECT_ROOT/$dir" ]]; then
        log "Directory exists: $dir/"
    else
        warning "Directory missing: $dir/ (would be created)"
    fi
done

# Test 8: Check Python imports
echo -e "\nTest 8: Python Import Test"
python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
try:
    import main
    print('✓ main.py imports successfully')
except ImportError as e:
    print('✗ Import error:', e)
"

# Test 9: Check if we can write to project directory
echo -e "\nTest 9: Write Permission Test"
TEST_FILE="$PROJECT_ROOT/.test_write_permission"
if touch "$TEST_FILE" 2>/dev/null; then
    rm "$TEST_FILE"
    log "Write permissions OK for $PROJECT_ROOT"
else
    error "No write permissions for $PROJECT_ROOT"
fi

# Test 10: Package manager detection
echo -e "\nTest 10: Package Manager Detection"
if command -v apt &> /dev/null; then
    log "APT package manager detected (Debian/Ubuntu)"
elif command -v dnf &> /dev/null; then
    log "DNF package manager detected (Fedora/RHEL)"
elif command -v yum &> /dev/null; then
    log "YUM package manager detected (older RHEL/CentOS)"
else
    warning "No supported package manager detected"
fi

# Summary
echo -e "\n${PURPLE}=== Test Summary ===${NC}"
echo "Project Root: $PROJECT_ROOT"
echo "Script Dir: $SCRIPT_DIR"
echo "Python Path: $(which python3)"
echo "User: $USER"
echo "Working Directory: $(pwd)"

# Test what would happen with database setup
echo -e "\n${BLUE}=== Database Setup Preview ===${NC}"
echo "Would create database: kleinanzeigen_crawler"
echo "Would create user: kleinanzeigen"
echo "Would generate password: [auto-generated]"
echo "Would save to: $PROJECT_ROOT/.env"

# Test Python package installation method
echo -e "\n${BLUE}=== Python Package Installation Test ===${NC}"
if python3 -m pip --version 2>&1 | grep -q "externally-managed-environment"; then
    warning "Detected externally-managed Python environment"
    echo "Would use: pip3 install --user -r requirements.txt"
else
    log "Standard Python environment"
    echo "Would use: pip3 install -r requirements.txt"
fi

echo -e "\n${GREEN}Quick Start script validation complete!${NC}"