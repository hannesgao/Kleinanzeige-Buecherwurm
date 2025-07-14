#!/usr/bin/env python3
"""
Setup verification script for Kleinanzeigen Crawler
This script checks if all requirements are met for running the crawler
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} is supported")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} is not supported")
        print("  Please upgrade to Python 3.8 or higher")
        return False

def check_required_packages():
    """Check if all required packages are installed"""
    print("\n📦 Checking required packages...")
    
    required_packages = [
        'selenium',
        'beautifulsoup4',
        'sqlalchemy',
        'loguru',
        'yaml',
        'dotenv',
        'requests',
        'pandas',
        'schedule',
        'apscheduler',
        'psycopg2',
        'webdriver_manager'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            # Handle package name differences
            import_name = package
            if package == 'yaml':
                import_name = 'yaml'
            elif package == 'dotenv':
                import_name = 'dotenv'
            elif package == 'beautifulsoup4':
                import_name = 'bs4'
            elif package == 'psycopg2':
                import_name = 'psycopg2'
            elif package == 'webdriver_manager':
                import_name = 'webdriver_manager'
            
            importlib.import_module(import_name)
            print(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} is missing")
    
    if missing_packages:
        print(f"\n  Install missing packages with:")
        print(f"  pip3 install {' '.join(missing_packages)}")
        return False
    else:
        print("\n✓ All required packages are installed")
        return True

def check_chrome_browser():
    """Check if Chrome browser is installed"""
    print("\n🌐 Checking Chrome browser...")
    
    chrome_commands = [
        'google-chrome',
        'google-chrome-stable',
        'chromium-browser',
        'chromium'
    ]
    
    for cmd in chrome_commands:
        try:
            result = subprocess.run([cmd, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✓ Chrome browser found: {version}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    print("✗ Chrome browser not found")
    print("  Please install Google Chrome or Chromium browser")
    print("  Ubuntu: sudo apt install google-chrome-stable")
    print("  Or visit: https://www.google.com/chrome/")
    return False

def check_database_connection():
    """Check database connection (if configured)"""
    print("\n🗄️ Checking database configuration...")
    
    # Check if .env file exists
    if not Path('.env').exists():
        print("⚠ .env file not found")
        print("  Copy .env.example to .env and configure database settings")
        return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    db_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = []
    
    for var in db_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"✗ Missing database environment variables: {missing_vars}")
        print("  Please configure these in your .env file")
        return False
    
    print("✓ Database configuration found")
    
    # Test database connection
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        conn.close()
        print("✓ Database connection successful")
        return True
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("  Please check your database configuration and ensure PostgreSQL is running")
        return False

def check_file_permissions():
    """Check file permissions"""
    print("\n🔒 Checking file permissions...")
    
    important_files = [
        'main.py',
        'config.yaml',
        '.env'
    ]
    
    issues = []
    
    for file_path in important_files:
        if Path(file_path).exists():
            stat = Path(file_path).stat()
            mode = stat.st_mode
            
            if file_path == '.env':
                # .env should be readable only by owner
                if mode & 0o077:
                    issues.append(f"{file_path} is readable by others (security risk)")
            else:
                # Other files should be readable
                if not (mode & 0o400):
                    issues.append(f"{file_path} is not readable")
    
    if issues:
        print("⚠ Permission issues found:")
        for issue in issues:
            print(f"  - {issue}")
        print("  Fix with: chmod 600 .env && chmod 644 config.yaml main.py")
        return False
    else:
        print("✓ File permissions are correct")
        return True

def check_disk_space():
    """Check available disk space"""
    print("\n💾 Checking disk space...")
    
    try:
        import shutil
        total, used, free = shutil.disk_usage('.')
        
        # Convert to GB
        free_gb = free / (1024**3)
        total_gb = total / (1024**3)
        
        if free_gb < 1:
            print(f"✗ Low disk space: {free_gb:.1f} GB free of {total_gb:.1f} GB")
            print("  Please free up disk space before running the crawler")
            return False
        else:
            print(f"✓ Disk space: {free_gb:.1f} GB free of {total_gb:.1f} GB")
            return True
            
    except Exception as e:
        print(f"⚠ Could not check disk space: {e}")
        return True

def main():
    """Run all setup checks"""
    print("🚀 Kleinanzeigen Crawler - Setup Check")
    print("=" * 50)
    
    checks = [
        check_python_version,
        check_required_packages,
        check_chrome_browser,
        check_database_connection,
        check_file_permissions,
        check_disk_space
    ]
    
    passed = 0
    failed = 0
    
    for check in checks:
        try:
            if check():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Check {check.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Setup Check Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All setup checks passed! You're ready to run the crawler.")
        print("\nNext steps:")
        print("1. python3 main.py --init-db    # Initialize database")
        print("2. python3 main.py --test       # Test run")
        print("3. python3 main.py --schedule   # Production run")
        return 0
    else:
        print("❌ Setup issues found. Please fix the issues above before running the crawler.")
        return 1

if __name__ == "__main__":
    sys.exit(main())