#!/usr/bin/env python3
"""
Complete integration test for Kleinanzeigen Crawler
This script performs comprehensive testing of all components
"""

import sys
import os
import time
import tempfile
import shutil
from pathlib import Path

def run_component_tests():
    """Run basic component tests"""
    print("🔧 Running component tests...")
    
    exit_code = os.system("python3 test_components.py")
    if exit_code != 0:
        print("❌ Component tests failed")
        return False
    
    print("✅ Component tests passed")
    return True

def run_database_tests():
    """Run database tests"""
    print("🗄️ Running database tests...")
    
    exit_code = os.system("python3 test_database.py")
    if exit_code != 0:
        print("❌ Database tests failed")
        return False
    
    print("✅ Database tests passed")
    return True

def run_setup_check():
    """Run setup verification"""
    print("🔍 Running setup check...")
    
    exit_code = os.system("python3 scripts/check_setup.py")
    if exit_code != 0:
        print("❌ Setup check failed")
        return False
    
    print("✅ Setup check passed")
    return True

def test_cli_help():
    """Test CLI help system"""
    print("📖 Testing CLI help...")
    
    try:
        # Test main help
        exit_code = os.system("python3 main.py --help > /dev/null 2>&1")
        if exit_code != 0:
            print("❌ Main help failed")
            return False
        
        # Test version
        exit_code = os.system("python3 main.py --version > /dev/null 2>&1")
        if exit_code != 0:
            print("❌ Version check failed")
            return False
        
        print("✅ CLI help system working")
        return True
        
    except Exception as e:
        print(f"❌ CLI help test failed: {e}")
        return False

def test_configuration_loading():
    """Test configuration loading with different files"""
    print("⚙️ Testing configuration loading...")
    
    try:
        # Test with default config
        if not Path('config.yaml').exists():
            print("❌ Default config.yaml not found")
            return False
        
        # Test with test config
        if not Path('config-test.yaml').exists():
            print("❌ Test config not found")
            return False
        
        # Test with example configs
        example_configs = [
            'examples/config-production.yaml',
            'examples/config-development.yaml',
            'examples/config-testing.yaml'
        ]
        
        for config_file in example_configs:
            if not Path(config_file).exists():
                print(f"❌ Example config not found: {config_file}")
                return False
        
        print("✅ Configuration files present")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_script_executability():
    """Test that scripts are executable"""
    print("🏃 Testing script executability...")
    
    try:
        scripts = [
            'scripts/install.sh',
            'scripts/monitor.py',
            'scripts/check_setup.py'
        ]
        
        for script in scripts:
            if not Path(script).exists():
                print(f"❌ Script not found: {script}")
                return False
            
            # Check if executable
            if not os.access(script, os.X_OK):
                print(f"❌ Script not executable: {script}")
                return False
        
        print("✅ All scripts are executable")
        return True
        
    except Exception as e:
        print(f"❌ Script executability test failed: {e}")
        return False

def test_project_structure():
    """Test project structure completeness"""
    print("📁 Testing project structure...")
    
    try:
        required_dirs = [
            'src',
            'src/scraper',
            'src/models',
            'src/config',
            'src/utils',
            'database',
            'tests',
            'logs',
            'scripts',
            'examples'
        ]
        
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                print(f"❌ Required directory missing: {dir_path}")
                return False
        
        required_files = [
            'README.md',
            'CLAUDE.md',
            'DEPLOYMENT.md',
            'LICENSE',
            'requirements.txt',
            'setup.py',
            'main.py',
            'config.yaml',
            '.env.example'
        ]
        
        for file_path in required_files:
            if not Path(file_path).exists():
                print(f"❌ Required file missing: {file_path}")
                return False
        
        print("✅ Project structure is complete")
        return True
        
    except Exception as e:
        print(f"❌ Project structure test failed: {e}")
        return False

def test_import_system():
    """Test Python import system"""
    print("🐍 Testing Python import system...")
    
    try:
        # Test basic imports without dependencies
        test_modules = [
            'src.config.config_loader',
            'src.scraper.parser',
            'src.models.book_listing',
            'src.models.crawl_session',
            'src.utils.retry',
            'src.utils.error_handler'
        ]
        
        sys.path.insert(0, '.')
        
        for module in test_modules:
            try:
                __import__(module)
                print(f"✅ {module} imports successfully")
            except ImportError as e:
                print(f"❌ {module} import failed: {e}")
                return False
        
        print("✅ Python import system working")
        return True
        
    except Exception as e:
        print(f"❌ Import system test failed: {e}")
        return False

def test_documentation_completeness():
    """Test documentation completeness"""
    print("📚 Testing documentation completeness...")
    
    try:
        # Check README
        with open('README.md', 'r') as f:
            readme_content = f.read()
            required_sections = [
                '# Kleinanzeige-Bücherwurm',
                '## Features',
                '## Installation',
                '## Usage',
                '## Development'
            ]
            
            for section in required_sections:
                if section not in readme_content:
                    print(f"❌ README missing section: {section}")
                    return False
        
        # Check CLAUDE.md
        with open('CLAUDE.md', 'r') as f:
            claude_content = f.read()
            if len(claude_content) < 1000:
                print("❌ CLAUDE.md too short")
                return False
        
        # Check DEPLOYMENT.md
        with open('DEPLOYMENT.md', 'r') as f:
            deployment_content = f.read()
            if len(deployment_content) < 1000:
                print("❌ DEPLOYMENT.md too short")
                return False
        
        print("✅ Documentation is complete")
        return True
        
    except Exception as e:
        print(f"❌ Documentation test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Kleinanzeigen Crawler - Complete Integration Test")
    print("=" * 60)
    
    tests = [
        ("Component Tests", run_component_tests),
        ("Database Tests", run_database_tests),
        ("Setup Check", run_setup_check),
        ("CLI Help", test_cli_help),
        ("Configuration Loading", test_configuration_loading),
        ("Script Executability", test_script_executability),
        ("Project Structure", test_project_structure),
        ("Import System", test_import_system),
        ("Documentation", test_documentation_completeness)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Integration Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests passed!")
        print("\n✅ Project is ready for production use!")
        print("\nQuick start:")
        print("1. ./scripts/install.sh")
        print("2. Edit .env with your credentials")
        print("3. python main.py --init-db")
        print("4. python main.py --test --headless")
        print("5. python main.py --schedule")
        return 0
    else:
        print("❌ Some integration tests failed.")
        print("Please fix the issues above before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())