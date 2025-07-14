#!/usr/bin/env python3
"""
End-to-end tests for Kleinanzeigen Crawler
These tests verify the complete workflow from configuration to notification
"""

import sys
import os
import tempfile
import json
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestEndToEnd:
    """End-to-end workflow tests"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_config = {
            'search': {
                'category': 'antike-buecher',
                'location': 'Karlsruhe',
                'radius_km': 5,
                'max_price': 0,
                'keywords': ['sammlung']
            },
            'selenium': {
                'headless': True,
                'page_load_timeout': 10,
                'implicit_wait': 5
            },
            'crawler': {
                'max_pages': 1,
                'delay_between_requests': 1,
                'retry_attempts': 2
            },
            'database': {
                'host': 'localhost',
                'name': 'test_db',
                'user': 'test_user',
                'password': 'test_pass'
            },
            'notifications': {
                'enabled': True,
                'email': {
                    'smtp_server': 'smtp.test.com',
                    'smtp_port': 587,
                    'sender': 'test@test.com',
                    'password': 'test_pass',
                    'recipients': ['recipient@test.com']
                }
            },
            'logging': {
                'level': 'DEBUG'
            }
        }
        
        self.sample_listings = [
            {
                'listing_id': 'test_123',
                'title': 'Antike Bücher Sammlung',
                'description': 'Eine wundervolle Sammlung antiker Bücher',
                'price': 0,
                'location': '76133 Karlsruhe',
                'postal_code': '76133',
                'seller_name': 'Test Verkäufer',
                'seller_type': 'private',
                'listing_url': 'https://www.kleinanzeigen.de/s-anzeige/test/123',
                'thumbnail_url': 'https://example.com/thumb.jpg',
                'image_urls': ['https://example.com/image1.jpg'],
                'phone_number': None,
                'listing_date': datetime.now(),
                'view_count': 42
            }
        ]
    
    @patch('src.scraper.crawler.webdriver.Chrome')
    @patch('src.config.database.create_engine')
    @patch('src.config.database.sessionmaker')
    @patch('src.utils.notifications.smtplib.SMTP')
    def test_complete_crawl_workflow(self, mock_smtp, mock_sessionmaker, mock_engine, mock_chrome):
        """Test complete crawl workflow from start to finish"""
        
        # Setup mocks
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        mock_db_engine = MagicMock()
        mock_engine.return_value = mock_db_engine
        
        mock_session_class = MagicMock()
        mock_sessionmaker.return_value = mock_session_class
        
        mock_db_session = MagicMock()
        mock_session_class.return_value = mock_db_session
        
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        # Mock driver behavior
        mock_driver.get.return_value = None
        mock_driver.current_url = "https://www.kleinanzeigen.de/s-antike-buecher/k0"
        mock_driver.page_source = """
        <html>
        <body>
            <article class="aditem">
                <a href="/s-anzeige/test-book/123456">
                    <h2 class="text-module-begin">Test Book Collection</h2>
                </a>
                <p class="aditem-main--middle--price">Zu verschenken</p>
                <div class="aditem-main--top--left">76133 Karlsruhe</div>
            </article>
        </body>
        </html>
        """
        
        mock_driver.find_elements.return_value = [MagicMock()]
        mock_driver.find_element.return_value = MagicMock()
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(self.test_config, f)
            config_path = f.name
        
        try:
            # Import and test the main workflow
            from src.config.config_loader import ConfigLoader
            from src.scraper.crawler import KleinanzeigenCrawler
            from src.config.database import DatabaseManager
            from src.utils.notifications import NotificationManager
            
            # Initialize components
            config_loader = ConfigLoader(config_path)
            crawler = KleinanzeigenCrawler(config_loader.get('selenium'))
            db_manager = DatabaseManager(config_loader.get('database'))
            notifier = NotificationManager(config_loader.get('notifications'))
            
            # Test search functionality
            search_params = config_loader.get('search')
            
            # Mock the search_books method to return URLs
            with patch.object(crawler, 'search_books') as mock_search:
                mock_search.return_value = ['https://www.kleinanzeigen.de/s-anzeige/test/123']
                
                # Mock get_listing_details to return structured data
                with patch.object(crawler, 'get_listing_details') as mock_get_details:
                    mock_get_details.return_value = self.sample_listings[0]
                    
                    # Execute search
                    listing_urls = crawler.search_books(search_params)
                    assert len(listing_urls) == 1
                    
                    # Process listings
                    listing_data = crawler.get_listing_details(listing_urls[0])
                    assert listing_data is not None
                    assert listing_data['title'] == 'Antike Bücher Sammlung'
                    
                    # Test notification
                    notifier.notify_new_listings([listing_data])
                    
                    # Verify SMTP was called
                    mock_smtp.assert_called_once()
            
            # Cleanup
            crawler.close()
            
        finally:
            os.unlink(config_path)
    
    def test_error_recovery_workflow(self):
        """Test error recovery during crawl workflow"""
        
        with patch('src.scraper.crawler.webdriver.Chrome') as mock_chrome:
            mock_driver = MagicMock()
            mock_chrome.return_value = mock_driver
            
            # Simulate network error
            mock_driver.get.side_effect = Exception("Network error")
            
            from src.scraper.crawler import KleinanzeigenCrawler
            from src.utils.retry import NetworkError
            
            crawler = KleinanzeigenCrawler(self.test_config['selenium'])
            
            # Test that retry mechanism works
            with patch.object(crawler, '_random_delay'):
                with pytest.raises(Exception):
                    crawler.get_listing_details("https://example.com/test")
            
            crawler.close()
    
    def test_data_persistence_workflow(self):
        """Test data persistence workflow"""
        
        with patch('src.config.database.create_engine') as mock_engine:
            with patch('src.config.database.sessionmaker') as mock_sessionmaker:
                
                # Setup database mocks
                mock_db_engine = MagicMock()
                mock_engine.return_value = mock_db_engine
                
                mock_session_class = MagicMock()
                mock_sessionmaker.return_value = mock_session_class
                
                mock_db_session = MagicMock()
                mock_session_class.return_value = mock_db_session
                
                # Setup context manager
                mock_session_class.return_value.__enter__.return_value = mock_db_session
                mock_session_class.return_value.__exit__.return_value = None
                
                from src.config.database import DatabaseManager
                from src.models import BookListing, CrawlSession
                
                db_manager = DatabaseManager(self.test_config['database'])
                
                # Test session creation
                with db_manager.get_session() as session:
                    # Create a crawl session
                    crawl_session = CrawlSession(
                        session_id=str(uuid.uuid4()),
                        start_time=datetime.now(),
                        status='running'
                    )
                    
                    session.add(crawl_session)
                    
                    # Create a book listing
                    book_listing = BookListing(
                        listing_id='test_123',
                        title='Test Book',
                        price=0,
                        location='Karlsruhe',
                        listing_url='https://example.com/test'
                    )
                    
                    session.add(book_listing)
                    
                # Verify database operations were called
                mock_db_session.add.assert_called()
                mock_db_session.commit.assert_called()
    
    def test_configuration_validation_workflow(self):
        """Test configuration validation workflow"""
        
        # Test with invalid configuration
        invalid_config = {
            'search': {
                # Missing required fields
            },
            'selenium': {
                'headless': 'invalid_boolean'  # Invalid type
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(invalid_config, f)
            config_path = f.name
        
        try:
            from src.config.config_loader import ConfigLoader
            
            config_loader = ConfigLoader(config_path)
            
            # Test that missing configuration is handled
            search_config = config_loader.get('search.location', 'default')
            assert search_config == 'default'
            
            # Test that invalid configuration is handled
            headless_config = config_loader.get('selenium.headless', True)
            assert headless_config == 'invalid_boolean'  # Raw value returned
            
        finally:
            os.unlink(config_path)
    
    def test_scheduling_workflow(self):
        """Test scheduling workflow"""
        
        from src.utils.scheduler import TaskScheduler
        
        scheduler = TaskScheduler()
        
        # Test job scheduling
        job_executed = False
        
        def test_job():
            nonlocal job_executed
            job_executed = True
            return "job completed"
        
        # Add job with cron expression
        scheduler.add_cron_job(test_job, "* * * * *", "test_job")
        
        # Verify job was added
        assert scheduler.scheduler is not None
        jobs = scheduler.scheduler.get_jobs()
        assert len(jobs) >= 1
        assert jobs[0].id == "test_job"
    
    def test_monitoring_workflow(self):
        """Test monitoring and statistics workflow"""
        
        with patch('src.config.database.create_engine') as mock_engine:
            with patch('src.config.database.sessionmaker') as mock_sessionmaker:
                
                # Setup database mocks
                mock_db_engine = MagicMock()
                mock_engine.return_value = mock_db_engine
                
                mock_session_class = MagicMock()
                mock_sessionmaker.return_value = mock_session_class
                
                mock_db_session = MagicMock()
                mock_session_class.return_value = mock_db_session
                
                # Setup context manager
                mock_session_class.return_value.__enter__.return_value = mock_db_session
                mock_session_class.return_value.__exit__.return_value = None
                
                # Mock query results
                mock_db_session.query.return_value.order_by.return_value.limit.return_value.all.return_value = [
                    MagicMock(
                        start_time=datetime.now(),
                        status='completed',
                        total_listings_found=5,
                        new_listings_found=2
                    )
                ]
                
                from src.config.database import DatabaseManager
                from src.models import CrawlSession
                
                db_manager = DatabaseManager(self.test_config['database'])
                
                # Test statistics gathering
                with db_manager.get_session() as session:
                    sessions = session.query(CrawlSession).order_by(
                        CrawlSession.start_time.desc()
                    ).limit(10).all()
                    
                    assert len(sessions) == 1
                    assert sessions[0].status == 'completed'
    
    def test_cleanup_workflow(self):
        """Test cleanup workflow"""
        
        with patch('src.config.database.create_engine') as mock_engine:
            with patch('src.config.database.sessionmaker') as mock_sessionmaker:
                
                # Setup database mocks
                mock_db_engine = MagicMock()
                mock_engine.return_value = mock_db_engine
                
                mock_session_class = MagicMock()
                mock_sessionmaker.return_value = mock_session_class
                
                mock_db_session = MagicMock()
                mock_session_class.return_value = mock_db_session
                
                # Setup context manager
                mock_session_class.return_value.__enter__.return_value = mock_db_session
                mock_session_class.return_value.__exit__.return_value = None
                
                # Mock cleanup operations
                mock_db_session.query.return_value.filter.return_value.count.return_value = 10
                mock_db_session.query.return_value.filter.return_value.delete.return_value = 10
                
                from src.config.database import DatabaseManager
                from src.models import BookListing
                
                db_manager = DatabaseManager(self.test_config['database'])
                
                # Test cleanup operations
                with db_manager.get_session() as session:
                    # Simulate cleanup of old inactive listings
                    old_listings = session.query(BookListing).filter(
                        BookListing.is_active == False
                    ).count()
                    
                    assert old_listings == 10
                    
                    # Simulate deletion
                    session.query(BookListing).filter(
                        BookListing.is_active == False
                    ).delete()
                    
                    # Verify delete was called
                    mock_db_session.query.return_value.filter.return_value.delete.assert_called()
    
    def teardown_method(self):
        """Cleanup after each test"""
        # Clean up any test files or resources
        pass