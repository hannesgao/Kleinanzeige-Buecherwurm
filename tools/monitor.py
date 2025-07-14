#!/usr/bin/env python3
"""
Monitoring script for Kleinanzeigen Crawler
This script provides monitoring and statistics for the crawler
"""

import sys
import os
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def show_recent_sessions(limit=10):
    """Show recent crawl sessions"""
    print(f"📊 Recent Crawl Sessions (last {limit})")
    print("=" * 60)
    
    try:
        from src.config import DatabaseManager, ConfigLoader
        
        config = ConfigLoader()
        db_manager = DatabaseManager(config.get('database', {}))
        
        with db_manager.get_session() as db:
            from src.models import CrawlSession
            
            sessions = db.query(CrawlSession).order_by(
                CrawlSession.start_time.desc()
            ).limit(limit).all()
            
            if not sessions:
                print("No crawl sessions found")
                return
            
            for session in sessions:
                status_emoji = {
                    'completed': '✅',
                    'failed': '❌',
                    'running': '🔄'
                }.get(session.status, '❓')
                
                duration = ""
                if session.end_time:
                    duration = session.end_time - session.start_time
                    duration_str = f" ({duration})"
                else:
                    duration_str = " (running)"
                
                print(f"{status_emoji} {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}{duration_str}")
                print(f"   Found: {session.total_listings_found or 0} | "
                      f"New: {session.new_listings_found or 0} | "
                      f"Updated: {session.updated_listings or 0}")
                
                if session.error_message:
                    print(f"   Error: {session.error_message[:100]}...")
                
                print()
                
    except Exception as e:
        print(f"Error fetching sessions: {e}")

def show_listing_stats():
    """Show listing statistics"""
    print("📈 Listing Statistics")
    print("=" * 60)
    
    try:
        from src.config import DatabaseManager, ConfigLoader
        
        config = ConfigLoader()
        db_manager = DatabaseManager(config.get('database', {}))
        
        with db_manager.get_session() as db:
            from src.models import BookListing
            from sqlalchemy import func
            
            # Total listings
            total = db.query(func.count(BookListing.id)).scalar()
            active = db.query(func.count(BookListing.id)).filter(
                BookListing.is_active == True
            ).scalar()
            
            print(f"Total listings: {total}")
            print(f"Active listings: {active}")
            print(f"Inactive listings: {total - active}")
            print()
            
            # Listings by location
            print("Top locations:")
            locations = db.query(
                BookListing.location,
                func.count(BookListing.id).label('count')
            ).filter(
                BookListing.is_active == True
            ).group_by(
                BookListing.location
            ).order_by(
                func.count(BookListing.id).desc()
            ).limit(10).all()
            
            for location, count in locations:
                print(f"  {location}: {count}")
            print()
            
            # Recent listings
            print("Recent listings (last 7 days):")
            week_ago = datetime.now() - timedelta(days=7)
            recent = db.query(func.count(BookListing.id)).filter(
                BookListing.created_at >= week_ago
            ).scalar()
            
            print(f"  New listings: {recent}")
            
    except Exception as e:
        print(f"Error fetching statistics: {e}")

def show_system_status():
    """Show system status"""
    print("🖥️ System Status")
    print("=" * 60)
    
    try:
        import psutil
        import shutil
        
        # Memory usage
        memory = psutil.virtual_memory()
        print(f"Memory: {memory.percent}% used ({memory.used / 1024**3:.1f} GB / {memory.total / 1024**3:.1f} GB)")
        
        # Disk usage
        disk = shutil.disk_usage('.')
        disk_percent = (disk.used / disk.total) * 100
        print(f"Disk: {disk_percent:.1f}% used ({disk.used / 1024**3:.1f} GB / {disk.total / 1024**3:.1f} GB)")
        
        # CPU usage
        cpu = psutil.cpu_percent(interval=1)
        print(f"CPU: {cpu}% used")
        
        # Check if Chrome is running
        chrome_procs = [p for p in psutil.process_iter(['pid', 'name']) if 'chrome' in p.info['name'].lower()]
        if chrome_procs:
            print(f"Chrome processes: {len(chrome_procs)} running")
        else:
            print("Chrome processes: None running")
        
    except ImportError:
        print("psutil not installed - install with: pip3 install psutil")
    except Exception as e:
        print(f"Error checking system status: {e}")

