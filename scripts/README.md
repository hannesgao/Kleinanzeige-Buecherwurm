# Kleinanzeigen Crawler - Installation and Deployment Scripts

This directory contains automated scripts for installing, configuring, and deploying the Kleinanzeigen Crawler.

## 📋 Available Scripts

### 1. `quick_start.sh` - Quick Start (Development)
**Purpose**: Fastest way to get started with minimal configuration
```bash
./scripts/quick_start.sh
```
- ✅ Installs basic dependencies
- ✅ Sets up PostgreSQL with default password
- ✅ Creates .env file
- ✅ Runs a test crawl
- ⏱️ Time: ~5 minutes

### 2. `install_complete.sh` - Complete Installation
**Purpose**: Full installation with all dependencies and proper configuration
```bash
./scripts/install_complete.sh
```
- ✅ Detects OS and installs system packages
- ✅ Installs Google Chrome
- ✅ Sets up PostgreSQL with secure password
- ✅ Configures Python environment
- ✅ Creates all necessary directories
- ✅ Verifies installation
- ⏱️ Time: ~10-15 minutes

### 3. `setup_database.sh` - Database Management
**Purpose**: Database setup, backup, restore, and management
```bash
# Setup new database
./scripts/setup_database.sh setup

# Backup database
./scripts/setup_database.sh backup

# Restore from backup
./scripts/setup_database.sh restore -f backup.sql

# Check database status
./scripts/setup_database.sh status

# Reset database (CAUTION!)
./scripts/setup_database.sh reset
```

### 4. `deploy_production.sh` - Production Deployment
**Purpose**: Deploy to production with systemd service
```bash
./scripts/deploy_production.sh
```
- ✅ Creates systemd service
- ✅ Sets up log rotation
- ✅ Creates monitoring scripts
- ✅ Configures automatic backups
- ✅ Sets resource limits
- ✅ Enables auto-start on boot
- ⏱️ Time: ~5 minutes

### 5. `docker_deploy.sh` - Docker Deployment
**Purpose**: Deploy using Docker containers
```bash
./scripts/docker_deploy.sh
```
- ✅ Creates docker-compose configuration
- ✅ Sets up PostgreSQL container
- ✅ Adds Redis for caching
- ✅ Includes Nginx reverse proxy
- ✅ Creates monitoring tools
- ⏱️ Time: ~10 minutes

## 🚀 Recommended Installation Flow

### For Development:
```bash
# Option 1: Quick start (fastest)
./scripts/quick_start.sh

# Option 2: Complete setup (recommended)
./scripts/install_complete.sh
```

### For Production:
```bash
# Step 1: Complete installation
./scripts/install_complete.sh

# Step 2: Configure .env file
nano .env

# Step 3: Deploy to production
./scripts/deploy_production.sh
```

### For Docker:
```bash
# Option 1: If already installed locally
./scripts/docker_deploy.sh

# Option 2: Fresh Docker deployment
git clone https://github.com/hannesgao/Kleinanzeige-Buecherwurm.git
cd Kleinanzeige-Buecherwurm
./scripts/docker_deploy.sh
```

## 📝 Script Details

### Environment Variables
All scripts respect the following environment variables:
- `PROJECT_ROOT`: Override project root directory
- `SKIP_DEPS`: Skip dependency installation
- `FORCE_INSTALL`: Force reinstallation of components

### Logging
All scripts create log files:
- Installation: `install.log`
- Deployment: `deploy.log`
- Database operations: Logged to stdout

### Error Handling
- All scripts use `set -e` to exit on errors
- Colored output for better readability
- Confirmation prompts for destructive actions
- Automatic rollback on critical failures

## 🔧 Customization

### Custom Database Settings
```bash
./scripts/setup_database.sh setup \
  --host localhost \
  --port 5432 \
  --database my_crawler \
  --user my_user
```

### Custom Installation Path
```bash
PROJECT_ROOT=/opt/crawler ./scripts/install_complete.sh
```

### Skip Confirmation Prompts
```bash
yes | ./scripts/quick_start.sh
```

## 🐛 Troubleshooting

### Permission Denied
```bash
chmod +x scripts/*.sh
```

### PostgreSQL Connection Failed
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database exists
./scripts/setup_database.sh status
```

### Python Package Installation Failed
```bash
# For system-managed Python
pip3 install --user -r requirements.txt

# For restricted environments
pip3 install --break-system-packages -r requirements.txt
```

### Service Won't Start
```bash
# Check logs
sudo journalctl -u kleinanzeigen-crawler -n 50

# Check service status
sudo systemctl status kleinanzeigen-crawler
```

## 🔐 Security Notes

1. **Database Passwords**: 
   - Automatically generated and stored in `.db_credentials`
   - File permissions set to 600 (owner-only)

2. **Environment Files**:
   - `.env` file permissions set to 600
   - Never commit `.env` to version control

3. **Systemd Service**:
   - Runs as non-root user
   - Resource limits enforced
   - Restricted file system access

## 📊 Post-Installation

After successful installation:

1. **Test the crawler**:
   ```bash
   python3 main.py --test --headless
   ```

2. **Monitor performance**:
   ```bash
   python3 tools/monitor.py --all
   ```

3. **Check logs**:
   ```bash
   tail -f logs/crawler_*.log
   ```

4. **Backup database**:
   ```bash
   ./scripts/setup_database.sh backup
   ```

## 🤝 Contributing

When adding new scripts:
1. Follow the existing naming convention
2. Use the same color scheme for output
3. Include proper error handling
4. Add usage information with `--help`
5. Update this README

## 📄 License

These scripts are part of the Kleinanzeigen Crawler project and are distributed under the MIT License.