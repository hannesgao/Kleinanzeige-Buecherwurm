import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from loguru import logger
import html

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
            
        subject = f"New Books on Kleinanzeigen: {len(listings)} Listings"
        body = self._create_listing_html(listings)
        
        recipients = self.config.get('email', {}).get('recipients', [])
        self.send_email(subject, body, recipients)
        
    def _create_listing_html(self, listings: List[Dict]) -> str:
        """Create HTML content for listing notification"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }
                h1 {
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }
                .listing {
                    background: #f9f9f9;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .listing h2 {
                    margin-top: 0;
                    color: #2c3e50;
                    font-size: 1.3em;
                }
                .listing-image {
                    float: right;
                    max-width: 150px;
                    max-height: 150px;
                    margin: 0 0 10px 15px;
                    border-radius: 4px;
                }
                .price {
                    font-size: 1.2em;
                    font-weight: bold;
                    color: #27ae60;
                    margin: 10px 0;
                }
                .location {
                    color: #7f8c8d;
                    margin: 5px 0;
                }
                .description {
                    margin: 10px 0;
                    color: #555;
                }
                .view-button {
                    display: inline-block;
                    background: #3498db;
                    color: white;
                    padding: 8px 16px;
                    text-decoration: none;
                    border-radius: 4px;
                    margin-top: 10px;
                }
                .view-button:hover {
                    background: #2980b9;
                }
                .footer {
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    text-align: center;
                    color: #7f8c8d;
                    font-size: 0.9em;
                }
                .clearfix::after {
                    content: "";
                    display: table;
                    clear: both;
                }
            </style>
        </head>
        <body>
            <h1>New Books on Kleinanzeigen 📚</h1>
            <p>Found <strong>{count}</strong> new free book collections!</p>
        """.format(count=len(listings))
        
        for listing in listings:
            # Escape HTML to prevent XSS
            title = html.escape(listing.get('title', 'No Title'))
            description = html.escape(listing.get('description', ''))[:300]
            if len(listing.get('description', '')) > 300:
                description += '...'
            
            price = listing.get('price', 0)
            price_text = 'Free' if price == 0 else f'{price:.2f} €'
            
            location = html.escape(listing.get('location', 'Unknown'))
            url = html.escape(listing.get('listing_url', '#'))
            thumbnail = html.escape(listing.get('thumbnail_url', '')) if listing.get('thumbnail_url') else ''
            
            html += f"""
            <div class="listing clearfix">
                {f'<img src="{thumbnail}" class="listing-image" alt="{title}">' if thumbnail else ''}
                <h2>{title}</h2>
                <p class="price">{price_text}</p>
                <p class="location">📍 {location}</p>
                <p class="description">{description}</p>
                <a href="{url}" class="view-button">View Listing →</a>
            </div>
            """
        
        html += """
            <div class="footer">
                <p>This email was automatically generated by Kleinanzeigen-Bücherwurm.</p>
                <p>To stop receiving notifications, please adjust your configuration.</p>
            </div>
        </body>
        </html>
        """
        
        return html