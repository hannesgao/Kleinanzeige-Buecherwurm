import pytest
from unittest.mock import Mock, patch, MagicMock
from src.utils.notifications import NotificationManager

class TestNotificationManager:
    """Test cases for the NotificationManager class"""
    
    def setup_method(self):
        """Setup test configuration"""
        self.config = {
            'enabled': True,
            'email': {
                'smtp_server': 'smtp.test.com',
                'smtp_port': 587,
                'sender': 'test@test.com',
                'password': 'test_password',
                'recipients': ['recipient@test.com']
            }
        }
        self.manager = NotificationManager(self.config)
    
    def test_init_enabled(self):
        """Test initialization with notifications enabled"""
        assert self.manager.enabled is True
        assert self.manager.config == self.config
    
    def test_init_disabled(self):
        """Test initialization with notifications disabled"""
        config = {'enabled': False}
        manager = NotificationManager(config)
        assert manager.enabled is False
    
    @patch('src.utils.notifications.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp_class):
        """Test successful email sending"""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        subject = "Test Subject"
        body = "Test Body"
        recipients = ["test@example.com"]
        
        self.manager.send_email(subject, body, recipients)
        
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with('test@test.com', 'test_password')
        mock_smtp.send_message.assert_called_once()
    
    @patch('src.utils.notifications.smtplib.SMTP')
    @patch('src.utils.notifications.logger')
    def test_send_email_failure(self, mock_logger, mock_smtp_class):
        """Test email sending failure"""
        mock_smtp_class.side_effect = Exception("SMTP error")
        
        subject = "Test Subject"
        body = "Test Body"
        recipients = ["test@example.com"]
        
        self.manager.send_email(subject, body, recipients)
        
        mock_logger.error.assert_called_once()
    
    @patch('src.utils.notifications.logger')
    def test_send_email_disabled(self, mock_logger):
        """Test email sending when notifications are disabled"""
        manager = NotificationManager({'enabled': False})
        
        subject = "Test Subject"
        body = "Test Body"
        recipients = ["test@example.com"]
        
        manager.send_email(subject, body, recipients)
        
        mock_logger.info.assert_called_once_with("Notifications disabled, skipping email")
    
    @patch.object(NotificationManager, 'send_email')
    def test_notify_new_listings(self, mock_send_email):
        """Test notifying about new listings"""
        listings = [
            {
                'title': 'Test Book 1',
                'price': 0,
                'location': 'Test Location',
                'listing_url': 'https://example.com/1'
            },
            {
                'title': 'Test Book 2',
                'price': 0,
                'location': 'Test Location',
                'listing_url': 'https://example.com/2'
            }
        ]
        
        self.manager.notify_new_listings(listings)
        
        mock_send_email.assert_called_once()
        args, kwargs = mock_send_email.call_args
        subject, body, recipients = args
        
        assert "2 Anzeigen" in subject
        assert recipients == ['recipient@test.com']
    
    @patch.object(NotificationManager, 'send_email')
    def test_notify_new_listings_empty(self, mock_send_email):
        """Test notifying with empty listings"""
        self.manager.notify_new_listings([])
        
        mock_send_email.assert_not_called()
    
    def test_create_listing_html(self):
        """Test HTML creation for listings"""
        listings = [
            {
                'title': 'Test Book',
                'description': 'Test Description',
                'price': 0,
                'location': 'Test Location',
                'listing_url': 'https://example.com/1',
                'thumbnail_url': 'https://example.com/thumb.jpg'
            }
        ]
        
        html = self.manager._create_listing_html(listings)
        
        assert 'Test Book' in html
        assert 'Test Description' in html
        assert 'Test Location' in html
        assert 'Zu verschenken' in html
        assert 'https://example.com/1' in html
        assert 'https://example.com/thumb.jpg' in html
        assert 'DOCTYPE html' in html
    
    def test_create_listing_html_no_image(self):
        """Test HTML creation for listings without images"""
        listings = [
            {
                'title': 'Test Book',
                'description': 'Test Description',
                'price': 0,
                'location': 'Test Location',
                'listing_url': 'https://example.com/1',
                'thumbnail_url': None
            }
        ]
        
        html = self.manager._create_listing_html(listings)
        
        assert 'Test Book' in html
        assert '<img src=' not in html  # No image tag should be present
    
    def test_create_listing_html_with_price(self):
        """Test HTML creation for listings with price"""
        listings = [
            {
                'title': 'Test Book',
                'description': 'Test Description',
                'price': 15.99,
                'location': 'Test Location',
                'listing_url': 'https://example.com/1'
            }
        ]
        
        html = self.manager._create_listing_html(listings)
        
        assert '15.99 €' in html
        assert 'Zu verschenken' not in html