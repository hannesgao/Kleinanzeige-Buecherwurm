import pytest
from unittest.mock import Mock, patch
from src.utils.error_handler import ErrorHandler

class TestErrorHandler:
    """Test cases for the ErrorHandler class"""
    
    def test_log_exception_basic(self):
        """Test basic exception logging"""
        error = ValueError("Test error")
        
        with patch('src.utils.error_handler.logger') as mock_logger:
            ErrorHandler.log_exception(error)
            
            mock_logger.error.assert_called()
            # Check that error type and message are logged
            args = mock_logger.error.call_args_list
            assert any("ValueError" in str(call) for call in args)
            assert any("Test error" in str(call) for call in args)
    
    def test_log_exception_with_context(self):
        """Test exception logging with context"""
        error = ValueError("Test error")
        context = {"url": "https://example.com", "attempt": 1}
        
        with patch('src.utils.error_handler.logger') as mock_logger:
            ErrorHandler.log_exception(error, context)
            
            mock_logger.error.assert_called()
            # Check that context is logged
            args = mock_logger.error.call_args_list
            assert any("url" in str(call) for call in args)
    
    def test_handle_selenium_error_stale_element(self):
        """Test handling of stale element reference error"""
        from selenium.common.exceptions import StaleElementReferenceException
        
        error = StaleElementReferenceException("Element is stale")
        result = ErrorHandler.handle_selenium_error(error)
        
        assert result is True  # Should be recoverable
    
    def test_handle_selenium_error_no_window(self):
        """Test handling of no window error"""
        from selenium.common.exceptions import NoSuchWindowException
        
        error = NoSuchWindowException("Window not found")
        result = ErrorHandler.handle_selenium_error(error)
        
        assert result is False  # Should not be recoverable
    
    def test_handle_network_error_connection(self):
        """Test handling of connection errors"""
        import requests
        
        error = requests.exceptions.ConnectionError("Connection failed")
        result = ErrorHandler.handle_network_error(error)
        
        assert result is True  # Should be recoverable
    
    def test_handle_network_error_timeout(self):
        """Test handling of timeout errors"""
        import requests
        
        error = requests.exceptions.Timeout("Request timeout")
        result = ErrorHandler.handle_network_error(error)
        
        assert result is True  # Should be recoverable
    
    def test_create_error_report(self):
        """Test error report creation"""
        error = ValueError("Test error")
        session_data = {"session_id": "123", "start_time": "2023-01-01"}
        
        report = ErrorHandler.create_error_report(error, session_data)
        
        assert report["error_type"] == "ValueError"
        assert report["error_message"] == "Test error"
        assert report["session_data"] == session_data
        assert "traceback" in report
        assert "timestamp" in report
        assert "python_version" in report