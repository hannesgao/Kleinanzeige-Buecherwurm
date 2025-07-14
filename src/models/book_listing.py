from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class BookListing(Base, TimestampMixin):
    __tablename__ = 'book_listings'
    
    id = Column(Integer, primary_key=True)
    listing_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    price = Column(Float, default=0.0)
    location = Column(String(200))
    postal_code = Column(String(10))
    distance_km = Column(Float)
    
    # Seller information
    seller_name = Column(String(200))
    seller_type = Column(String(50))  # private or commercial
    seller_id = Column(String(100))
    
    # Listing details
    category = Column(String(200))
    subcategory = Column(String(200))
    condition = Column(String(100))
    listing_date = Column(DateTime)
    view_count = Column(Integer)
    
    # URLs and images
    listing_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500))
    image_urls = Column(Text)  # JSON array of image URLs
    
    # Contact information
    phone_number = Column(String(50))
    contact_name = Column(String(200))
    
    # Tracking
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    times_seen = Column(Integer, default=1)
    
    # Crawl session relationship
    crawl_session_id = Column(Integer, ForeignKey('crawl_sessions.id'))
    crawl_session = relationship("CrawlSession", back_populates="listings")
    
    def __repr__(self):
        return f"<BookListing(id={self.id}, title='{self.title[:50]}...', price={self.price})>"