#!/usr/bin/env python3
"""
Pytest configuration and fixtures for Kleinanzeigen Crawler tests
"""

import pytest
import os
import sys
import tempfile
import yaml
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def sample_config():
    """Provide sample configuration for tests"""
    return {
        'search': {
            'category': 'antike-buecher',
            'location': 'Karlsruhe',
            'radius_km': 20,
            'max_price': 0,
            'keywords': ['sammlung', 'konvolut', 'nachlass']
        },
        'selenium': {
            'browser': 'chrome',
            'headless': True,
            'window_size': '1920,1080',
            'page_load_timeout': 30,
            'implicit_wait': 10
        },
        'crawler': {
            'max_pages': 5,
            'delay_between_requests': 3,
            'retry_attempts': 3,
            'retry_delay': 5
        },
        'database': {
            'type': 'postgresql',
            'host': 'localhost',
            'port': 5432,
            'name': 'test_crawler',
            'user': 'test_user',
            'password': 'test_password'
        },
        'logging': {
            'level': 'DEBUG',
            'format': '{time} | {level} | {message}',
            'rotation': '10 MB',
            'retention': '3 days'
        },
        'notifications': {
            'enabled': False,
            'email': {
                'smtp_server': 'smtp.test.com',
                'smtp_port': 587,
                'sender': 'test@test.com',
                'password': 'test_password',
                'recipients': ['recipient@test.com']
            }
        },
        'schedule': {
            'enabled': False,
            'cron': '0 */6 * * *'
        }
    }

@pytest.fixture
def temp_config_file(sample_config):
    """Create a temporary config file for tests"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(sample_config, f)
        config_path = f.name
    
    yield config_path
    
    # Cleanup
    os.unlink(config_path)

@pytest.fixture
def sample_listing_data():
    """Provide sample listing data for tests"""
    from datetime import datetime
    
    return {
        'listing_id': 'test_123456',
        'title': 'Antike Bücher Sammlung',
        'description': 'Eine wundervolle Sammlung antiker Bücher aus dem 19. Jahrhundert',
        'price': 0.0,
        'location': '76133 Karlsruhe',
        'postal_code': '76133',
        'distance_km': 5.2,
        'seller_name': 'Test Verkäufer',
        'seller_type': 'private',
        'seller_id': 'seller_123',
        'category': 'Antike Bücher',
        'subcategory': 'Sammlung',
        'condition': 'Gut',
        'listing_date': datetime(2023, 12, 1, 10, 30),
        'view_count': 42,
        'listing_url': 'https://www.kleinanzeigen.de/s-anzeige/test-book/123456',
        'thumbnail_url': 'https://img.kleinanzeigen.de/test/thumb.jpg',
        'image_urls': [
            'https://img.kleinanzeigen.de/test/image1.jpg',
            'https://img.kleinanzeigen.de/test/image2.jpg'
        ],
        'phone_number': None,
        'contact_name': 'Test Kontakt'
    }

@pytest.fixture
def sample_html_listing():
    """Provide sample HTML for listing tests"""
    return """
    <html>
    <head>
        <title>Antike Bücher Sammlung - Kleinanzeigen</title>
        <meta name="ad-id" content="test_123456">
    </head>
    <body>
        <h1 id="viewad-title">Antike Bücher Sammlung</h1>
        <p id="viewad-description-text">Eine wundervolle Sammlung antiker Bücher aus dem 19. Jahrhundert</p>
        <h2 id="viewad-price">Zu verschenken</h2>
        <span id="viewad-locality">76133 Karlsruhe</span>
        <span class="userprofile-name">Test Verkäufer</span>
        <span id="viewad-extra-info">Eingestellt am: Heute</span>
        <div id="viewad-image">
            <img src="https://img.kleinanzeigen.de/test/image1.jpg" alt="Buch">
        </div>
        <div class="breadcrump-link">Bücher</div>
        <div class="breadcrump-link">Antike Bücher</div>
        <span>42 mal aufgerufen</span>
    </body>
    </html>
    """

@pytest.fixture
def sample_search_results_html():
    """Provide sample HTML for search results tests"""
    return """
    <html>
    <body>
        <article class="aditem">
            <a href="/s-anzeige/antike-buecher-sammlung/123456">
                <h2 class="text-module-begin">Antike Bücher Sammlung</h2>
            </a>
            <p class="aditem-main--middle--price">Zu verschenken</p>
            <div class="aditem-main--top--left">76133 Karlsruhe</div>
            <div class="aditem-main--top--right">Heute</div>
            <img src="https://img.kleinanzeigen.de/test/thumb.jpg" alt="Buch">
        </article>
        <article class="aditem">
            <a href="/s-anzeige/buchkonvolut/789012">
                <h2 class="text-module-begin">Buchkonvolut zu verschenken</h2>
            </a>
            <p class="aditem-main--middle--price">Zu verschenken</p>
            <div class="aditem-main--top--left">76131 Karlsruhe</div>
            <div class="aditem-main--top--right">Gestern</div>
            <img src="https://img.kleinanzeigen.de/test/thumb2.jpg" alt="Bücher">
        </article>
    </body>
    </html>
    """

@pytest.fixture
def mock_selenium_driver():
    """Provide a mock Selenium driver for tests"""
    from unittest.mock import MagicMock
    
    driver = MagicMock()
    driver.get.return_value = None
    driver.quit.return_value = None
    driver.find_element.return_value = MagicMock()
    driver.find_elements.return_value = [MagicMock()]
    driver.current_url = "https://www.kleinanzeigen.de/test"
    driver.page_source = "<html><body>Test</body></html>"
    
    return driver

@pytest.fixture
def mock_database_session():
    """Provide a mock database session for tests"""
    from unittest.mock import MagicMock
    
    session = MagicMock()
    session.add.return_value = None
    session.commit.return_value = None
    session.rollback.return_value = None
    session.close.return_value = None
    session.query.return_value = MagicMock()
    
    return session

# Test markers
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "network: mark test as requiring network access"
    )
    config.addinivalue_line(
        "markers", "selenium: mark test as requiring Selenium"
    )
    config.addinivalue_line(
        "markers", "database: mark test as requiring database"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "functional: mark test as functional test"
    )

# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on path"""
    for item in items:
        # Add markers based on test path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "functional" in str(item.fspath):
            item.add_marker(pytest.mark.functional)
        
        # Add markers based on test name
        if "selenium" in item.name.lower():
            item.add_marker(pytest.mark.selenium)
        if "database" in item.name.lower():
            item.add_marker(pytest.mark.database)
        if "network" in item.name.lower():
            item.add_marker(pytest.mark.network)

# Skip conditions
def pytest_runtest_setup(item):
    """Setup function to skip tests based on environment"""
    # Skip selenium tests if explicitly disabled
    if "selenium" in [mark.name for mark in item.iter_markers()]:
        if os.getenv('SKIP_SELENIUM_TESTS', '').lower() == 'true':
            pytest.skip("Selenium tests skipped")
    
    # Skip network tests if explicitly disabled
    if "network" in [mark.name for mark in item.iter_markers()]:
        if os.getenv('SKIP_NETWORK_TESTS', '').lower() == 'true':
            pytest.skip("Network tests skipped")
    
    # Skip database tests if explicitly disabled
    if "database" in [mark.name for mark in item.iter_markers()]:
        if os.getenv('SKIP_DATABASE_TESTS', '').lower() == 'true':
            pytest.skip("Database tests skipped")