#!/bin/bash

# Snowflake Localhost Proxy - Start Script
# Alternative to: make start

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
API_URL="http://localhost:4566"
DB_URL="localhost:5432"

echo -e "${BLUE}🚀 Starting Snowflake Localhost Proxy...${NC}"

# Check if Docker is running
echo -e "${YELLOW}Checking if Docker is running...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Stop any existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose down

# Start the services
echo -e "${YELLOW}🔧 Starting PostgreSQL and Flask API...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Check if services are running
echo -e "${YELLOW}🔍 Checking service status...${NC}"
docker-compose ps

# Test the health endpoint
echo -e "${YELLOW}🏥 Testing health endpoint...${NC}"
if curl -s "$API_URL/health" > /dev/null; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
fi

echo ""
echo -e "${GREEN}✅ Services started successfully!${NC}"
echo ""
echo -e "${BLUE}📊 Available endpoints:${NC}"
echo "   - Health check: $API_URL/health"
echo "   - PostgreSQL: $DB_URL"
echo ""
echo -e "${BLUE}🧪 To run tests:${NC}"
echo "   python test_local_snowflake.py"
echo "   # or use Makefile: make test"
echo ""
echo -e "${BLUE}📝 To view logs:${NC}"
echo "   docker-compose logs -f"
echo "   # or use Makefile: make logs"
echo ""
echo -e "${BLUE}🛑 To stop services:${NC}"
echo "   docker-compose down"
echo "   # or use Makefile: make stop"
echo ""
echo -e "${BLUE}📚 Available commands:${NC}"
echo "   ./start.sh          # Start services (this script)"
echo "   make start          # Start services (Makefile)"
echo "   make test           # Run tests"
echo "   make logs           # View logs"
echo "   make stop           # Stop services"
echo "   make help           # Show all Makefile commands" 