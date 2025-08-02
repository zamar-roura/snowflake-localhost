.# Snowflake Localhost Proxy - Makefile
# Usage: make <target>

# Variables
DOCKER_COMPOSE = docker-compose
PROJECT_NAME = snowflake-localhost
API_URL = http://localhost:4566
DB_URL = localhost:5432

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
BLUE = \033[0;34m
NC = \033[0m # No Color

# Default target
.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)Snowflake Localhost Proxy - Available Commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

.PHONY: start
start: ## Start all services (PostgreSQL + Flask API)
	@echo "$(BLUE)🚀 Starting Snowflake Localhost Proxy...$(NC)"
	@echo "$(YELLOW)Checking if Docker is running...$(NC)"
	@if ! docker info > /dev/null 2>&1; then \
		echo "$(RED)❌ Docker is not running. Please start Docker and try again.$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)🛑 Stopping existing containers...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(YELLOW)🔧 Starting PostgreSQL and Flask API...$(NC)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(YELLOW)⏳ Waiting for services to be ready...$(NC)"
	@sleep 10
	@echo "$(YELLOW)🔍 Checking service status...$(NC)"
	@$(DOCKER_COMPOSE) ps
	@echo "$(YELLOW)🏥 Testing health endpoint...$(NC)"
	@curl -s $(API_URL)/health || echo "$(RED)❌ Health check failed$(NC)"
	@echo ""
	@echo "$(GREEN)✅ Services started successfully!$(NC)"
	@echo ""
	@echo "$(BLUE)📊 Available endpoints:$(NC)"
	@echo "   - Health check: $(API_URL)/health"
	@echo "   - PostgreSQL: $(DB_URL)"
	@echo ""
	@echo "$(BLUE)🧪 To run tests:$(NC)"
	@echo "   make test"
	@echo ""
	@echo "$(BLUE)📝 To view logs:$(NC)"
	@echo "   make logs"
	@echo ""
	@echo "$(BLUE)🛑 To stop services:$(NC)"
	@echo "   make stop"

.PHONY: stop
stop: ## Stop all services
	@echo "$(YELLOW)🛑 Stopping all services...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ Services stopped successfully!$(NC)"

.PHONY: restart
restart: stop start ## Restart all services

.PHONY: status
status: ## Show status of all services
	@echo "$(BLUE)📊 Service Status:$(NC)"
	@$(DOCKER_COMPOSE) ps

.PHONY: logs
logs: ## Show logs from all services
	@echo "$(BLUE)📝 Service Logs:$(NC)"
	@$(DOCKER_COMPOSE) logs -f

.PHONY: logs-api
logs-api: ## Show logs from Flask API only
	@echo "$(BLUE)📝 Flask API Logs:$(NC)"
	@$(DOCKER_COMPOSE) logs -f snowflake-proxy

.PHONY: logs-db
logs-db: ## Show logs from PostgreSQL only
	@echo "$(BLUE)📝 PostgreSQL Logs:$(NC)"
	@$(DOCKER_COMPOSE) logs -f postgres

.PHONY: test
test: ## Run comprehensive test suite
	@echo "$(BLUE)🧪 Running Snowflake Localhost Proxy Tests$(NC)"
	@echo "$(YELLOW)Make sure the Docker containers are running: make start$(NC)"
	@echo "$(YELLOW)==================================================$(NC)"
	@python test_local_snowflake.py

.PHONY: test-example
test-example: ## Run example usage test
	@echo "$(BLUE)🧪 Running Example Usage Test$(NC)"
	@echo "$(YELLOW)Make sure the Docker containers are running: make start$(NC)"
	@echo "$(YELLOW)==================================================$(NC)"
	@python example_usage.py

.PHONY: health
health: ## Test health endpoint
	@echo "$(BLUE)🏥 Testing health endpoint...$(NC)"
	@curl -s $(API_URL)/health || echo "$(RED)❌ Health check failed$(NC)"

.PHONY: clean
clean: ## Remove all containers, networks, and volumes
	@echo "$(YELLOW)🧹 Cleaning up all Docker resources...$(NC)"
	@$(DOCKER_COMPOSE) down -v --remove-orphans
	@echo "$(GREEN)✅ Cleanup completed!$(NC)"

.PHONY: build
build: ## Build Docker images
	@echo "$(BLUE)🔨 Building Docker images...$(NC)"
	@$(DOCKER_COMPOSE) build
	@echo "$(GREEN)✅ Build completed!$(NC)"

.PHONY: rebuild
rebuild: clean build start ## Rebuild and restart all services

.PHONY: shell-api
shell-api: ## Open shell in Flask API container
	@echo "$(BLUE)🐍 Opening shell in Flask API container...$(NC)"
	@$(DOCKER_COMPOSE) exec snowflake-proxy /bin/bash

.PHONY: shell-db
shell-db: ## Open shell in PostgreSQL container
	@echo "$(BLUE)🐍 Opening shell in PostgreSQL container...$(NC)"
	@$(DOCKER_COMPOSE) exec postgres /bin/bash

.PHONY: db-connect
db-connect: ## Connect to PostgreSQL database
	@echo "$(BLUE)🗄️ Connecting to PostgreSQL database...$(NC)"
	@$(DOCKER_COMPOSE) exec postgres psql -U snowflake_user -d snowflake_local

.PHONY: install-deps
install-deps: ## Install Python dependencies locally
	@echo "$(BLUE)📦 Installing Python dependencies...$(NC)"
	@pip install -r requirements.txt
	@echo "$(GREEN)✅ Dependencies installed!$(NC)"

.PHONY: lint
lint: ## Run code linting (if flake8 is available)
	@echo "$(BLUE)🔍 Running code linting...$(NC)"
	@if command -v flake8 >/dev/null 2>&1; then \
		find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" | xargs flake8; \
	else \
		echo "$(YELLOW)flake8 not found. Install with: pip install flake8$(NC)"; \
	fi

.PHONY: format
format: ## Format Python code (if black is available)
	@echo "$(BLUE)🎨 Formatting Python code...$(NC)"
	@if command -v black >/dev/null 2>&1; then \
		find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" | xargs black; \
	else \
		echo "$(YELLOW)black not found. Install with: pip install black$(NC)"; \
	fi

.PHONY: debug
debug: ## Start services in debug mode (show logs)
	@echo "$(BLUE)🐛 Starting services in debug mode...$(NC)"
	@$(DOCKER_COMPOSE) down
	@$(DOCKER_COMPOSE) up

.PHONY: api-test
api-test: ## Test API endpoints manually
	@echo "$(BLUE)🧪 Testing API endpoints...$(NC)"
	@echo "$(YELLOW)Testing health endpoint:$(NC)"
	@curl -s $(API_URL)/health | jq . || curl -s $(API_URL)/health
	@echo ""
	@echo "$(YELLOW)Testing connection creation:$(NC)"
	@curl -s -X POST $(API_URL)/v1/connection \
		-H "Content-Type: application/json" \
		-d '{"user":"test","password":"test","account":"localhost"}' | jq . || \
	curl -s -X POST $(API_URL)/v1/connection \
		-H "Content-Type: application/json" \
		-d '{"user":"test","password":"test","account":"localhost"}'

.PHONY: monitor
monitor: ## Monitor resource usage
	@echo "$(BLUE)📊 Monitoring resource usage...$(NC)"
	@echo "$(YELLOW)Container resource usage:$(NC)"
	@docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
	@echo ""
	@echo "$(YELLOW)Disk usage:$(NC)"
	@docker system df

.PHONY: backup
backup: ## Create database backup
	@echo "$(BLUE)💾 Creating database backup...$(NC)"
	@mkdir -p backups
	@$(DOCKER_COMPOSE) exec postgres pg_dump -U snowflake_user snowflake_local > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Backup created in backups/ directory!$(NC)"

.PHONY: restore
restore: ## Restore database from backup (usage: make restore BACKUP_FILE=backups/backup_20231201_120000.sql)
	@echo "$(BLUE)📥 Restoring database from backup...$(NC)"
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "$(RED)❌ Please specify BACKUP_FILE parameter$(NC)"; \
		echo "Usage: make restore BACKUP_FILE=backups/backup_20231201_120000.sql"; \
		exit 1; \
	fi
	@if [ ! -f "$(BACKUP_FILE)" ]; then \
		echo "$(RED)❌ Backup file $(BACKUP_FILE) not found$(NC)"; \
		exit 1; \
	fi
	@$(DOCKER_COMPOSE) exec -T postgres psql -U snowflake_user -d snowflake_local < $(BACKUP_FILE)
	@echo "$(GREEN)✅ Database restored successfully!$(NC)"

.PHONY: reset-db
reset-db: ## Reset database (drop and recreate)
	@echo "$(YELLOW)⚠️  This will delete all data! Are you sure? [y/N]$(NC)"
	@read -p " " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(BLUE)🔄 Resetting database...$(NC)"; \
		$(DOCKER_COMPOSE) exec postgres psql -U snowflake_user -d snowflake_local -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"; \
		$(DOCKER_COMPOSE) exec postgres psql -U snowflake_user -d snowflake_local < init-scripts/01-init.sql; \
		echo "$(GREEN)✅ Database reset completed!$(NC)"; \
	else \
		echo "$(YELLOW)Operation cancelled.$(NC)"; \
	fi

# Development targets
.PHONY: dev-setup
dev-setup: install-deps start ## Setup development environment
	@echo "$(GREEN)✅ Development environment ready!$(NC)"

.PHONY: dev-test
dev-test: test test-example ## Run all tests

.PHONY: dev-clean
dev-clean: clean ## Clean development environment

# Quick shortcuts
.PHONY: up
up: start ## Alias for start

.PHONY: down
down: stop ## Alias for stop

.PHONY: ps
ps: status ## Alias for status

# Show help by default
.DEFAULT_GOAL := help 