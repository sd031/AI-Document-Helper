#!/bin/bash

# Quick verification script
echo "🔍 AI Document Helper - Quick Verification"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Check services
echo "1. Checking services..."
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Services are running${NC}"
else
    echo -e "${RED}✗ Services are not running${NC}"
    echo "Run: docker-compose up -d"
    exit 1
fi

# Check backend health
echo ""
echo "2. Checking backend health..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend is not healthy${NC}"
    exit 1
fi

# Check frontend
echo ""
echo "3. Checking frontend..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is accessible${NC}"
else
    echo -e "${RED}✗ Frontend is not accessible${NC}"
    exit 1
fi

# Check documents indexed
echo ""
echo "4. Checking indexed documents..."
doc_count=$(curl -s http://localhost:8000/stats | grep -o '"total_documents":[0-9]*' | grep -o '[0-9]*')
if [ "$doc_count" -gt 0 ]; then
    echo -e "${GREEN}✓ $doc_count document chunks indexed${NC}"
else
    echo -e "${RED}✗ No documents indexed${NC}"
    echo "Run: docker-compose --profile training up mlops"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✓ All checks passed!${NC}"
echo ""
echo "Your AI Document Helper is ready to use!"
echo ""
echo "Access points:"
echo "  • Frontend: http://localhost:3000"
echo "  • Backend:  http://localhost:8000"
echo "  • API Docs: http://localhost:8000/docs"
echo ""
