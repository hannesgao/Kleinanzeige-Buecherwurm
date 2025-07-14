# Project Structure - Kleinanzeige Bücherwurm

## 📁 Complete Directory Structure

```
Kleinanzeige-Buecherwurm/
├── README.md                          # Main project documentation
├── CLAUDE.md                          # Claude Code integration guide
├── LICENSE                            # MIT License
├── setup.py                           # Python package setup
├── requirements.txt                   # Python dependencies
├── main.py                           # Main entry point
├── config.yaml                       # Default configuration
├── .env.example                      # Environment variables template
├── .gitignore                        # Git ignore rules
│
├── src/                              # Source code
│   ├── __init__.py
│   ├── scraper/                      # Web scraping components
│   │   ├── __init__.py
│   │   ├── crawler.py                # Main Selenium crawler
│   │   └── parser.py                 # HTML parsing utilities
│   ├── models/                       # Database models
│   │   ├── __init__.py
│   │   ├── base.py                   # SQLAlchemy base classes
│   │   ├── book_listing.py           # Book listing model
│   │   └── crawl_session.py          # Crawl session model
│   ├── config/                       # Configuration management
│   │   ├── __init__.py
│   │   ├── config_loader.py          # YAML config loader
│   │   └── database.py               # Database connection manager
│   └── utils/                        # Utility functions
│       ├── __init__.py
│       ├── logger.py                 # Logging configuration
│       ├── scheduler.py              # Task scheduling
│       ├── notifications.py          # Email notifications
│       ├── retry.py                  # Retry decorators
│       └── error_handler.py          # Error handling utilities
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── conftest.py                   # Pytest configuration
│   ├── run_tests.py                  # Test runner script
│   ├── config-test.yaml              # Test configuration
│   ├── unit/                         # Unit tests
│   │   ├── __init__.py
│   │   ├── test_config.py
│   │   ├── test_parser.py
│   │   ├── test_retry.py
│   │   ├── test_error_handler.py
│   │   └── test_notifications.py
│   ├── integration/                  # Integration tests
│   │   ├── __init__.py
│   │   ├── test_components.py
│   │   ├── test_database.py
│   │   └── test_complete.py
│   └── functional/                   # Functional tests
│       ├── __init__.py
│       ├── test_production_crawler.py
│       └── test_end_to_end.py
│
├── database/                         # Database related files
│   ├── schema.sql                    # PostgreSQL schema
│   └── migrations/                   # Database migrations (future)
│
├── config/                           # Configuration examples
│   ├── config-production.yaml        # Production configuration
│   ├── config-development.yaml       # Development configuration
│   └── config-testing.yaml          # Testing configuration
│
├── tools/                            # Development and management tools
│   ├── install.sh                    # Installation script
│   ├── check_setup.py                # Environment verification
│   └── monitor.py                    # Monitoring and statistics
│
├── deployment/                       # Deployment configurations
│   ├── docker-compose.yml            # Docker Compose setup
│   ├── Dockerfile                    # Docker image definition
│   └── systemd-service.service       # Systemd service file
│
├── docs/                            # Documentation
│   ├── PROJECT_STRUCTURE.md         # This file
│   ├── DEPLOYMENT.md                # Deployment guide
│   └── SUMMARY.md                   # Project summary
│
└── logs/                            # Application logs (created at runtime)
```

## 📋 File Descriptions

### Core Application Files

- **`main.py`**: Main entry point with CLI interface
- **`config.yaml`**: Default configuration file
- **`.env.example`**: Template for environment variables
- **`requirements.txt`**: Python dependencies list
- **`setup.py`**: Package installation configuration

### Source Code (`src/`)

#### Scraper Module (`src/scraper/`)
- **`crawler.py`**: Main Selenium-based crawler with Chrome automation
- **`parser.py`**: BeautifulSoup-based HTML parser for listing extraction

#### Models Module (`src/models/`)
- **`base.py`**: SQLAlchemy base classes and mixins
- **`book_listing.py`**: Database model for book listings
- **`crawl_session.py`**: Database model for crawl sessions

#### Config Module (`src/config/`)
- **`config_loader.py`**: YAML configuration loader with environment variable support
- **`database.py`**: Database connection and session management

#### Utils Module (`src/utils/`)
- **`logger.py`**: Logging configuration and setup
- **`scheduler.py`**: Cron-based task scheduling
- **`notifications.py`**: Email notification system
- **`retry.py`**: Retry decorators with exponential backoff
- **`error_handler.py`**: Centralized error handling

