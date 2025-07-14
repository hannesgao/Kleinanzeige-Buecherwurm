#!/bin/bash
# Docker deployment script for Kleinanzeigen Crawler
# Handles containerized deployment with docker-compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check Docker installation
check_docker() {
    log "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        # Check for docker compose (v2)
        if ! docker compose version &> /dev/null; then
            error "Docker Compose is not installed. Please install Docker Compose."
        else
            # Use docker compose v2
            DOCKER_COMPOSE="docker compose"
        fi
    else
        DOCKER_COMPOSE="docker-compose"
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running. Please start Docker."
    fi
    
    log "Docker and Docker Compose are installed and running"
}

# Create Docker environment file
create_docker_env() {
    log "Creating Docker environment configuration..."
    
    if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
        warning ".env file not found. Creating from template..."
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        warning "Please edit .env file with your configuration before running containers"
        exit 1
    fi
    
    # Create .env.docker with Docker-specific overrides
    cat > "$PROJECT_ROOT/.env.docker" <<EOF
# Docker-specific environment variables
COMPOSE_PROJECT_NAME=kleinanzeigen-crawler

# Database configuration for Docker
DB_HOST=postgres
DB_PORT=5432

# Redis configuration (if using for caching)
REDIS_HOST=redis
REDIS_PORT=6379

# Chrome configuration
CHROME_OPTIONS=--no-sandbox,--disable-dev-shm-usage,--disable-gpu
EOF
    
    log "Docker environment created"
}

# Create docker-compose.override.yml for development
create_compose_override() {
    log "Creating docker-compose override file..."
    
    cat > "$PROJECT_ROOT/docker-compose.override.yml" <<EOF
version: '3.8'

services:
  crawler:
    volumes:
      - ./src:/app/src:ro
      - ./config.yaml:/app/config.yaml:ro
      - ./logs:/app/logs
      - ./data:/app/data
    environment:
      - DEBUG=True
    command: python3 main.py --test --headless

  postgres:
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_PASSWORD=development_password
EOF
    
    log "Override file created for development"
}

# Update main docker-compose.yml
update_docker_compose() {
    log "Updating docker-compose.yml..."
    
    cat > "$PROJECT_ROOT/docker-compose.yml" <<EOF
version: '3.8'

services:
  crawler:
    build:
      context: .
      dockerfile: deployment/Dockerfile
    container_name: kleinanzeigen-crawler
    restart: unless-stopped
    depends_on:
      - postgres
    env_file:
      - .env
      - .env.docker
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - crawler-network
    healthcheck:
      test: ["CMD", "python3", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:14-alpine
    container_name: kleinanzeigen-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=kleinanzeigen_crawler
      - POSTGRES_USER=kleinanzeigen
      - POSTGRES_PASSWORD=\${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./database/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql:ro
    networks:
      - crawler-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U kleinanzeigen -d kleinanzeigen_crawler"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: kleinanzeigen-redis
    restart: unless-stopped
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    networks:
      - crawler-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: kleinanzeigen-nginx
    restart: unless-stopped
    ports:
      - "8080:80"
    volumes:
      - ./deployment/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./logs:/var/log/nginx
    depends_on:
      - crawler
    networks:
      - crawler-network

volumes:
  postgres-data:
    driver: local

networks:
  crawler-network:
    driver: bridge
EOF
    
    log "docker-compose.yml updated"
}

# Create nginx configuration
create_nginx_config() {
    log "Creating nginx configuration..."
    
    mkdir -p "$PROJECT_ROOT/deployment"
    
    cat > "$PROJECT_ROOT/deployment/nginx.conf" <<'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    sendfile on;
    keepalive_timeout 65;
    
    server {
        listen 80;
        server_name localhost;
        
        location / {
            root /usr/share/nginx/html;
            index index.html;
        }
        
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
        
        location /logs {
            alias /var/log/nginx;
            autoindex on;
            autoindex_exact_size off;
            autoindex_localtime on;
        }
    }
}
EOF
    
    log "Nginx configuration created"
}

# Build and start containers
start_containers() {
    log "Building and starting containers..."
    
    cd "$PROJECT_ROOT"
    
    # Build images
    info "Building Docker images..."
    $DOCKER_COMPOSE build --no-cache
    
    # Start containers
    info "Starting containers..."
    $DOCKER_COMPOSE up -d
    
    # Wait for services to be ready
    info "Waiting for services to be ready..."
    sleep 10
    
    # Check container status
    $DOCKER_COMPOSE ps
    
    log "Containers started successfully"
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring..."
    
    # Create monitoring script
    cat > "$PROJECT_ROOT/scripts/docker_monitor.sh" <<'EOF'
#!/bin/bash
# Docker monitoring script

echo "=== Docker Container Status ==="
docker-compose ps

echo -e "\n=== Container Resource Usage ==="
docker stats --no-stream

echo -e "\n=== Recent Logs ==="
docker-compose logs --tail=20 crawler

echo -e "\n=== Database Status ==="
docker-compose exec postgres pg_isready -U kleinanzeigen

echo -e "\n=== Crawler Health ==="
docker-compose exec crawler python3 tools/monitor.py --stats
EOF
    
    chmod +x "$PROJECT_ROOT/scripts/docker_monitor.sh"
    log "Monitoring script created"
}

# Show usage information
show_usage() {
    echo -e "\n${GREEN}=== Docker Deployment Complete! ===${NC}\n"
    
    echo "Container Management Commands:"
    echo "  Start:    $DOCKER_COMPOSE up -d"
    echo "  Stop:     $DOCKER_COMPOSE down"
    echo "  Logs:     $DOCKER_COMPOSE logs -f crawler"
    echo "  Status:   $DOCKER_COMPOSE ps"
    echo "  Monitor:  ./scripts/docker_monitor.sh"
    echo ""
    echo "Access Points:"
    echo "  Web UI:   http://localhost:8080"
    echo "  Database: localhost:5432"
    echo ""
    echo "Useful Commands:"
    echo "  Shell:    $DOCKER_COMPOSE exec crawler bash"
    echo "  DB Shell: $DOCKER_COMPOSE exec postgres psql -U kleinanzeigen"
    echo "  Rebuild:  $DOCKER_COMPOSE build --no-cache"
    echo ""
    echo "To run a one-time crawl:"
    echo "  $DOCKER_COMPOSE run --rm crawler python3 main.py --test"
}

# Main deployment flow
main() {
    echo "======================================"
    echo "Kleinanzeigen Crawler Docker Deploy"
    echo "======================================"
    echo ""
    
    # Check prerequisites
    check_docker
    
    # Create configurations
    create_docker_env
    update_docker_compose
    create_compose_override
    create_nginx_config
    
    # Ask about starting containers
    read -p "Start Docker containers now? (Y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        start_containers
        setup_monitoring
        show_usage
    else
        echo ""
        echo "Docker configuration created. To start manually:"
        echo "  cd $PROJECT_ROOT"
        echo "  $DOCKER_COMPOSE up -d"
    fi
}

# Run main function
main "$@"