# Snowflake Localhost Proxy

A local development environment that mimics Snowflake's API using PostgreSQL as the backend database. This project provides a Flask API layer that intercepts Snowflake connection calls and translates Snowflake SQL syntax to PostgreSQL-compatible SQL.

## Overview

This project creates a LocalStack-like environment for Snowflake development by:

1. **PostgreSQL Database**: Running a PostgreSQL container as the backend database
2. **Flask API Proxy**: A Flask application that intercepts Snowflake API calls
3. **SQL Translation**: Converting Snowflake-specific SQL syntax to PostgreSQL
4. **Connection Management**: Managing connections and sessions similar to Snowflake

## Project Structure

```
snowflake-localhost/
├── docker-compose.yml          # Docker services configuration
├── Dockerfile                  # Flask API container definition
├── requirements.txt            # Python dependencies
├── app/                       # Flask application
│   ├── app.py                 # Main Flask application
│   └── snowflake_proxy/       # Core proxy components
│       ├── connection_handler.py    # PostgreSQL connection management
│       ├── sql_translator.py       # SQL syntax translation
│       └── snowflake_local_client.py # Modified Snowflake client
├── init-scripts/              # PostgreSQL initialization
│   └── 01-init.sql           # Database setup script
├── test_local_snowflake.py    # Test script
└── README.md                  # This file
```

## Features

### ✅ Implemented
- **Connection Management**: Create and manage connections similar to Snowflake
- **Basic SQL Translation**: Convert common Snowflake syntax to PostgreSQL
- **Data Type Mapping**: Map Snowflake data types to PostgreSQL equivalents
- **Function Translation**: Translate Snowflake functions to PostgreSQL
- **Pandas Integration**: Support for pandas DataFrame operations
- **Parameter Binding**: Support for parameterized queries
- **Transaction Support**: Basic transaction management

### 🔄 Partially Implemented
- **MERGE Syntax**: Basic translation (needs enhancement)
- **Advanced Snowflake Features**: Some features need more sophisticated translation

### 📋 Planned
- **Stored Procedures**: Support for Snowflake stored procedures
- **User-Defined Functions**: Custom function translation
- **Advanced Data Types**: Full support for all Snowflake data types
- **Performance Optimization**: Query optimization and caching

## Quick Start

### 1. Start the Services

```bash
# Option 1: Using Makefile (recommended)
make start

# Option 2: Using shell script
./start.sh

# Check if services are running
make status
```

### 2. Test the Connection

```bash
# Test the health endpoint
curl http://localhost:4566/health
```

### 3. Run the Test Script

```bash
# Install dependencies (if running locally)
make install-deps

# Run the test script
make test

# Or run directly:
python test_local_snowflake.py
```

## Usage

### Using the Local Snowflake Client

```python
from app.snowflake_proxy.snowflake_local_client import SnowflakeLocalClient

# Create a client (similar to your original SnowflakePython)
client = SnowflakeLocalClient(
    user="snowflake_user",
    password="snowflake_password",
    account="localhost",
    warehouse="COMPUTE_WH",
    database="snowflake_local",
    schema="public"
)

# Execute queries (same interface as original)
result = client.execute_query("SELECT * FROM example_table LIMIT 5")

# Use pandas integration
df = client.pandas_execute_query("SELECT * FROM example_table")

# Get column information
columns = client.get_columns_info("example_table")

# Close the connection
client.close()
```

### API Endpoints

The Flask API provides the following endpoints:

- `GET /health` - Health check
- `POST /v1/connection` - Create a new connection
- `POST /v1/query` - Execute a query
- `DELETE /v1/connection/{connection_id}` - Close a connection

## SQL Translation Examples

| Snowflake Syntax | PostgreSQL Translation |
|------------------|----------------------|
| `NUMBER(10,2)` | `NUMERIC(10,2)` |
| `VARCHAR(255)` | `VARCHAR(255)` |
| `CURRENT_TIMESTAMP()` | `CURRENT_TIMESTAMP` |
| `UUID_STRING()` | `gen_random_uuid()` |
| `SELECT TOP 5` | `SELECT ... LIMIT 5` |
| `MERGE INTO` | `INSERT ... ON CONFLICT` |

## Quick Start Options

### Option 1: Makefile (Recommended)
The project includes a comprehensive Makefile for easy management:

```bash
# Show all available commands
make help

# Basic operations
make start          # Start all services
make stop           # Stop all services
make restart        # Restart all services
make status         # Show service status

# Testing
make test           # Run comprehensive tests
make test-example   # Run example usage test
make health         # Test health endpoint

# Logs and debugging
make logs           # Show all service logs
make logs-api       # Show Flask API logs only
make logs-db        # Show PostgreSQL logs only
make debug          # Start in debug mode

# Development
make install-deps   # Install Python dependencies
make lint           # Run code linting
make format         # Format Python code
make dev-setup      # Setup development environment

# Database operations
make db-connect     # Connect to PostgreSQL
make backup         # Create database backup
make restore        # Restore from backup (BACKUP_FILE=file.sql)
make reset-db       # Reset database

# Container operations
make shell-api      # Open shell in Flask container
make shell-db       # Open shell in PostgreSQL container
make build          # Build Docker images
make rebuild        # Rebuild and restart

# Cleanup
make clean          # Remove all containers and volumes
make monitor        # Monitor resource usage
```

### Option 2: Shell Script
For users who prefer shell scripts, a simple `start.sh` script is also available:

```bash
# Start services
./start.sh

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Run tests
python test_local_snowflake.py
```

## Configuration

### Environment Variables

The following environment variables can be configured:

- `POSTGRES_HOST`: PostgreSQL host (default: localhost)
- `POSTGRES_PORT`: PostgreSQL port (default: 5432)
- `POSTGRES_DB`: Database name (default: snowflake_local)
- `POSTGRES_USER`: Database user (default: snowflake_user)
- `POSTGRES_PASSWORD`: Database password (default: snowflake_password)

### Docker Configuration

The `docker-compose.yml` file configures:

- **PostgreSQL**: Port 5432, persistent volume
- **Flask API**: Port 4566, development mode
- **Networks**: Isolated network for service communication

## Development

### Adding New SQL Translations

To add new SQL syntax translations, modify `app/snowflake_proxy/sql_translator.py`:

```python
def _translate_new_syntax(self, query: str) -> str:
    """Add new translation rules here"""
    # Example: Replace Snowflake-specific function
    query = query.replace('SNOWFLAKE_FUNC()', 'postgres_func()')
    return query
```

### Extending Connection Management

To add new connection features, modify `app/snowflake_proxy/connection_handler.py`:

```python
def new_feature(self, connection_id: str, **kwargs):
    """Add new connection features here"""
    # Implementation
    pass
```

## Troubleshooting

### Common Issues

1. **Connection Refused**: Make sure Docker containers are running
   ```bash
   make start
   ```

2. **Database Connection Error**: Check PostgreSQL logs
   ```bash
   make logs-db
   ```

3. **API Errors**: Check Flask API logs
   ```bash
   make logs-api
   ```

### Debug Mode

To run in debug mode:

```bash
# Start with debug logging
make debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Acknowledgments

- Inspired by LocalStack's approach to AWS service emulation
- Built on PostgreSQL's robust SQL support
- Uses Flask for lightweight API development 