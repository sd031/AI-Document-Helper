#!/bin/bash

# AI Document Helper - Setup Script
# This script sets up the entire system

set -e  # Exit on error

echo "=========================================="
echo "AI Document Helper - Setup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Step 1: Checking prerequisites..."
echo "----------------------------------"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi
echo -e "${GREEN}✓ Docker is installed${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose is installed${NC}"

echo ""

echo "Step 2: Building Docker images..."
echo "----------------------------------"
docker-compose build

echo ""

echo "Step 3: Starting services..."
echo "----------------------------"
docker-compose up -d

echo ""

echo "Step 4: Waiting for services to be ready..."
echo "--------------------------------------------"

# Wait for Ollama
echo "Waiting for Ollama to start..."
sleep 10

# Pull LLM model
echo "Pulling Ollama model (this may take a few minutes)..."
docker exec ollama ollama pull llama3.2

echo ""

echo "Step 5: Running training pipeline..."
echo "-------------------------------------"
docker-compose --profile training up mlops

echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo -e "${GREEN}The AI Document Helper is ready to use!${NC}"
echo ""
echo "Access points:"
echo "  - Frontend UI:    http://localhost:3000"
echo "  - Backend API:    http://localhost:8000"
echo "  - API Docs:       http://localhost:8000/docs"
echo "  - Qdrant:         http://localhost:6333/dashboard"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Upload documents or use the sample documents"
echo "  3. Ask questions about your documents"
echo ""
echo "To run tests:"
echo "  ./scripts/run_tests.sh"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
