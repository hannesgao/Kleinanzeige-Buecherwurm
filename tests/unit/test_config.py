import pytest
import os
import tempfile
from src.config.config_loader import ConfigLoader

class TestConfigLoader:
    """Test cases for the ConfigLoader class"""
    
    def test_load_config_with_env_vars(self):
        """Test loading config with environment variables"""
        # Create a temporary config file
        config_content = """
        database:
          host: "${DB_HOST}"
          port: 5432
          name: "${DB_NAME}"
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            config_path = f.name
        
        try:
            # Set environment variables
            os.environ['DB_HOST'] = 'localhost'
            os.environ['DB_NAME'] = 'testdb'
            
            # Load config
            config_loader = ConfigLoader(config_path)
            
            # Test values
            assert config_loader.get('database.host') == 'localhost'
            assert config_loader.get('database.name') == 'testdb'
            assert config_loader.get('database.port') == 5432
            
        finally:
            # Cleanup
            os.unlink(config_path)
            os.environ.pop('DB_HOST', None)
            os.environ.pop('DB_NAME', None)
    
    def test_get_nested_config(self):
        """Test getting nested configuration values"""
        config_content = """
        search:
          location: "Karlsruhe"
          radius_km: 20
          keywords:
            - "sammlung"
            - "konvolut"
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            config_path = f.name
        
        try:
            config_loader = ConfigLoader(config_path)
            
            assert config_loader.get('search.location') == 'Karlsruhe'
            assert config_loader.get('search.radius_km') == 20
            assert config_loader.get('search.keywords') == ['sammlung', 'konvolut']
            assert config_loader.get('nonexistent.key', 'default') == 'default'
            
        finally:
            os.unlink(config_path)