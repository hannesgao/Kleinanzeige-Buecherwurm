import pytest
from src.scraper.parser import ListingParser

class TestListingParser:
    """Test cases for the ListingParser class"""
    
    def setup_method(self):
        self.parser = ListingParser()
    
    def test_clean_price_free_items(self):
        """Test price cleaning for free items"""
        assert self.parser.clean_price("Zu verschenken") == 0.0
        assert self.parser.clean_price("Gratis") == 0.0
        assert self.parser.clean_price("Kostenlos") == 0.0
        assert self.parser.clean_price("Free") == 0.0
    
    def test_clean_price_numeric(self):
        """Test price cleaning for numeric values"""
        assert self.parser.clean_price("10 €") == 10.0
        assert self.parser.clean_price("5,50 EUR") == 5.5
        assert self.parser.clean_price("100 VB") == 100.0
        assert self.parser.clean_price("15,99 Festpreis") == 15.99
    
    def test_clean_price_edge_cases(self):
        """Test price cleaning edge cases"""
        assert self.parser.clean_price("") == 0.0
        assert self.parser.clean_price(None) == 0.0
        assert self.parser.clean_price("Kein Preis") == 0.0
    
    def test_parse_relative_date(self):
        """Test relative date parsing"""
        result = self.parser.parse_relative_date("Heute")
        assert result is not None
        
        result = self.parser.parse_relative_date("Gestern")
        assert result is not None
        
        result = self.parser.parse_relative_date("vor 3 Tagen")
        assert result is not None