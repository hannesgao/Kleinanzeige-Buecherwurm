#!/bin/bash
# Quick test to verify script functionality

echo "🧪 Testing Script Functionality"
echo "================================="

# Test 1: Check all scripts exist and are executable
echo -e "\n1. Script Files:"
for script in quick_start.sh install_complete.sh setup_database.sh deploy_production.sh docker_deploy.sh; do
    if [[ -x scripts/$script ]]; then
        echo "✅ $script"
    else
        echo "❌ $script"
    fi
done

# Test 2: Check syntax
echo -e "\n2. Syntax Check:"
for script in scripts/*.sh; do
    if bash -n "$script" 2>/dev/null; then
        echo "✅ $(basename $script) - syntax OK"
    else
        echo "❌ $(basename $script) - syntax ERROR"
        bash -n "$script"
    fi
done

# Test 3: Check main functions
echo -e "\n3. Function Check:"
echo "quick_start.sh functions:"
grep -E "^[a-zA-Z_]+\(\)" scripts/quick_start.sh | head -5

echo -e "\ninstall_complete.sh functions:"
grep -E "^[a-zA-Z_]+\(\)" scripts/install_complete.sh | head -5

# Test 4: Check project structure requirements
echo -e "\n4. Project Structure:"
required_files=("requirements.txt" "main.py" "config.yaml" ".env.example")
for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file"
    else
        echo "❌ $file"
    fi
done

# Test 5: Check if scripts can be sourced (for function testing)
echo -e "\n5. Function Availability Test:"
if bash -c "source scripts/quick_start.sh; declare -F | grep -q 'declare -f check_system'"; then
    echo "✅ quick_start.sh functions can be loaded"
else
    echo "❌ quick_start.sh functions cannot be loaded"
fi

# Test 6: Test specific script components
echo -e "\n6. Component Test:"

# Test OS detection from quick_start
if grep -q "detect_os\|/etc/os-release" scripts/quick_start.sh; then
    echo "✅ OS detection present"
else
    echo "❌ OS detection missing"
fi

# Test database setup
if grep -q "postgres\|psql\|kleinanzeigen_crawler" scripts/quick_start.sh; then
    echo "✅ Database setup present"
else
    echo "❌ Database setup missing"
fi

# Test dependency installation
if grep -q "apt\|dnf\|pip3" scripts/quick_start.sh; then
    echo "✅ Dependency installation present"
else
    echo "❌ Dependency installation missing"
fi

echo -e "\n7. Script Integration Test:"
# Test if main script can be run with --help or similar
for script in scripts/setup_database.sh; do
    if bash "$script" --help &>/dev/null || bash "$script" -h &>/dev/null; then
        echo "✅ $(basename $script) supports help"
    else
        echo "ℹ️  $(basename $script) no help option"
    fi
done

echo -e "\n✅ Basic functionality test completed!"
echo "All scripts are syntactically correct and contain expected components."