### Test Suite (`tests/`)

#### Unit Tests (`tests/unit/`)
- **`test_config.py`**: Configuration loading tests
- **`test_parser.py`**: HTML parsing tests
- **`test_retry.py`**: Retry mechanism tests
- **`test_error_handler.py`**: Error handling tests
- **`test_notifications.py`**: Notification system tests

#### Integration Tests (`tests/integration/`)
- **`test_components.py`**: Component integration tests
- **`test_database.py`**: Database integration tests
- **`test_complete.py`**: Complete system integration tests

#### Functional Tests (`tests/functional/`)
- **`test_production_crawler.py`**: Production environment tests
- **`test_end_to_end.py`**: End-to-end workflow tests

### Configuration (`config/`)
- **`config-production.yaml`**: Production-optimized configuration
- **`config-development.yaml`**: Development configuration with debugging
- **`config-testing.yaml`**: Testing configuration with minimal settings

### Tools (`tools/`)
- **`install.sh`**: Automated installation script
- **`check_setup.py`**: Environment and dependency verification
- **`monitor.py`**: Monitoring, statistics, and maintenance

### Deployment (`deployment/`)
- **`docker-compose.yml`**: Multi-container Docker setup
- **`Dockerfile`**: Container image definition
- **`systemd-service.service`**: Linux service configuration

### Documentation (`docs/`)
- **`PROJECT_STRUCTURE.md`**: This file - project structure documentation
- **`DEPLOYMENT.md`**: Deployment guide and instructions
- **`SUMMARY.md`**: Project summary and completion status

### Database (`database/`)
- **`schema.sql`**: PostgreSQL database schema
- **`migrations/`**: Directory for future database migrations

## 🔧 Key Features by Directory

### Source Code Organization
- **Modular Design**: Clear separation of concerns
- **Type Hints**: Comprehensive type annotations
- **Error Handling**: Robust error handling throughout
- **Logging**: Structured logging with rotation
- **Configuration**: Flexible YAML-based configuration

### Test Organization
- **Three-Tier Testing**: Unit, Integration, and Functional tests
- **Pytest Framework**: Modern testing with fixtures
- **Mock Support**: Comprehensive mocking for external dependencies
- **Coverage**: Test coverage reporting
- **CI/CD Ready**: Suitable for continuous integration

### Configuration Management
- **Environment Specific**: Separate configs for different environments
- **Environment Variables**: Secure handling of sensitive data
- **Validation**: Configuration validation and error reporting
- **Flexibility**: Easy customization for different use cases

### Deployment Options
- **Docker**: Containerized deployment
- **Systemd**: Linux service integration
- **Manual**: Traditional installation
- **Cloud**: Ready for cloud deployment

## 🚀 Usage Patterns

### Development Workflow
1. **Setup**: `./tools/install.sh`
2. **Test**: `python tests/run_tests.py --unit`
3. **Develop**: Edit source code in `src/`
4. **Test**: `python tests/run_tests.py --integration`
5. **Deploy**: Use configurations in `config/` and `deployment/`

### Testing Workflow
1. **Quick Tests**: `python tests/run_tests.py --quick`
2. **Unit Tests**: `python tests/run_tests.py --unit`
3. **Integration**: `python tests/run_tests.py --integration`
4. **Functional**: `python tests/run_tests.py --functional`
5. **Coverage**: `python tests/run_tests.py --coverage`

### Deployment Workflow
1. **Environment Check**: `python tools/check_setup.py`
2. **Configuration**: Copy and edit config files
3. **Database**: `python main.py --init-db`
4. **Test**: `python main.py --test --headless`
5. **Deploy**: Choose from Docker, systemd, or manual deployment

## 📊 Metrics and Monitoring

### Built-in Monitoring
- **Database Statistics**: Crawl sessions and listing counts
- **Performance Metrics**: Processing times and success rates
- **Error Tracking**: Comprehensive error logging
- **System Health**: Resource usage monitoring

### Log Management
- **Structured Logging**: JSON-formatted logs
- **Log Rotation**: Automatic log file rotation
- **Log Retention**: Configurable retention policies
- **Log Analysis**: Tools for log analysis and troubleshooting

This structure provides a solid foundation for a production-ready web scraping application with proper separation of concerns, comprehensive testing, and flexible deployment options.