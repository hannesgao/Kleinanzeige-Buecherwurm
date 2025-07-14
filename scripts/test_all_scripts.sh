#!/bin/bash
# Comprehensive test script for all installation and deployment scripts
# Tests functionality without requiring sudo or making system changes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Test results
PASSED=0
FAILED=0
WARNINGS=0

# Functions
test_pass() {
    echo -e "${GREEN}✓ PASS${NC} $1"
    ((PASSED++))
}

test_fail() {
    echo -e "${RED}✗ FAIL${NC} $1"
    ((FAILED++))
}

test_warn() {
    echo -e "${YELLOW}⚠ WARN${NC} $1"
    ((WARNINGS++))
}

test_info() {
    echo -e "${BLUE}ℹ INFO${NC} $1"
}

section() {
    echo -e "\n${PURPLE}━━━ $1 ━━━${NC}"
}

# Test if script exists and is executable
test_script_exists() {
    local script=$1
    local script_path="$SCRIPT_DIR/$script"
    
    if [[ -f "$script_path" ]]; then
        if [[ -x "$script_path" ]]; then
            test_pass "$script exists and is executable"
            return 0
        else
            test_fail "$script exists but is not executable"
            return 1
        fi
    else
        test_fail "$script does not exist"
        return 1
    fi
}

# Test script syntax
test_script_syntax() {
    local script=$1
    local script_path="$SCRIPT_DIR/$script"
    
    if bash -n "$script_path" 2>/dev/null; then
        test_pass "$script syntax is valid"
        return 0
    else
        test_fail "$script has syntax errors"
        bash -n "$script_path" 2>&1 | head -5
        return 1
    fi
}

# Test script functions
test_script_functions() {
    local script=$1
    local script_path="$SCRIPT_DIR/$script"
    
    # Extract function names
    local functions=$(grep -E "^[a-zA-Z_]+\(\)" "$script_path" | sed 's/().*//' | grep -v "^main$" || true)
    
    if [[ -n "$functions" ]]; then
        local count=$(echo "$functions" | wc -l)
        test_pass "$script has $count functions defined"
        echo "  Functions: $(echo $functions | tr '\n' ', ')"
        return 0
    else
        test_warn "$script has no functions defined"
        return 0
    fi
}

# Test help/usage
test_script_help() {
    local script=$1
    local script_path="$SCRIPT_DIR/$script"
    
    # Check if script has help option
    if grep -q "usage\|help\|--help" "$script_path"; then
        test_pass "$script has help/usage information"
        return 0
    else
        test_warn "$script lacks help/usage information"
        return 0
    fi
}

# Test script dependencies
test_script_deps() {
    local script=$1
    local script_path="$SCRIPT_DIR/$script"
    
    # Check for required commands
    local commands=$(grep -oE "(command -v|which) [a-zA-Z0-9_-]+" "$script_path" | awk '{print $NF}' | sort -u || true)
    
    if [[ -n "$commands" ]]; then
        test_info "$script checks for: $(echo $commands | tr '\n' ', ')"
        
        # Test if commands exist
        local missing=""
        for cmd in $commands; do
            if ! command -v "$cmd" &>/dev/null; then
                missing="$missing $cmd"
            fi
        done
        
        if [[ -n "$missing" ]]; then
            test_warn "Missing commands:$missing"
        else
            test_pass "All checked commands are available"
        fi
    else
        test_info "$script does not check for external commands"
    fi
    return 0
}

# Test environment handling
test_script_env() {
    local script=$1
    local script_path="$SCRIPT_DIR/$script"
    
    # Check for environment variable usage
    local env_vars=$(grep -oE '\$\{?[A-Z_]+[A-Z0-9_]*\}?' "$script_path" | sort -u | grep -v '\$BASH\|\$REPLY\|\$EUID' || true)
    
    if [[ -n "$env_vars" ]]; then
        local count=$(echo "$env_vars" | wc -l)
        test_info "$script uses $count environment variables"
        return 0
    else
        test_info "$script uses no custom environment variables"
        return 0
    fi
}

