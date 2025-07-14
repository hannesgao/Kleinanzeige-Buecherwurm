-- PostgreSQL schema for Kleinanzeigen Crawler

-- Create database (run as superuser)
-- CREATE DATABASE kleinanzeigen_crawler;

-- Crawl sessions table
CREATE TABLE IF NOT EXISTS crawl_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    total_listings_found INTEGER DEFAULT 0,
    new_listings_found INTEGER DEFAULT 0,
    updated_listings INTEGER DEFAULT 0,
    pages_crawled INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'running',
    error_message TEXT,
    search_config TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Book listings table
CREATE TABLE IF NOT EXISTS book_listings (
    id SERIAL PRIMARY KEY,
    listing_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) DEFAULT 0.00,
    location VARCHAR(200),
    postal_code VARCHAR(10),
    distance_km DECIMAL(5, 2),
    
    -- Seller information
    seller_name VARCHAR(200),
    seller_type VARCHAR(50),
    seller_id VARCHAR(100),
    
    -- Listing details
    category VARCHAR(200),
    subcategory VARCHAR(200),
    condition VARCHAR(100),
    listing_date TIMESTAMP,
    view_count INTEGER,
    
    -- URLs and images
    listing_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    image_urls TEXT,
    
    -- Contact information
    phone_number VARCHAR(50),
    contact_name VARCHAR(200),
    
    -- Tracking
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    times_seen INTEGER DEFAULT 1,
    
    -- Foreign keys
    crawl_session_id INTEGER REFERENCES crawl_sessions(id),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_listing_id ON book_listings(listing_id);
CREATE INDEX idx_seller_id ON book_listings(seller_id);
CREATE INDEX idx_location ON book_listings(location);
CREATE INDEX idx_price ON book_listings(price);
CREATE INDEX idx_listing_date ON book_listings(listing_date);
CREATE INDEX idx_is_active ON book_listings(is_active);
CREATE INDEX idx_crawl_session ON book_listings(crawl_session_id);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_crawl_sessions_updated_at BEFORE UPDATE
    ON crawl_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_book_listings_updated_at BEFORE UPDATE
    ON book_listings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();