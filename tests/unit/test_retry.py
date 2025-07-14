import pytest
import time
from unittest.mock import Mock, patch
from src.utils.retry import retry_on_exception, NetworkError, ParseError

class TestRetryDecorator:
    """Test cases for the retry decorator"""
    
    def test_retry_success_on_first_attempt(self):
        """Test that function succeeds on first attempt"""
        @retry_on_exception(max_attempts=3, delay=0.1)
        def successful_function():
            return "success"
        
        result = successful_function()
        assert result == "success"
    
    def test_retry_success_after_failures(self):
        """Test that function succeeds after some failures"""
        call_count = 0
        
        @retry_on_exception(max_attempts=3, delay=0.1)
        def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = failing_then_success()
        assert result == "success"
        assert call_count == 3
    
    def test_retry_exhausted_attempts(self):
        """Test that function fails after exhausting all attempts"""
        @retry_on_exception(max_attempts=2, delay=0.1)
        def always_failing():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            always_failing()
    
    def test_retry_with_specific_exceptions(self):
        """Test that retry only catches specific exceptions"""
        @retry_on_exception(max_attempts=2, delay=0.1, exceptions=(NetworkError,))
        def network_error_function():
            raise NetworkError("Network issue")
        
        with pytest.raises(NetworkError):
            network_error_function()
        
        @retry_on_exception(max_attempts=2, delay=0.1, exceptions=(NetworkError,))
        def other_error_function():
            raise ValueError("Different error")
        
        with pytest.raises(ValueError):
            other_error_function()
    
    def test_retry_backoff(self):
        """Test that backoff works correctly"""
        start_time = time.time()
        
        @retry_on_exception(max_attempts=3, delay=0.1, backoff=2.0)
        def always_failing():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            always_failing()
        
        elapsed = time.time() - start_time
        # Should take at least 0.1 + 0.2 = 0.3 seconds
        assert elapsed >= 0.3
    
    def test_custom_exceptions(self):
        """Test custom exception types"""
        error = NetworkError("Network error")
        assert isinstance(error, Exception)
        
        error = ParseError("Parse error")
        assert isinstance(error, Exception)