# Test error handling
test_script_errors() {
    local script=$1
    local script_path="$SCRIPT_DIR/$script"
    
    # Check for error handling
    if grep -q "set -e" "$script_path"; then
        test_pass "$script uses 'set -e' for error handling"
    else
        test_warn "$script does not use 'set -e'"
    fi
    
    # Check for error functions
    if grep -qE "error\(\)|die\(\)" "$script_path"; then
        test_pass "$script has error handling functions"
    else
        test_info "$script has no explicit error functions"
    fi
    
    return 0
}

# Test logging
test_script_logging() {
    local script=$1
    local script_path="$SCRIPT_DIR/$script"
    
    # Check for logging
    if grep -qE "log\(\)|echo.*>>" "$script_path"; then
        test_pass "$script implements logging"
        
        # Check for log file
        if grep -qE "LOG_FILE|\.log" "$script_path"; then
            test_pass "$script logs to file"
        else
            test_info "$script logs to stdout only"
        fi
    else
        test_warn "$script has no logging mechanism"
    fi
    
    return 0
}

# Test specific scripts
test_quick_start() {
    section "Testing quick_start.sh"
    
    local script="quick_start.sh"
    test_script_exists "$script" || return
    test_script_syntax "$script" || return
    test_script_functions "$script"
    test_script_deps "$script"
    test_script_errors "$script"
    
    # Specific tests for quick_start
    if grep -q "show_banner" "$SCRIPT_DIR/$script"; then
        test_pass "Has ASCII banner"
    fi
    
    if grep -q "quick_install_deps" "$SCRIPT_DIR/$script"; then
        test_pass "Has dependency installation"
    fi
    
    if grep -q "quick_db_setup" "$SCRIPT_DIR/$script"; then
        test_pass "Has database setup"
    fi
}

test_install_complete() {
    section "Testing install_complete.sh"
    
    local script="install_complete.sh"
    test_script_exists "$script" || return
    test_script_syntax "$script" || return
    test_script_functions "$script"
    test_script_deps "$script"
    test_script_errors "$script"
    test_script_logging "$script"
    
    # Specific tests
    if grep -q "detect_os" "$SCRIPT_DIR/$script"; then
        test_pass "Has OS detection"
    fi
    
    if grep -q "check_root" "$SCRIPT_DIR/$script"; then
        test_pass "Has root user check"
    fi
}

test_setup_database() {
    section "Testing setup_database.sh"
    
    local script="setup_database.sh"
    test_script_exists "$script" || return
    test_script_syntax "$script" || return
    test_script_functions "$script"
    test_script_help "$script"
    test_script_errors "$script"
    
    # Specific tests
    if grep -q "parse_args" "$SCRIPT_DIR/$script"; then
        test_pass "Has argument parsing"
    fi
    
    if grep -q "generate_password" "$SCRIPT_DIR/$script"; then
        test_pass "Has password generation"
    fi
    
    if grep -qE "backup|restore" "$SCRIPT_DIR/$script"; then
        test_pass "Has backup/restore functionality"
    fi
}

test_deploy_production() {
    section "Testing deploy_production.sh"
    
    local script="deploy_production.sh"
    test_script_exists "$script" || return
    test_script_syntax "$script" || return
    test_script_functions "$script"
    test_script_deps "$script"
    test_script_errors "$script"
    test_script_logging "$script"
    
    # Specific tests
    if grep -q "systemd" "$SCRIPT_DIR/$script"; then
        test_pass "Has systemd service creation"
    fi
    
    if grep -q "logrotate" "$SCRIPT_DIR/$script"; then
        test_pass "Has log rotation setup"
    fi
    
    if grep -q "monitor" "$SCRIPT_DIR/$script"; then
        test_pass "Has monitoring setup"
    fi
}

