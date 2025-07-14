# Kleinanzeige-Bücherwurm

A fully-implemented Python web crawler for finding free antique book collections on Kleinanzeigen.de within a 20km radius of Karlsruhe.

## ✨ Features

- 🔍 **Automated Search**: Intelligent search for free antique books and collections
- 🌐 **Selenium Automation**: Chrome browser simulation with anti-detection measures
- 📊 **PostgreSQL Storage**: Robust database with deduplication and tracking
- 📧 **Email Notifications**: Rich HTML email alerts for new findings
- ⏰ **Scheduled Crawling**: Configurable cron-based scheduling
- 🔧 **YAML Configuration**: Flexible configuration with environment variables
- 🛡️ **Error Handling**: Comprehensive retry logic and error recovery
- 🧪 **Test Mode**: Safe testing with limited listings
- 📝 **Logging**: Structured logging with rotation and retention

## 🚀 Complete Setup Guide

### System Requirements
- **OS**: Ubuntu 20.04+ / Debian 11+ (or similar Linux distribution)
- **Python**: 3.8 or higher
- **PostgreSQL**: 12.0 or higher
- **Chrome/Chromium**: Latest stable version
- **RAM**: 8GB minimum (16GB recommended for production)
- **Disk Space**: 10GB minimum
- **Network**: Stable internet connection

### Step 1: Install System Dependencies

#### Ubuntu/Debian:
```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install -y python3 python3-pip python3-dev

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install Chrome browser
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# Install additional system dependencies
sudo apt install -y build-essential libpq-dev git
```

#### RHEL/CentOS/Fedora:
```bash
# Install Python and pip
sudo dnf install -y python3 python3-pip python3-devel

# Install PostgreSQL
sudo dnf install -y postgresql postgresql-server postgresql-contrib

# Install Chrome browser
sudo dnf install -y fedora-workstation-repositories
sudo dnf config-manager --set-enabled google-chrome
sudo dnf install -y google-chrome-stable

# Install additional dependencies
sudo dnf install -y gcc gcc-c++ postgresql-devel git
```

### Step 2: Set Up PostgreSQL Database

```bash
# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt, create database and user:
CREATE USER kleinanzeigen WITH PASSWORD 'your-secure-password';
CREATE DATABASE kleinanzeigen_crawler OWNER kleinanzeigen;
GRANT ALL PRIVILEGES ON DATABASE kleinanzeigen_crawler TO kleinanzeigen;
\q

# Exit postgres user
exit
```

### Step 3: Clone and Configure the Project

```bash
# Clone the repository
git clone https://github.com/hannesgao/Kleinanzeige-Buecherwurm.git
cd Kleinanzeige-Buecherwurm

# Create .env file from template
cp .env.example .env

# Edit .env file with your configuration
nano .env
```

Configure the following in `.env`:
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=kleinanzeigen_crawler
DB_USER=kleinanzeigen
DB_PASSWORD=your-secure-password

# Email Configuration (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFICATION_EMAIL=recipient@example.com

# Optional: Debug mode
DEBUG=False
```

### Step 4: Install Python Dependencies

#### Option A: System-wide installation (requires root)
```bash
# Install dependencies system-wide
sudo pip3 install --break-system-packages -r requirements.txt
```

#### Option B: User installation (recommended)
```bash
# Install dependencies for current user only
pip3 install --user -r requirements.txt

# Add local bin to PATH if needed
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### Option C: Virtual environment (if preferred)
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Verify Installation

```bash
# Run setup verification
python3 tools/check_setup.py

# Expected output:
# ✅ Python version supported
# ✅ All required packages installed
# ✅ Chrome browser found
# ✅ Database configuration found
# ✅ File permissions correct
# ✅ Disk space sufficient
```

### Step 6: Initialize Database

```bash
# Create database tables
python3 main.py --init-db

# Verify database setup
psql -h localhost -U kleinanzeigen -d kleinanzeigen_crawler -c "\dt"
```

### Step 7: Test the Crawler

```bash
# Run test crawl (limited to 5 listings)
python3 main.py --test --headless

# Check logs
tail -f logs/crawler_*.log
```

### Step 8: Production Setup

