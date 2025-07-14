from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base, TimestampMixin

class CrawlSession(Base, TimestampMixin):
    __tablename__ = 'crawl_sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), unique=True, nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    
    # Statistics
    total_listings_found = Column(Integer, default=0)
    new_listings_found = Column(Integer, default=0)
    updated_listings = Column(Integer, default=0)
    pages_crawled = Column(Integer, default=0)
    
    # Status
    status = Column(String(50), default='running')  # running, completed, failed
    error_message = Column(Text)
    
    # Configuration snapshot
    search_config = Column(Text)  # JSON of search parameters used
    
    # Relationships
    listings = relationship("BookListing", back_populates="crawl_session")
    
    def __repr__(self):
        return f"<CrawlSession(id={self.id}, status={self.status}, listings={self.total_listings_found})>"