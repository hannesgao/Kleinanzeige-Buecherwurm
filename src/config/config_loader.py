import yaml
import os
from dotenv import load_dotenv
from typing import Dict, Any
import re

class ConfigLoader:
    """Load and manage configuration from yaml and environment variables"""
    
    def __init__(self, config_path: str = "config.yaml"):
        load_dotenv()
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from yaml file"""
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        return self._replace_env_vars(config)
        
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
                env_value = os.getenv(match, '')
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