def show_log_tail(lines=20):
    """Show recent log entries"""
    print(f"📝 Recent Log Entries (last {lines} lines)")
    print("=" * 60)
    
    try:
        log_dir = Path('logs')
        if not log_dir.exists():
            print("No logs directory found")
            return
        
        # Find most recent log file
        log_files = list(log_dir.glob('crawler_*.log'))
        if not log_files:
            print("No log files found")
            return
        
        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
        
        # Read last N lines
        with open(latest_log, 'r') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:]
        
        print(f"File: {latest_log.name}")
        print("-" * 40)
        
        for line in recent_lines:
            print(line.rstrip())
            
    except Exception as e:
        print(f"Error reading logs: {e}")

def cleanup_old_data(days=30):
    """Clean up old data"""
    print(f"🧹 Cleaning up data older than {days} days")
    print("=" * 60)
    
    try:
        from src.config import DatabaseManager, ConfigLoader
        
        config = ConfigLoader()
        db_manager = DatabaseManager(config.get('database', {}))
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with db_manager.get_session() as db:
            from src.models import BookListing, CrawlSession
            
            # Clean up old inactive listings
            old_listings = db.query(BookListing).filter(
                BookListing.is_active == False,
                BookListing.updated_at < cutoff_date
            ).count()
            
            if old_listings > 0:
                db.query(BookListing).filter(
                    BookListing.is_active == False,
                    BookListing.updated_at < cutoff_date
                ).delete()
                print(f"Deleted {old_listings} old inactive listings")
            
            # Clean up old completed sessions
            old_sessions = db.query(CrawlSession).filter(
                CrawlSession.status == 'completed',
                CrawlSession.end_time < cutoff_date
            ).count()
            
            if old_sessions > 0:
                db.query(CrawlSession).filter(
                    CrawlSession.status == 'completed',
                    CrawlSession.end_time < cutoff_date
                ).delete()
                print(f"Deleted {old_sessions} old completed sessions")
            
            if old_listings == 0 and old_sessions == 0:
                print("No old data to clean up")
        
        # Clean up old log files
        log_dir = Path('logs')
        if log_dir.exists():
            old_logs = []
            for log_file in log_dir.glob('*.log'):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    old_logs.append(log_file)
                    log_file.unlink()
            
            if old_logs:
                print(f"Deleted {len(old_logs)} old log files")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")

def main():
    """Main monitoring interface"""
    parser = argparse.ArgumentParser(
        description='Kleinanzeigen Crawler Monitor',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--sessions', type=int, default=10,
                       help='Show recent crawl sessions (default: 10)')
    parser.add_argument('--stats', action='store_true',
                       help='Show listing statistics')
    parser.add_argument('--system', action='store_true',
                       help='Show system status')
    parser.add_argument('--logs', type=int, default=20,
                       help='Show recent log entries (default: 20)')
    parser.add_argument('--cleanup', type=int, metavar='DAYS',
                       help='Clean up data older than DAYS (default: 30)')
    parser.add_argument('--all', action='store_true',
                       help='Show all information')
    
    args = parser.parse_args()
    
    if args.all:
        show_recent_sessions(args.sessions)
        print()
        show_listing_stats()
        print()
        show_system_status()
        print()
        show_log_tail(args.logs)
    else:
        if args.sessions or not any([args.stats, args.system, args.logs, args.cleanup]):
            show_recent_sessions(args.sessions)
        
        if args.stats:
            show_listing_stats()
        
        if args.system:
            show_system_status()
        
        if args.logs:
            show_log_tail(args.logs)
        
        if args.cleanup:
            cleanup_old_data(args.cleanup)

if __name__ == "__main__":
    main()