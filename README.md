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

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL database
- Chrome browser
- 8GB+ RAM recommended

### Installation

1. **Clone and setup**:
```bash
git clone https://github.com/hannesgao/Kleinanzeige-Buecherwurm.git
cd Kleinanzeige-Buecherwurm
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your database and email credentials
```

4. **Initialize database**:
```bash
python main.py --init-db
```

5. **Test the crawler**:
```bash
python main.py --test --headless
```

## 🎯 Usage

### Command Line Options

```bash
# Run once (interactive mode)
python main.py

# Run in headless mode
python main.py --headless

# Test mode (limit to 5 listings)
python main.py --test

# Scheduled mode (runs every 6 hours)
python main.py --schedule

# Custom configuration
python main.py --config custom-config.yaml
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
├── src/
│   ├── scraper/
│   │   ├── crawler.py      # Main Selenium crawler
│   │   └── parser.py       # HTML parsing logic
│   ├── models/
│   │   ├── book_listing.py # Listing database model
│   │   └── crawl_session.py # Session tracking
│   ├── config/
│   │   ├── config_loader.py # YAML + env config
│   │   └── database.py     # Database manager
│   └── utils/
│       ├── logger.py       # Logging setup
│       ├── scheduler.py    # Cron scheduling
│       ├── notifications.py # Email notifications
│       ├── retry.py        # Retry decorators
│       └── error_handler.py # Error management
├── database/
│   └── schema.sql          # PostgreSQL schema
├── tests/                  # Unit tests
├── logs/                   # Application logs
├── config.yaml             # Main configuration
├── requirements.txt        # Dependencies
└── main.py                # Entry point
```

## 🔧 Development

### Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=src

# Specific test
pytest tests/test_parser.py -v
```

### Code Quality
```bash
# Format code
black src/

# Type checking
mypy src/

# Linting
flake8 src/
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

## 🔍 Troubleshooting

### Common Issues

1. **ChromeDriver**: Auto-managed by webdriver-manager
2. **Database Connection**: Check `.env` credentials
3. **Element Not Found**: HTML structure may have changed
4. **Email Notifications**: Verify SMTP settings and app passwords

### Debug Mode
```bash
# Enable debug logging
export DEBUG=True
python main.py --test
```

### Log Analysis
```bash
# View recent logs
tail -f logs/crawler_*.log

# Search for errors
grep -i error logs/crawler_*.log
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