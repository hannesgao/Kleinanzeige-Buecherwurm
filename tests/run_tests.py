#!/usr/bin/env python3
"""
Test runner for Kleinanzeigen Crawler
This script provides an easy way to run different types of tests
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

def run_unit_tests(verbose=False):
    """Run unit tests"""
    print("🧪 Running unit tests...")
    cmd = ["python", "-m", "pytest", "tests/unit/", "-v" if verbose else "-q"]
    return subprocess.run(cmd).returncode == 0

def run_integration_tests(verbose=False):
    """Run integration tests"""
    print("🔗 Running integration tests...")
    cmd = ["python", "-m", "pytest", "tests/integration/", "-v" if verbose else "-q"]
    return subprocess.run(cmd).returncode == 0

def run_functional_tests(verbose=False):
    """Run functional tests"""
    print("⚙️ Running functional tests...")
    cmd = ["python", "-m", "pytest", "tests/functional/", "-v" if verbose else "-q"]
    return subprocess.run(cmd).returncode == 0

def run_all_tests(verbose=False):
    """Run all tests"""
    print("🚀 Running all tests...")
    cmd = ["python", "-m", "pytest", "tests/", "-v" if verbose else "-q"]
    return subprocess.run(cmd).returncode == 0

def run_quick_tests(verbose=False):
    """Run quick tests (excluding slow ones)"""
    print("⚡ Running quick tests...")
    cmd = ["python", "-m", "pytest", "tests/", "-m", "not slow", "-v" if verbose else "-q"]
    return subprocess.run(cmd).returncode == 0

def run_production_tests(verbose=False):
    """Run production-ready tests"""
    print("🏭 Running production tests...")
    
    # Set environment variables for production testing
    env = os.environ.copy()
    env['SKIP_SELENIUM_TESTS'] = 'false'
    env['SKIP_NETWORK_TESTS'] = 'true'  # Skip network tests in production
    env['SKIP_DATABASE_TESTS'] = 'true'  # Skip database tests in production
    
    cmd = ["python", "-m", "pytest", "tests/functional/", "-v" if verbose else "-q"]
    return subprocess.run(cmd, env=env).returncode == 0

def run_coverage_tests(verbose=False):
    """Run tests with coverage reporting"""
    print("📊 Running tests with coverage...")
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "--cov=src",
        "--cov-report=html",
        "--cov-report=term",
        "-v" if verbose else "-q"
    ]
    return subprocess.run(cmd).returncode == 0

def run_specific_test(test_path, verbose=False):
    """Run a specific test file or function"""
    print(f"🎯 Running specific test: {test_path}")
    cmd = ["python", "-m", "pytest", test_path, "-v" if verbose else "-q"]
    return subprocess.run(cmd).returncode == 0

def check_test_requirements():
    """Check if test requirements are met"""
    print("🔍 Checking test requirements...")
    
    required_packages = [
        'pytest',
        'pytest-cov',
        'pytest-mock'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is available")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Install missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All test requirements are met")
    return True

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(
        description='Test runner for Kleinanzeigen Crawler',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tests/run_tests.py --unit              # Run unit tests
  python tests/run_tests.py --integration       # Run integration tests  
  python tests/run_tests.py --functional        # Run functional tests
  python tests/run_tests.py --all               # Run all tests
  python tests/run_tests.py --quick             # Run quick tests
  python tests/run_tests.py --production        # Run production tests
  python tests/run_tests.py --coverage          # Run with coverage
  python tests/run_tests.py --test tests/unit/test_parser.py  # Run specific test
        """
    )
    
    parser.add_argument('--unit', action='store_true', help='Run unit tests')
    parser.add_argument('--integration', action='store_true', help='Run integration tests')
    parser.add_argument('--functional', action='store_true', help='Run functional tests')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    parser.add_argument('--quick', action='store_true', help='Run quick tests (no slow tests)')
    parser.add_argument('--production', action='store_true', help='Run production tests')
    parser.add_argument('--coverage', action='store_true', help='Run tests with coverage')
    parser.add_argument('--test', help='Run specific test file or function')
    parser.add_argument('--check', action='store_true', help='Check test requirements')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Check requirements first
    if args.check:
        return 0 if check_test_requirements() else 1
    
    # If no specific test type is specified, run quick tests
    if not any([args.unit, args.integration, args.functional, args.all, 
               args.quick, args.production, args.coverage, args.test]):
        args.quick = True
    
    success = True
    
    if args.unit:
        success &= run_unit_tests(args.verbose)
    
    if args.integration:
        success &= run_integration_tests(args.verbose)
    
    if args.functional:
        success &= run_functional_tests(args.verbose)
    
    if args.all:
        success &= run_all_tests(args.verbose)
    
    if args.quick:
        success &= run_quick_tests(args.verbose)
    
    if args.production:
        success &= run_production_tests(args.verbose)
    
    if args.coverage:
        success &= run_coverage_tests(args.verbose)
    
    if args.test:
        success &= run_specific_test(args.test, args.verbose)
    
    if success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())