# Kleinanzeige-Bücherwurm

A Python-based web crawler for finding free antique book collections on Kleinanzeigen.de within a 20km radius of Karlsruhe.

## Features

- 🔍 Automated search for free antique books and collections
- 🌐 Selenium-based crawler with Chrome browser simulation
- 📊 PostgreSQL database for storing listings
- 📧 Email notifications for new finds
- ⏰ Scheduled crawling (configurable intervals)
- 🔧 Comprehensive configuration via YAML

## Prerequisites

- Python 3.8+
- PostgreSQL database
- Chrome browser
- ChromeDriver (auto-downloaded by webdriver-manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/hannesgao/Kleinanzeige-Buecherwurm.git
cd Kleinanzeige-Buecherwurm
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database and email credentials
```

5. Initialize the database:
```bash
python main.py --init-db
```

## Configuration

Edit `config.yaml` to customize:

- Search parameters (location, radius, keywords)
- Selenium settings (headless mode, timeouts)
- Database connection
- Email notifications
- Crawling schedule

## Usage

### Run once:
```bash
python main.py
```

### Run with scheduler:
```bash
python main.py --schedule
```

### Custom config file:
```bash
python main.py --config path/to/config.yaml
```

## Project Structure

```
├── src/
│   ├── scraper/        # Web scraping logic
│   ├── models/         # Database models
│   ├── config/         # Configuration management
│   └── utils/          # Utilities (logging, notifications)
├── database/           # Database schema
├── tests/              # Unit tests
├── logs/               # Application logs
├── config.yaml         # Main configuration
├── requirements.txt    # Python dependencies
└── main.py            # Entry point
```

## Development

### Running tests:
```bash
pytest
```

### Code formatting:
```bash
black src/
```

### Type checking:
```bash
mypy src/
```

## License

MIT License - see LICENSE file

## Author

Hannes | hannesgao.eth