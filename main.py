#!/usr/bin/env python3
import argparse
import sys
from loguru import logger
from src.config import ConfigLoader, DatabaseManager
from src.scraper import KleinanzeigenCrawler
from src.utils import setup_logger, TaskScheduler, NotificationManager

def main():
    """Main entry point for the crawler"""
    parser = argparse.ArgumentParser(description='Kleinanzeigen Book Crawler')
    parser.add_argument('--config', default='config.yaml', help='Path to config file')
    parser.add_argument('--schedule', action='store_true', help='Run with scheduler')
    parser.add_argument('--init-db', action='store_true', help='Initialize database tables')
    
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
    
    # Initialize crawler
    crawler = KleinanzeigenCrawler(config.get('selenium', {}))
    
    # Initialize notifications
    notifier = NotificationManager(config.get('notifications', {}))
    
    if args.schedule:
        # Run with scheduler
        scheduler = TaskScheduler()
        cron = config.get('schedule.cron', '0 */6 * * *')
        scheduler.add_cron_job(
            lambda: run_crawl(crawler, db_manager, notifier, config),
            cron,
            'kleinanzeigen_crawl'
        )
        scheduler.start()
    else:
        # Run once
        run_crawl(crawler, db_manager, notifier, config)

def run_crawl(crawler, db_manager, notifier, config):
    """Execute a single crawl session"""
    logger.info("Starting crawl session...")
    
    try:
        # TODO: Implement crawl logic
        # 1. Search for books
        # 2. Parse listings
        # 3. Save to database
        # 4. Send notifications
        pass
        
    except Exception as e:
        logger.error(f"Crawl failed: {e}")
        raise
    finally:
        crawler.close()

if __name__ == "__main__":
    main()