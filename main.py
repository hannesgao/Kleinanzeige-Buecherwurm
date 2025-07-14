#!/usr/bin/env python3
import argparse
import sys
import json
import uuid
from datetime import datetime
from typing import List, Dict
from loguru import logger
from src.config import ConfigLoader, DatabaseManager
from src.scraper import KleinanzeigenCrawler
from src.utils import setup_logger, TaskScheduler, NotificationManager
from src.models import BookListing, CrawlSession
from sqlalchemy.exc import IntegrityError

def main():
    """Main entry point for the crawler"""
    parser = argparse.ArgumentParser(description='Kleinanzeigen Book Crawler')
    parser.add_argument('--config', default='config.yaml', help='Path to config file')
    parser.add_argument('--schedule', action='store_true', help='Run with scheduler')
    parser.add_argument('--init-db', action='store_true', help='Initialize database tables')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--test', action='store_true', help='Run in test mode (limit to 5 listings)')
    
    args = parser.parse_args()
    
    # Load configuration
    config = ConfigLoader(args.config)
    
    # Setup logger
    setup_logger(config.get('logging', {}))
    
    # Initialize database
    db_manager = DatabaseManager(config.get('database', {}))
    
    if args.init_db:
        logger.info("Initializing database tables...")
        db_manager.create_tables()
        logger.info("Database initialization complete")
        return
    
    # Override headless mode if specified
    selenium_config = config.get('selenium', {})
    if args.headless:
        selenium_config['headless'] = True
    
    # Initialize notifications
    notifier = NotificationManager(config.get('notifications', {}))
    
    if args.schedule:
        # Run with scheduler
        scheduler = TaskScheduler()
        cron = config.get('schedule.cron', '0 */6 * * *')
        scheduler.add_cron_job(
            lambda: run_crawl_session(db_manager, notifier, config, selenium_config, args.test),
            cron,
            'kleinanzeigen_crawl'
        )
        scheduler.start()
    else:
        # Run once
        run_crawl_session(db_manager, notifier, config, selenium_config, args.test)

def run_crawl_session(db_manager, notifier, config, selenium_config, test_mode=False):
    """Execute a single crawl session"""
    session_id = str(uuid.uuid4())
    logger.info(f"Starting crawl session {session_id}")
    
    crawler = None
    crawl_session = None
    
    try:
        # Create crawl session in database
        with db_manager.get_session() as db:
            crawl_session = CrawlSession(
                session_id=session_id,
                start_time=datetime.utcnow(),
                status='running',
                search_config=json.dumps(config.get('search', {}))
            )
            db.add(crawl_session)
            db.commit()
            crawl_session_id = crawl_session.id
        
        # Initialize crawler
        crawler = KleinanzeigenCrawler(selenium_config)
        
        # Get search parameters
        search_params = config.get('search', {})
        
        # Search for listings
        logger.info("Searching for book listings...")
        listing_urls = crawler.search_books(search_params)
        
        if test_mode:
            listing_urls = listing_urls[:5]
            logger.info(f"Test mode: limiting to {len(listing_urls)} listings")
        
        logger.info(f"Found {len(listing_urls)} listings to process")
        
        # Process each listing
        new_listings = []
        updated_listings = []
        
        for i, url in enumerate(listing_urls, 1):
            logger.info(f"Processing listing {i}/{len(listing_urls)}: {url}")
            
            try:
                # Get listing details
                listing_data = crawler.get_listing_details(url)
                
                if not listing_data:
                    logger.warning(f"Failed to get details for {url}")
                    continue
                
                # Save to database
                is_new = save_listing(db_manager, listing_data, crawl_session_id)
                
                if is_new:
                    new_listings.append(listing_data)
                else:
                    updated_listings.append(listing_data)
                    
            except Exception as e:
                logger.error(f"Error processing listing {url}: {e}")
                continue
        
        # Update crawl session statistics
        with db_manager.get_session() as db:
            crawl_session = db.query(CrawlSession).filter_by(id=crawl_session_id).first()
            crawl_session.total_listings_found = len(listing_urls)
            crawl_session.new_listings_found = len(new_listings)
            crawl_session.updated_listings = len(updated_listings)
            crawl_session.pages_crawled = len(listing_urls)  # Simplified for now
            crawl_session.status = 'completed'
            crawl_session.end_time = datetime.utcnow()
            db.commit()
        
        logger.info(f"Crawl session completed. New: {len(new_listings)}, Updated: {len(updated_listings)}")
        
        # Send notifications for new listings
        if new_listings and not test_mode:
            logger.info(f"Sending notifications for {len(new_listings)} new listings")
            notifier.notify_new_listings(new_listings)
            
    except Exception as e:
        logger.error(f"Crawl session failed: {e}")
        
        # Update session status
        if crawl_session_id:
            with db_manager.get_session() as db:
                crawl_session = db.query(CrawlSession).filter_by(id=crawl_session_id).first()
                if crawl_session:
                    crawl_session.status = 'failed'
                    crawl_session.error_message = str(e)
                    crawl_session.end_time = datetime.utcnow()
                    db.commit()
        raise
        
    finally:
        if crawler:
            crawler.close()

