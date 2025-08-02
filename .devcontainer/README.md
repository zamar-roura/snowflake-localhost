# Dev Container Setup

This project includes VS Code Dev Container configurations for easy development setup.

## Available Configurations

### 1. Full Stack (Recommended)
- **File**: `devcontainer.json`
- **Uses**: Docker Compose with PostgreSQL + Snowflake Proxy
- **Features**: Complete development environment with database

### 2. Application Only
- **File**: `devcontainer-dockerfile.json`
- **Uses**: Just the Dockerfile
- **Features**: Lightweight setup for application development only

## How to Use

1. **Install VS Code Dev Containers Extension**
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Search for "Dev Containers" and install

2. **Open in Dev Container**
   - Open this project in VS Code
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Dev Containers: Reopen in Container"
   - Select your preferred configuration

3. **Alternative Method**
   - Right-click on the `.devcontainer` folder
   - Select "Reopen in Container"

## What's Included

- **Python 3.11** with all dependencies
- **Code formatting** with Black and isort
- **Linting** with Flake8
- **Python extensions** for VS Code
- **Docker support** extensions
- **Port forwarding** for your application (4566) and database (5432)

## Development Workflow

1. The container will automatically install dependencies
2. Your code is mounted at `/app` in the container
3. Changes are reflected immediately
4. Use the integrated terminal for running commands
5. Debug directly in the container

## Troubleshooting

- If the container fails to build, check that Docker is running
- For database issues, ensure the PostgreSQL service is healthy
- Check the VS Code Dev Containers logs for detailed error messages 