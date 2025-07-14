#!/usr/bin/env python3
"""
Component test script for Kleinanzeigen Crawler
This script tests individual components without requiring full dependencies
"""

import sys
import os
import yaml
import traceback
from pathlib import Path

def test_config_loading():
    """Test configuration loading functionality"""
    print("🔧 Testing configuration loading...")
    
    try:
        # Test basic YAML loading
        with open('config-test.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        print("✓ YAML loading successful")
        
        # Test nested access
        assert config['search']['location'] == 'Karlsruhe'
        assert config['search']['radius_km'] == 20
        assert len(config['search']['keywords']) == 3
        
        print("✓ Configuration structure validation passed")
        
        # Test environment variable placeholder
        db_config = config['database']
        assert 'host' in db_config
        assert 'name' in db_config
        
        print("✓ Database configuration present")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        traceback.print_exc()
        return False

def test_file_structure():
    """Test project file structure"""
    print("\n📁 Testing project file structure...")
    
    required_files = [
        'main.py',
        'config.yaml',
        'requirements.txt',
        'setup.py',
        '.env.example',
        'src/__init__.py',
        'src/scraper/__init__.py',
        'src/scraper/crawler.py',
        'src/scraper/parser.py',
        'src/models/__init__.py',
        'src/models/book_listing.py',
        'src/models/crawl_session.py',
        'src/config/__init__.py',
        'src/config/config_loader.py',
        'src/config/database.py',
        'src/utils/__init__.py',
        'src/utils/logger.py',
        'src/utils/scheduler.py',
        'src/utils/notifications.py',
        'src/utils/retry.py',
        'src/utils/error_handler.py',
        'database/schema.sql',
        'tests/__init__.py',
        'tests/test_parser.py',
        'tests/test_config.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    else:
        print("✓ All required files present")
        return True

def test_syntax_validation():
    """Test Python syntax validation"""
    print("\n🐍 Testing Python syntax validation...")
    
    python_files = [
        'main.py',
        'setup.py',
        'src/scraper/crawler.py',
        'src/scraper/parser.py',
        'src/models/book_listing.py',
        'src/models/crawl_session.py',
        'src/config/config_loader.py',
        'src/config/database.py',
        'src/utils/logger.py',
        'src/utils/scheduler.py',
        'src/utils/notifications.py',
        'src/utils/retry.py',
        'src/utils/error_handler.py'
    ]
    
    syntax_errors = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), file_path, 'exec')
            print(f"✓ {file_path} - syntax OK")
        except SyntaxError as e:
            syntax_errors.append(f"{file_path}: {e}")
            print(f"✗ {file_path} - syntax error: {e}")
        except Exception as e:
            print(f"⚠ {file_path} - could not read: {e}")
    
    if syntax_errors:
        print(f"\n✗ Syntax errors found: {len(syntax_errors)}")
        return False
    else:
        print("\n✓ All Python files have valid syntax")
        return True

def test_requirements():
    """Test requirements.txt structure"""
    print("\n📦 Testing requirements.txt...")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        required_packages = [
            'selenium',
            'beautifulsoup4',
            'sqlalchemy',
            'loguru',
            'pyyaml',
            'python-dotenv',
            'requests',
            'pandas',
            'schedule',
            'APScheduler',
            'pytest'
        ]
        
        found_packages = []
        for req in requirements:
            if req.strip() and not req.startswith('#'):
                package_name = req.split('==')[0].split('>=')[0].split('<=')[0]
                found_packages.append(package_name)
        
        missing = []
        for pkg in required_packages:
            if pkg not in found_packages:
                missing.append(pkg)
        
        if missing:
            print(f"✗ Missing packages in requirements.txt: {missing}")
            return False
        else:
            print("✓ All required packages found in requirements.txt")
            return True
            
    except Exception as e:
        print(f"✗ Error reading requirements.txt: {e}")
        return False

def test_database_schema():
    """Test database schema file"""
    print("\n🗄️ Testing database schema...")
    
    try:
        with open('database/schema.sql', 'r') as f:
            schema = f.read()
        
        # Check for required tables
        required_tables = ['crawl_sessions', 'book_listings']
        required_indexes = ['idx_listing_id', 'idx_is_active']
        
        missing_tables = []
        for table in required_tables:
            if f'CREATE TABLE IF NOT EXISTS {table}' not in schema:
                missing_tables.append(table)
        
        missing_indexes = []
        for index in required_indexes:
            if f'CREATE INDEX {index}' not in schema:
                missing_indexes.append(index)
        
        if missing_tables:
            print(f"✗ Missing tables in schema: {missing_tables}")
            return False
        
        if missing_indexes:
            print(f"⚠ Missing indexes in schema: {missing_indexes}")
        
        print("✓ Database schema structure looks good")
        return True
        
    except Exception as e:
        print(f"✗ Error reading database schema: {e}")
        return False

def test_environment_template():
    """Test .env.example file"""
    print("\n🔐 Testing environment template...")
    
    try:
        with open('.env.example', 'r') as f:
            env_template = f.read()
        
        required_vars = [
            'DB_HOST',
            'DB_NAME', 
            'DB_USER',
            'DB_PASSWORD',
            'SMTP_SERVER',
            'EMAIL_SENDER',
            'EMAIL_PASSWORD',
            'EMAIL_RECIPIENT'
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in env_template:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"✗ Missing environment variables: {missing_vars}")
            return False
        else:
            print("✓ All required environment variables present")
            return True
            
    except Exception as e:
        print(f"✗ Error reading .env.example: {e}")
        return False

def main():
    """Run all component tests"""
    print("🚀 Kleinanzeigen Crawler - Component Testing")
    print("=" * 50)
    
    tests = [
        test_config_loading,
        test_file_structure,
        test_syntax_validation,
        test_requirements,
        test_database_schema,
        test_environment_template
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All component tests passed!")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())