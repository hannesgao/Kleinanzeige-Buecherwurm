from loguru import logger
import sys
from typing import Dict

def setup_logger(config: Dict):
    """Configure logger based on settings"""
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stderr,
        format=config.get('format', '{time} | {level} | {message}'),
        level=config.get('level', 'INFO')
    )
    
    # Add file handler with rotation
    logger.add(
        "logs/crawler_{time}.log",
        rotation=config.get('rotation', '100 MB'),
        retention=config.get('retention', '7 days'),
        format=config.get('format', '{time} | {level} | {message}'),
        level=config.get('level', 'INFO')
    )
    
    return logger