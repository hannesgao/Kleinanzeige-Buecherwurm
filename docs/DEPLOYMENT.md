# Deployment Guide - Kleinanzeige Bücherwurm

This guide will help you deploy the Kleinanzeigen crawler in a production environment.

## Prerequisites

### System Requirements
- Ubuntu 20.04+ or similar Linux distribution
- Python 3.8+
- PostgreSQL 12+
- Chrome browser
- 4GB+ RAM (8GB recommended)
- 10GB+ disk space

### Required Software
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Chrome browser
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable -y

# Install additional dependencies
sudo apt install build-essential libpq-dev -y
```

## Database Setup

### 1. Create Database User
```bash
sudo -u postgres psql
```

```sql
-- Create user
CREATE USER kleinanzeigen_user WITH PASSWORD 'your_secure_password';

-- Create database
CREATE DATABASE kleinanzeigen_crawler OWNER kleinanzeigen_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE kleinanzeigen_crawler TO kleinanzeigen_user;

-- Exit
\q
```

### 2. Test Database Connection
```bash
psql -h localhost -U kleinanzeigen_user -d kleinanzeigen_crawler -c "SELECT version();"
```

## Application Setup

### 1. Clone and Install
```bash
# Clone repository
git clone https://github.com/hannesgao/Kleinanzeige-Buecherwurm.git
cd Kleinanzeige-Buecherwurm

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Required environment variables:
```bash
# Database
DB_HOST=localhost
DB_NAME=kleinanzeigen_crawler
DB_USER=kleinanzeigen_user
DB_PASSWORD=your_secure_password

# Email (optional)
SMTP_SERVER=smtp.gmail.com
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENT=recipient@example.com

# Application
DEBUG=False
```

### 3. Initialize Database
```bash
# Create tables
python main.py --init-db

# Verify setup
python test_database.py
```

### 4. Test Installation
```bash
# Run component tests
python test_components.py

# Test crawler (limited run)
python main.py --test --headless
```

## Production Deployment

### 1. Systemd Service
Create `/etc/systemd/system/kleinanzeigen-crawler.service`:

```ini
[Unit]
Description=Kleinanzeigen Book Crawler
After=network.target postgresql.service

[Service]
Type=simple
User=kleinanzeigen
Group=kleinanzeigen
WorkingDirectory=/home/kleinanzeigen/Kleinanzeige-Buecherwurm
Environment=PATH=/home/kleinanzeigen/Kleinanzeige-Buecherwurm/venv/bin
ExecStart=/home/kleinanzeigen/Kleinanzeige-Buecherwurm/venv/bin/python main.py --schedule --headless
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Create Service User
```bash
# Create dedicated user
sudo useradd -r -s /bin/false kleinanzeigen

# Set ownership
sudo chown -R kleinanzeigen:kleinanzeigen /home/kleinanzeigen/Kleinanzeige-Buecherwurm
```

### 3. Enable and Start Service
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable kleinanzeigen-crawler.service

# Start service
sudo systemctl start kleinanzeigen-crawler.service

# Check status
sudo systemctl status kleinanzeigen-crawler.service
```

## Monitoring

### 1. Log Management
```bash
# View logs
sudo journalctl -u kleinanzeigen-crawler.service -f

# View application logs
tail -f /home/kleinanzeigen/Kleinanzeige-Buecherwurm/logs/crawler_*.log
```

### 2. Database Monitoring
```bash
# Connect to database
psql -h localhost -U kleinanzeigen_user -d kleinanzeigen_crawler

# Check recent activity
SELECT * FROM crawl_sessions ORDER BY start_time DESC LIMIT 10;

# Check listing counts
SELECT COUNT(*) as total_listings, 
       COUNT(CASE WHEN is_active = true THEN 1 END) as active_listings
FROM book_listings;
```

### 3. System Monitoring
```bash
# Check disk usage
df -h

# Check memory usage
free -h

# Check Chrome processes
ps aux | grep chrome
```

## Maintenance

### 1. Regular Tasks
```bash
# Update dependencies (monthly)
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Clean old logs (weekly)
find logs/ -name "*.log" -mtime +7 -delete

# Database maintenance (monthly)
psql -h localhost -U kleinanzeigen_user -d kleinanzeigen_crawler -c "VACUUM ANALYZE;"
```

### 2. Backup Strategy
```bash
# Database backup
pg_dump -h localhost -U kleinanzeigen_user kleinanzeigen_crawler > backup_$(date +%Y%m%d).sql

# Application backup
tar -czf app_backup_$(date +%Y%m%d).tar.gz /home/kleinanzeigen/Kleinanzeige-Buecherwurm
```

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
   - ChromeDriver is auto-managed by webdriver-manager
   - Ensure Chrome browser is installed and up-to-date

2. **Database Connection Issues**
   - Check PostgreSQL service: `sudo systemctl status postgresql`
   - Verify credentials in `.env` file
   - Test connection manually

3. **Memory Issues**
   - Chrome can be memory-intensive
   - Consider running with `--headless` flag
   - Monitor with `htop` or `top`

4. **Network Issues**
   - Check internet connectivity
   - Verify kleinanzeigen.de accessibility
   - Review firewall settings

### Performance Tuning

1. **Database Optimization**
   ```sql
   -- Add indexes for better performance
   CREATE INDEX idx_listing_date ON book_listings(listing_date);
   CREATE INDEX idx_price ON book_listings(price);
   ```

2. **Memory Management**
   - Adjust `crawler.max_pages` in config
   - Increase `crawler.delay_between_requests`
   - Use `--headless` mode in production

3. **Scheduling Optimization**
   - Adjust cron schedule based on listing frequency
   - Consider peak times for better results

## Security

### 1. Access Control
```bash
# Restrict file permissions
chmod 600 .env
chmod 755 main.py

# Set directory permissions
chmod 750 /home/kleinanzeigen/Kleinanzeige-Buecherwurm
```

### 2. Network Security
- Use firewall to restrict database access
- Consider VPN for remote access
- Regularly update system packages

### 3. Data Protection
- Regular database backups
- Encrypt sensitive configuration
- Monitor for unauthorized access

## Scaling

### Multiple Instances
- Use different search locations
- Implement load balancing
- Coordinate via shared database

### Cloud Deployment
- Docker containerization
- Kubernetes orchestration
- Managed database services

## Support

For issues and questions:
1. Check logs for error messages
2. Review configuration settings
3. Test individual components
4. Consult documentation

Remember to respect kleinanzeigen.de terms of service and implement reasonable rate limiting.