#### Option A: Systemd Service (Recommended)
```bash
# Copy service file
sudo cp deployment/systemd-service.service /etc/systemd/system/kleinanzeigen-crawler.service

# Edit service file to match your setup
sudo nano /etc/systemd/system/kleinanzeigen-crawler.service

# Update paths and user in the service file:
# User=your-username
# WorkingDirectory=/path/to/Kleinanzeige-Buecherwurm
# ExecStart=/usr/bin/python3 /path/to/Kleinanzeige-Buecherwurm/main.py --schedule --headless

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable kleinanzeigen-crawler
sudo systemctl start kleinanzeigen-crawler

# Check service status
sudo systemctl status kleinanzeigen-crawler
```

#### Option B: Docker Deployment
```bash
# Build Docker image
docker build -t kleinanzeigen-crawler .

# Run with docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

#### Option C: Cron Job
```bash
# Add to crontab
crontab -e

# Add this line to run every 6 hours
0 */6 * * * cd /path/to/Kleinanzeige-Buecherwurm && /usr/bin/python3 main.py --headless >> logs/cron.log 2>&1
```

### Step 9: Monitoring and Maintenance

```bash
# View crawler statistics
python3 tools/monitor.py --stats

# View recent sessions
python3 tools/monitor.py --sessions 10

# View system status
python3 tools/monitor.py --system

# Clean up old data (older than 30 days)
python3 tools/monitor.py --cleanup 30

