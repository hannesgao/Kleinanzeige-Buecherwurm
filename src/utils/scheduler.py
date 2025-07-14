from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from typing import Callable, Dict

class TaskScheduler:
    """Schedule crawler tasks"""
    
    def __init__(self):
        self.scheduler = BlockingScheduler()
        
    def add_cron_job(self, func: Callable, cron_expression: str, job_id: str):
        """Add a cron job to the scheduler"""
        trigger = CronTrigger.from_crontab(cron_expression)
        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            replace_existing=True
        )
        logger.info(f"Scheduled job {job_id} with cron: {cron_expression}")
        
    def start(self):
        """Start the scheduler"""
        logger.info("Starting scheduler...")
        try:
            self.scheduler.start()
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            self.scheduler.shutdown()
            
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")