def save_listing(db_manager, listing_data: Dict, crawl_session_id: int) -> bool:
    """Save listing to database and return True if new listing"""
    is_new = False
    
    with db_manager.get_session() as db:
        # Check if listing already exists
        existing = db.query(BookListing).filter_by(
            listing_id=listing_data.get('listing_id')
        ).first()
        
        if existing:
            # Update existing listing
            logger.debug(f"Updating existing listing {existing.listing_id}")
            
            # Update fields
            existing.title = listing_data.get('title', existing.title)
            existing.description = listing_data.get('description', existing.description)
            existing.price = listing_data.get('price', existing.price)
            existing.location = listing_data.get('location', existing.location)
            existing.postal_code = listing_data.get('postal_code', existing.postal_code)
            existing.view_count = listing_data.get('view_count', existing.view_count)
            existing.last_seen = datetime.utcnow()
            existing.times_seen = existing.times_seen + 1
            existing.is_active = True
            
            # Update images if available
            if listing_data.get('image_urls'):
                existing.image_urls = json.dumps(listing_data['image_urls'])
                existing.thumbnail_url = listing_data.get('thumbnail_url')
                
        else:
            # Create new listing
            logger.debug(f"Creating new listing {listing_data.get('listing_id')}")
            is_new = True
            
            new_listing = BookListing(
                listing_id=listing_data.get('listing_id'),
                title=listing_data.get('title'),
                description=listing_data.get('description'),
                price=listing_data.get('price', 0.0),
                location=listing_data.get('location'),
                postal_code=listing_data.get('postal_code'),
                distance_km=listing_data.get('distance_km'),
                seller_name=listing_data.get('seller_name'),
                seller_type=listing_data.get('seller_type', 'private'),
                seller_id=listing_data.get('seller_id'),
                category=listing_data.get('category'),
                subcategory=listing_data.get('subcategory'),
                condition=listing_data.get('condition'),
                listing_date=listing_data.get('listing_date'),
                view_count=listing_data.get('view_count'),
                listing_url=listing_data.get('listing_url'),
                thumbnail_url=listing_data.get('thumbnail_url'),
                image_urls=json.dumps(listing_data.get('image_urls', [])),
                phone_number=listing_data.get('phone_number'),
                contact_name=listing_data.get('contact_name'),
                crawl_session_id=crawl_session_id
            )
            
            db.add(new_listing)
        
        try:
            db.commit()
        except IntegrityError as e:
            logger.error(f"Database integrity error: {e}")
            db.rollback()
            is_new = False
            
    return is_new

if __name__ == "__main__":
    main()