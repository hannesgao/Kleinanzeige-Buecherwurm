#!/usr/bin/env python3
"""
Database connection test script
This script tests database connectivity and operations
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_database_connection():
    """Test database connection without requiring actual database"""
    print("🗄️ Testing database connection logic...")
    
    try:
        # Test environment variables
        test_env = {
            'DB_HOST': 'localhost',
            'DB_NAME': 'test_db',
            'DB_USER': 'test_user',
            'DB_PASSWORD': 'test_password'
        }
        
        # Temporarily set environment variables
        for key, value in test_env.items():
            os.environ[key] = value
        
        # Test config loading with database settings
        from src.config.config_loader import ConfigLoader
        
        config = ConfigLoader('config-test.yaml')
        db_config = config.get('database', {})
        
        # Validate database configuration
        required_keys = ['host', 'name', 'user', 'password']
        missing_keys = [key for key in required_keys if not db_config.get(key)]
        
        if missing_keys:
            print(f"✗ Missing database configuration keys: {missing_keys}")
            return False
        
        print("✓ Database configuration validation passed")
        
        # Test database manager initialization (without actual connection)
        try:
            from src.config.database import DatabaseManager
            
            # This will fail if PostgreSQL is not installed, but that's expected
            print("✓ DatabaseManager class can be imported")
            
        except ImportError as e:
            print(f"✗ DatabaseManager import failed: {e}")
            return False
        
        # Clean up environment variables
        for key in test_env:
            os.environ.pop(key, None)
        
        return True
        
    except Exception as e:
        print(f"✗ Database connection test failed: {e}")
        return False

def test_model_definitions():
    """Test SQLAlchemy model definitions"""
    print("\n📊 Testing model definitions...")
    
    try:
        from src.models import BookListing, CrawlSession, Base
        
        # Test BookListing model
        print("✓ BookListing model imported successfully")
        
        # Test CrawlSession model
        print("✓ CrawlSession model imported successfully")
        
        # Test Base model
        print("✓ Base model imported successfully")
        
        # Test model attributes
        listing_attrs = [
            'id', 'listing_id', 'title', 'description', 'price',
            'location', 'seller_name', 'listing_url', 'created_at'
        ]
        
        for attr in listing_attrs:
            if not hasattr(BookListing, attr):
                print(f"✗ BookListing missing attribute: {attr}")
                return False
        
        print("✓ BookListing model attributes validated")
        
        session_attrs = [
            'id', 'session_id', 'start_time', 'end_time', 'status',
            'total_listings_found', 'new_listings_found'
        ]
        
        for attr in session_attrs:
            if not hasattr(CrawlSession, attr):
                print(f"✗ CrawlSession missing attribute: {attr}")
                return False
        
        print("✓ CrawlSession model attributes validated")
        
        return True
        
    except Exception as e:
        print(f"✗ Model definition test failed: {e}")
        return False

def test_sql_schema():
    """Test SQL schema file"""
    print("\n📝 Testing SQL schema...")
    
    try:
        with open('database/schema.sql', 'r') as f:
            schema = f.read()
        
        # Test for required tables
        required_tables = [
            'CREATE TABLE IF NOT EXISTS crawl_sessions',
            'CREATE TABLE IF NOT EXISTS book_listings'
        ]
        
        missing_tables = []
        for table_sql in required_tables:
            if table_sql not in schema:
                missing_tables.append(table_sql)
        
        if missing_tables:
            print(f"✗ Missing table definitions: {missing_tables}")
            return False
        
        print("✓ Required tables found in schema")
        
        # Test for indexes
        required_indexes = [
            'CREATE INDEX idx_listing_id',
            'CREATE INDEX idx_is_active'
        ]
        
        missing_indexes = []
        for index_sql in required_indexes:
            if index_sql not in schema:
                missing_indexes.append(index_sql)
        
        if missing_indexes:
            print(f"⚠ Missing indexes (performance may be affected): {missing_indexes}")
        else:
            print("✓ Required indexes found in schema")
        
        # Test for foreign keys
        if 'REFERENCES crawl_sessions(id)' not in schema:
            print("⚠ Foreign key relationship not found")
        else:
            print("✓ Foreign key relationships found")
        
        return True
        
    except Exception as e:
        print(f"✗ SQL schema test failed: {e}")
        return False

def main():
    """Run all database tests"""
    print("🚀 Kleinanzeigen Crawler - Database Testing")
    print("=" * 50)
    
    tests = [
        test_database_connection,
        test_model_definitions,
        test_sql_schema
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
    print(f"📊 Database Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All database tests passed!")
        print("\nNote: Actual database connection requires PostgreSQL and proper credentials")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())