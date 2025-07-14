from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from loguru import logger
from typing import Optional

class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self, config: dict):
        self.config = config
        self.engine = None
        self.SessionLocal = None
        self._init_database()
        
    def _init_database(self):
        """Initialize database connection"""
        db_config = self.config
        connection_string = (
            f"postgresql://{db_config['user']}:{db_config['password']}"
            f"@{db_config['host']}:{db_config['port']}/{db_config['name']}"
        )
        
        self.engine = create_engine(
            connection_string,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info("Database connection initialized")
        
    @contextmanager
    def get_session(self) -> Session:
        """Get database session context manager"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
            
    def create_tables(self):
        """Create all tables in the database"""
        from ..models.base import Base
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")