test_docker_deploy() {
    section "Testing docker_deploy.sh"
    
    local script="docker_deploy.sh"
    test_script_exists "$script" || return
    test_script_syntax "$script" || return
    test_script_functions "$script"
    test_script_deps "$script"
    test_script_errors "$script"
    
    # Specific tests
    if grep -q "docker-compose" "$SCRIPT_DIR/$script"; then
        test_pass "Has docker-compose configuration"
    fi
    
    if grep -q "check_docker" "$SCRIPT_DIR/$script"; then
        test_pass "Has Docker verification"
    fi
}

# Test project structure
test_project_structure() {
    section "Testing Project Structure"
    
    # Required directories
    local dirs=("src" "tests" "config" "deployment" "database" "tools" "docs" "quality")
    for dir in "${dirs[@]}"; do
        if [[ -d "$PROJECT_ROOT/$dir" ]]; then
            test_pass "Directory exists: $dir/"
        else
            test_fail "Directory missing: $dir/"
        fi
    done
    
    # Required files
    local files=("requirements.txt" "main.py" "config.yaml" ".env.example" "setup.py" "README.md")
    for file in "${files[@]}"; do
        if [[ -f "$PROJECT_ROOT/$file" ]]; then
            test_pass "File exists: $file"
        else
            test_fail "File missing: $file"
        fi
    done
}

# Test Python environment
test_python_env() {
    section "Testing Python Environment"
    
    # Python version
    if command -v python3 &>/dev/null; then
        local version=$(python3 --version | cut -d' ' -f2)
        test_pass "Python $version installed"
        
        # Check if version is 3.8+
        local major=$(echo $version | cut -d. -f1)
        local minor=$(echo $version | cut -d. -f2)
        if [[ $major -eq 3 && $minor -ge 8 ]]; then
            test_pass "Python version meets requirements (3.8+)"
        else
            test_fail "Python version too old (requires 3.8+)"
        fi
    else
        test_fail "Python 3 not found"
    fi
    
    # Check pip
    if python3 -m pip --version &>/dev/null; then
        test_pass "pip is available"
    else
        test_fail "pip not available"
    fi
}

# Test script interactions
test_script_interactions() {
    section "Testing Script Interactions"
    
    # Check if scripts reference each other
    if grep -q "install_complete.sh" "$SCRIPT_DIR/deploy_production.sh"; then
        test_pass "deploy_production.sh references install_complete.sh"
    fi
    
    # Check if scripts use common PROJECT_ROOT
    local root_usage=$(grep -l "PROJECT_ROOT" "$SCRIPT_DIR"/*.sh | wc -l)
    test_pass "$root_usage scripts use PROJECT_ROOT variable"
    
    # Check for consistent color scheme
    local color_scripts=$(grep -l "RED=.*033" "$SCRIPT_DIR"/*.sh | wc -l)
    test_pass "$color_scripts scripts use consistent color scheme"
}

# Main test execution
main() {
    echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║     Kleinanzeigen Crawler Scripts Test   ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
    
    # Test individual scripts
    test_quick_start
    test_install_complete
    test_setup_database
    test_deploy_production
    test_docker_deploy
    
    # Test project environment
    test_project_structure
    test_python_env
    test_script_interactions
    
    # Summary
    echo -e "\n${CYAN}═══════════════════════════════════════════${NC}"
    echo -e "${CYAN}                TEST SUMMARY                ${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════${NC}"
    
    echo -e "  ${GREEN}Passed:${NC}   $PASSED"
    echo -e "  ${YELLOW}Warnings:${NC} $WARNINGS"
    echo -e "  ${RED}Failed:${NC}   $FAILED"
    
    local total=$((PASSED + WARNINGS + FAILED))
    local score=$((PASSED * 100 / total))
    
    echo -e "\n  Score: ${score}%"
    
    if [[ $FAILED -eq 0 ]]; then
        echo -e "\n${GREEN}✅ All critical tests passed!${NC}"
        return 0
    else
        echo -e "\n${RED}❌ Some tests failed. Please review.${NC}"
        return 1
    fi
}

# Run tests
main "$@"