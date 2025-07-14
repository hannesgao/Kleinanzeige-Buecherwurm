import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from loguru import logger

class NotificationManager:
    """Handle email notifications for new listings"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get('enabled', False)
        
    def send_email(self, subject: str, body: str, recipients: List[str]):
        """Send email notification"""
        if not self.enabled:
            logger.info("Notifications disabled, skipping email")
            return
            
        email_config = self.config.get('email', {})
        
        try:
            msg = MIMEMultipart()
            msg['From'] = email_config.get('sender')
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(email_config.get('smtp_server'), email_config.get('smtp_port')) as server:
                server.starttls()
                server.login(email_config.get('sender'), email_config.get('password'))
                server.send_message(msg)
                
            logger.info(f"Email sent successfully to {len(recipients)} recipients")
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            
    def notify_new_listings(self, listings: List[Dict]):
        """Send notification about new listings"""
        if not listings:
            return
            
        subject = f"Neue Bücher auf Kleinanzeigen: {len(listings)} Anzeigen"
        body = self._create_listing_html(listings)
        
        recipients = self.config.get('email', {}).get('recipients', [])
        self.send_email(subject, body, recipients)
        
    def _create_listing_html(self, listings: List[Dict]) -> str:
        """Create HTML content for listing notification"""
        # TODO: Implement HTML template for listings
        pass