# View all monitoring info
python3 tools/monitor.py --all
```

### Troubleshooting

#### Common Issues:

1. **Permission Denied Error**
```bash
# Fix file permissions
chmod 600 .env
chmod 644 config.yaml main.py
chmod +x tools/*.sh tools/*.py tests/run_tests.py
```

2. **Database Connection Failed**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -h localhost -U kleinanzeigen -d kleinanzeigen_crawler

# Check firewall
sudo ufw status
```

3. **Chrome Driver Issues**
```bash
# Verify Chrome installation
google-chrome --version

# The webdriver-manager package should handle driver automatically
# If issues persist, check Chrome version compatibility
```

4. **Missing Python Packages**
```bash
# For externally-managed environments (Ubuntu 23.04+):
sudo apt install python3-selenium python3-bs4 python3-sqlalchemy python3-psycopg2

# Or use --break-system-packages flag
pip3 install --break-system-packages -r requirements.txt
```

5. **Email Notifications Not Working**
```bash
# For Gmail, create App Password:
# 1. Go to Google Account settings
# 2. Security → 2-Step Verification → App passwords
# 3. Generate password for "Mail"
# 4. Use this password in .env
```

### Performance Optimization

1. **Database Indexing**
```sql
-- Already included in schema.sql, but verify:
psql -h localhost -U kleinanzeigen -d kleinanzeigen_crawler
\di
```

2. **Log Rotation**
```bash
# Logs are automatically rotated (configured in src/utils/logger.py)
# Manual cleanup if needed:
find logs/ -name "*.log" -mtime +30 -delete
```

3. **Resource Limits**
```bash
# For systemd service, edit the service file:
# MemoryMax=2G
# CPUQuota=50%
```

## 🎯 Usage

### Command Line Options

```bash
# Run once (interactive mode)
python3 main.py

# Run in headless mode
python3 main.py --headless

# Test mode (limit to 5 listings)
python3 main.py --test

# Scheduled mode (runs every 6 hours)
python3 main.py --schedule

# Custom configuration
python3 main.py --config custom-config.yaml
```

### Configuration

Edit `config.yaml` for:

**Search Parameters**:
- Location: Karlsruhe (customizable)
- Radius: 20km (adjustable)
- Keywords: "sammlung", "konvolut", "nachlass"
- Price filter: Free items only

**Crawler Settings**:
- Headless mode toggle
- Request delays (anti-detection)
- Retry attempts and backoff
- Page load timeouts

**Database & Notifications**:
- PostgreSQL connection
- Email SMTP configuration
- Notification templates

## 📁 Project Structure

```
├── src/                    # Source code
│   ├── scraper/           # Web scraping components
│   ├── models/            # Database models
│   ├── config/            # Configuration management
│   └── utils/             # Utility functions
├── tests/                 # Complete test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── functional/        # Functional tests
├── quality/               # Quality assurance
│   ├── audits/           # Security and code audits
│   ├── reports/          # Quality reports
│   └── testing/          # Testing tools
├── config/                # Configuration examples
├── tools/                 # Development tools
├── deployment/            # Deployment configurations
├── docs/                  # Documentation
├── database/              # Database schema
├── logs/                  # Application logs
├── config.yaml            # Main configuration
├── requirements.txt       # Dependencies
└── main.py               # Entry point
```

See [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for detailed structure documentation and [docs/PROJECT_REORGANIZATION_SUMMARY.md](docs/PROJECT_REORGANIZATION_SUMMARY.md) for reorganization details.

## 🔧 Development

### Running Tests
```bash
# Quick tests (recommended)
python3 tests/run_tests.py --quick

# All tests
python3 tests/run_tests.py --all

# Specific test types
python3 tests/run_tests.py --unit
python3 tests/run_tests.py --integration
python3 tests/run_tests.py --functional

# With coverage
python3 tests/run_tests.py --coverage

# Production tests
python3 tests/run_tests.py --production

# Project verification
python3 quality/testing/check_project.py
```

### Code Quality
```bash
# Format code
python3 -m black src/

# Type checking
python3 -m mypy src/

# Linting
python3 -m flake8 src/
```

### Database Operations
```bash
# Connect to PostgreSQL
psql -h localhost -d kleinanzeigen_crawler -U your_user

# View recent sessions
SELECT * FROM crawl_sessions ORDER BY start_time DESC LIMIT 10;

# Count active listings
SELECT COUNT(*) FROM book_listings WHERE is_active = TRUE;
```

### Monitoring
```bash
# View crawler statistics
python3 tools/monitor.py --stats

# View recent sessions
python3 tools/monitor.py --sessions 10

# View system status
python3 tools/monitor.py --system

# View all information
python3 tools/monitor.py --all
```

## 🛡️ Error Handling

The crawler includes robust error handling:

- **Retry Logic**: Exponential backoff for failed requests
- **Selenium Errors**: Handles stale elements, timeouts, session issues
- **Network Resilience**: Connection failures and timeouts
- **Database Safety**: Integrity constraints and connection pooling
- **Graceful Degradation**: Partial failures don't stop the entire session

## 📊 Monitoring

- **Session Tracking**: Each crawl session is logged with statistics
- **Listing History**: Track when listings were first/last seen
- **Error Reporting**: Comprehensive error logs with context
- **Performance Metrics**: Processing times and success rates

## ⚖️ Legal & Ethical

- **Public Data Only**: Scrapes publicly available listings
- **Rate Limiting**: Respectful delays between requests
- **Terms Compliance**: Follows robots.txt and reasonable usage
- **Data Privacy**: No personal data collection beyond public listings

## 🔍 Additional Information

### Security Best Practices

1. **Database Security**
   - Use strong passwords
   - Restrict database access to localhost only
   - Regular backups: `pg_dump kleinanzeigen_crawler > backup.sql`

2. **Email Security**
   - Use app-specific passwords, never your main password
   - Consider using a dedicated email account for notifications

3. **File Permissions**
   - Keep `.env` readable only by owner: `chmod 600 .env`
   - Never commit `.env` to version control

### Advanced Configuration

1. **Custom Search Parameters** (edit `config.yaml`):
```yaml
search:
  keywords:
    - "antiquariat"
    - "bücher sammlung"
    - "bibliothek auflösung"
  radius_km: 50  # Increase search radius
  max_listings_per_page: 50
```

2. **Notification Templates** (edit `config.yaml`):
```yaml
notifications:
  subject_template: "New books found: {count} listings"
  max_items_per_email: 20
```

3. **Performance Tuning**:
```yaml
crawler:
  page_load_timeout: 30
  delay_between_requests: [2, 5]  # Random delay between 2-5 seconds
  retry_attempts: 3
  retry_backoff_factor: 2
```

### Integration Examples

1. **Webhook Integration**:
```python
# Add to src/utils/notifications.py
def send_webhook(listings):
    webhook_url = os.getenv('WEBHOOK_URL')
    if webhook_url:
        requests.post(webhook_url, json={
            'listings': [l.to_dict() for l in listings]
        })
```

2. **Telegram Notifications**:
```python
# Add Telegram bot support
def send_telegram(message):
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if bot_token and chat_id:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(url, data={'chat_id': chat_id, 'text': message})
```

## 📈 Performance

- **Optimized Parsing**: BeautifulSoup with lxml parser
- **Connection Pooling**: Efficient database connections
- **Memory Management**: Proper cleanup of browser sessions
- **Resource Monitoring**: Automatic log rotation and cleanup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests and ensure code quality
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 👨‍💻 Author

**Hannes** | hannesgao.eth

---

*Built with Python, Selenium, PostgreSQL, and ❤️ for book lovers*