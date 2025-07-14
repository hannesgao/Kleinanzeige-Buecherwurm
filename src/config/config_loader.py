import yaml
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import re
from loguru import logger

class ConfigLoader:
    """Load and manage configuration from yaml and environment variables"""
    
    def __init__(self, config_path: str = "config.yaml"):
        load_dotenv()
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from yaml file"""
        try:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            if config is None:
                raise ValueError(f"Configuration file is empty or invalid: {self.config_path}")
                
            return self._replace_env_vars(config)
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file {self.config_path}: {e}")
        except FileNotFoundError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration from {self.config_path}: {e}")
        
    def _replace_env_vars(self, config: Any) -> Any:
        """Recursively replace environment variables in config"""
        if isinstance(config, dict):
            return {k: self._replace_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Replace ${VAR_NAME} with environment variable
            pattern = r'\$\{([^}]+)\}'
            matches = re.findall(pattern, config)
            for match in matches:
                env_value = os.getenv(match)
                if env_value is None:
                    logger.warning(f"Environment variable '{match}' not found, using empty string")
                    env_value = ''
                config = config.replace(f'${{{match}}}', env_value)
            return config
        return config
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def validate_required_env_vars(self, required_vars: list) -> bool:
        """Validate that all required environment variables are set"""
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        return True
    
    def validate_database_config(self) -> bool:
        """Validate database configuration is complete"""
        db_config = self.get('database', {})
        required_fields = ['host', 'name', 'user', 'password']
        
        missing_fields = []
        for field in required_fields:
            value = db_config.get(field)
            if not value or value.strip() == '':
                missing_fields.append(field)
        
        if missing_fields:
            logger.error(f"Missing database configuration fields: {', '.join(missing_fields)}")
            return False
        return True