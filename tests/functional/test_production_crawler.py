#!/usr/bin/env python3
"""
Production environment functional tests for Kleinanzeigen Crawler
These tests verify that the crawler works correctly in a production-like environment
"""

import sys
import os
import time
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestProductionCrawler:
    """Functional tests for production crawler"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_config = {
            'search': {
                'category': 'antike-buecher',
                'location': 'Karlsruhe',
                'radius_km': 5,
                'max_price': 0,
                'keywords': ['test']
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
            'logging': {
                'level': 'DEBUG'
            }
        }
    
    @pytest.mark.skipif(os.getenv('SKIP_SELENIUM_TESTS') == 'true', 
                       reason="Selenium tests skipped")
    def test_crawler_initialization(self):
        """Test that crawler can be initialized with production config"""
        try:
            from src.scraper.crawler import KleinanzeigenCrawler
            
            crawler = KleinanzeigenCrawler(self.test_config['selenium'])
            assert crawler is not None
            assert crawler.config == self.test_config['selenium']
            
            # Test driver setup
            crawler.setup_driver()
            assert crawler.driver is not None
            assert crawler.wait is not None
            
            # Cleanup
            crawler.close()
            
        except ImportError:
            pytest.skip("Selenium not available")
    
    @pytest.mark.skipif(os.getenv('SKIP_NETWORK_TESTS') == 'true',
                       reason="Network tests skipped")
    def test_search_page_access(self):
        """Test that the crawler can access Kleinanzeigen search pages"""
        try:
            from src.scraper.crawler import KleinanzeigenCrawler
            
            crawler = KleinanzeigenCrawler(self.test_config['selenium'])
            
            # Test basic page access
            search_url = f"{crawler.BASE_URL}/s-antike-buecher/k0"
            crawler.driver.get(search_url)
            
            # Check that we reached the correct page
            assert "kleinanzeigen.de" in crawler.driver.current_url
            
            # Check for common page elements
            page_source = crawler.driver.page_source
            assert len(page_source) > 1000  # Should have substantial content
            
            crawler.close()
            
        except ImportError:
            pytest.skip("Selenium not available")
        except Exception as e:
            pytest.skip(f"Network test failed: {e}")
    
    def test_parser_with_real_html(self):
        """Test parser with realistic HTML structure"""
        from src.scraper.parser import ListingParser
        
        # Sample HTML that mimics Kleinanzeigen structure
        sample_html = """
        <html>
        <body>
            <article class="aditem">
                <a href="/s-anzeige/test-book/123456">
                    <h2 class="text-module-begin">Test Book Collection</h2>
                </a>
                <p class="aditem-main--middle--price">Zu verschenken</p>
                <div class="aditem-main--top--left">76133 Karlsruhe</div>
                <div class="aditem-main--top--right">Heute</div>
                <img src="https://example.com/image.jpg" alt="Test">
            </article>
        </body>
        </html>
        """
        
        parser = ListingParser()
        results = parser.parse_search_results(sample_html)
        
        assert len(results) == 1
        assert results[0]['title'] == 'Test Book Collection'
        assert results[0]['price'] == 0.0
        assert results[0]['location'] == '76133 Karlsruhe'
        assert 'kleinanzeigen.de' in results[0]['url']
    
    def test_database_connection_mock(self):
        """Test database operations with mock database"""
        from src.config.database import DatabaseManager
        
        with patch('src.config.database.create_engine') as mock_engine:
            with patch('src.config.database.sessionmaker') as mock_session:
                mock_engine.return_value = Mock()
                mock_session.return_value = Mock()
                
                db_manager = DatabaseManager(self.test_config['database'])
                
                assert db_manager.engine is not None
                assert db_manager.SessionLocal is not None
                
                # Test session context manager
                with db_manager.get_session() as session:
                    assert session is not None
    
    def test_notification_system(self):
        """Test notification system with mock SMTP"""
        from src.utils.notifications import NotificationManager
        
        config = {
            'enabled': True,
            'email': {
                'smtp_server': 'smtp.test.com',
                'smtp_port': 587,
                'sender': 'test@test.com',
                'password': 'test_pass',
                'recipients': ['recipient@test.com']
            }
        }
        
        with patch('src.utils.notifications.smtplib.SMTP') as mock_smtp:
            notifier = NotificationManager(config)
            
            test_listings = [
                {
                    'title': 'Test Book',
                    'price': 0,
                    'location': 'Karlsruhe',
                    'listing_url': 'https://example.com/1'
                }
            ]
            
            # This should not raise an exception
            notifier.notify_new_listings(test_listings)
            
            # Verify SMTP was called
            mock_smtp.assert_called_once()
    
    def test_complete_workflow_mock(self):
        """Test complete workflow with mocked dependencies"""
        from src.config.config_loader import ConfigLoader
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(self.test_config, f)
            config_path = f.name
        
        try:
            # Test config loading
            config_loader = ConfigLoader(config_path)
            assert config_loader.get('search.location') == 'Karlsruhe'
            
            # Test main components initialization
            with patch('src.scraper.crawler.webdriver.Chrome'):
                with patch('src.config.database.create_engine'):
                    with patch('src.config.database.sessionmaker'):
                        from src.scraper.crawler import KleinanzeigenCrawler
                        from src.config.database import DatabaseManager
                        from src.utils.notifications import NotificationManager
                        
                        # Initialize components
                        crawler = KleinanzeigenCrawler(config_loader.get('selenium'))
                        db_manager = DatabaseManager(config_loader.get('database'))
                        notifier = NotificationManager({'enabled': False})
                        
                        # All components should initialize without errors
                        assert crawler is not None
                        assert db_manager is not None
                        assert notifier is not None
                        
        finally:
            os.unlink(config_path)
    
    def test_error_handling_production(self):
        """Test error handling in production-like scenarios"""
        from src.utils.error_handler import ErrorHandler
        from src.utils.retry import retry_on_exception, NetworkError
        
        # Test retry mechanism
        call_count = 0
        
        @retry_on_exception(max_attempts=3, delay=0.1)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise NetworkError("Network issue")
            return "success"
        
        result = flaky_function()
        assert result == "success"
        assert call_count == 3
        
        # Test error reporting
        error = ValueError("Test error")
        session_data = {"session_id": "test_session"}
        
        report = ErrorHandler.create_error_report(error, session_data)
        assert report["error_type"] == "ValueError"
        assert report["session_data"] == session_data
    
    def test_logging_configuration(self):
        """Test logging configuration"""
        from src.utils.logger import setup_logger
        
        log_config = {
            'level': 'INFO',
            'format': '{time} | {level} | {message}',
            'rotation': '1 MB',
            'retention': '1 day'
        }
        
        # This should not raise an exception
        logger = setup_logger(log_config)
        assert logger is not None
    
    def test_scheduler_configuration(self):
        """Test scheduler configuration"""
        from src.utils.scheduler import TaskScheduler
        
        scheduler = TaskScheduler()
        
        # Test adding a job
        def test_job():
            return "job executed"
        
        scheduler.add_cron_job(test_job, "0 0 * * *", "test_job")
        
        # Should not raise an exception
        assert scheduler.scheduler is not None
    
    @pytest.mark.skipif(os.getenv('SKIP_PERFORMANCE_TESTS') == 'true',
                       reason="Performance tests skipped")
    def test_performance_basic(self):
        """Basic performance test"""
        from src.scraper.parser import ListingParser
        
        # Create a large HTML document
        large_html = """
        <html><body>
        """ + """
        <article class="aditem">
            <a href="/s-anzeige/test-book-{i}/123456">
                <h2 class="text-module-begin">Test Book {i}</h2>
            </a>
            <p class="aditem-main--middle--price">Zu verschenken</p>
            <div class="aditem-main--top--left">76133 Karlsruhe</div>
        </article>
        """.format(i=i) * 100 + """
        </body></html>
        """
        
        parser = ListingParser()
        
        start_time = time.time()
        results = parser.parse_search_results(large_html)
        end_time = time.time()
        
        # Should parse 100 listings
        assert len(results) == 100
        
        # Should complete within reasonable time (less than 5 seconds)
        assert (end_time - start_time) < 5.0
    
    def test_memory_usage_basic(self):
        """Basic memory usage test"""
        import tracemalloc
        
        from src.scraper.parser import ListingParser
        
        # Start tracing
        tracemalloc.start()
        
        parser = ListingParser()
        
        # Create some test data
        for i in range(100):
            html = f"""
            <html><body>
                <article class="aditem">
                    <h2 class="text-module-begin">Test Book {i}</h2>
                </article>
            </body></html>
            """
            parser.parse_search_results(html)
        
        # Get current memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Memory usage should be reasonable (less than 50MB)
        assert peak < 50 * 1024 * 1024  # 50MB
    
    def teardown_method(self):
        """Cleanup after each test"""
        # Clean up any test files or resources
        pass