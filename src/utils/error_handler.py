from typing import Optional, Dict, Any
from loguru import logger
import traceback
import sys
from datetime import datetime

class ErrorHandler:
    """Centralized error handling for the crawler"""
    
    @staticmethod
    def log_exception(error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log exception with context information"""
        error_type = type(error).__name__
        error_message = str(error)
        
        logger.error(f"{error_type}: {error_message}")
        
        if context:
            logger.error(f"Context: {context}")
        
        # Log full traceback in debug mode
        logger.debug(f"Traceback:\n{traceback.format_exc()}")
    
    @staticmethod
    def handle_selenium_error(error: Exception, url: Optional[str] = None) -> bool:
        """
        Handle Selenium-specific errors
        Returns True if error is recoverable
        """
        from selenium.common.exceptions import (
            StaleElementReferenceException,
            NoSuchWindowException,
            SessionNotCreatedException
        )
        
        if isinstance(error, StaleElementReferenceException):
            logger.warning(f"Stale element reference at {url}, retrying...")
            return True
            
        elif isinstance(error, NoSuchWindowException):
            logger.error(f"Browser window closed unexpectedly at {url}")
            return False
            
        elif isinstance(error, SessionNotCreatedException):
            logger.error("Failed to create browser session. Check Chrome/ChromeDriver compatibility")
            return False
            
        return True
    
    @staticmethod
    def handle_network_error(error: Exception, url: Optional[str] = None) -> bool:
        """
        Handle network-related errors
        Returns True if error is recoverable
        """
        import requests
        from urllib3.exceptions import MaxRetryError
        
        if isinstance(error, requests.exceptions.ConnectionError):
            logger.warning(f"Connection error at {url}, network may be down")
            return True
            
        elif isinstance(error, requests.exceptions.Timeout):
            logger.warning(f"Request timeout at {url}")
            return True
            
        elif isinstance(error, MaxRetryError):
            logger.error(f"Max retries exceeded for {url}")
            return False
            
        return True
    
    @staticmethod
    def create_error_report(error: Exception, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed error report for debugging"""
        return {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'session_data': session_data,
            'python_version': sys.version,
            'timestamp': datetime.utcnow().isoformat()
        }