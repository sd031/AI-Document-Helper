#!/bin/bash

# AI Document Helper - End-to-End Test Script
# This script tests the entire workflow of the system

set -e  # Exit on error

echo "=========================================="
echo "AI Document Helper - End-to-End Tests"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to print test result
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC}: $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}: $2"
        ((TESTS_FAILED++))
    fi
}

# Function to test endpoint
test_endpoint() {
    local url=$1
    local description=$2
    local expected_status=${3:-200}
    
    echo -n "Testing: $description... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$response" = "$expected_status" ]; then
        print_result 0 "$description"
        return 0
    else
        print_result 1 "$description (Expected: $expected_status, Got: $response)"
        return 1
    fi
}

echo "Step 1: Checking if services are running..."
echo "-------------------------------------------"

# Check if Docker Compose is running
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${RED}Error: Services are not running. Please run 'docker-compose up -d' first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker services are running${NC}"
echo ""

echo "Step 2: Waiting for services to be ready..."
echo "--------------------------------------------"

# Wait for backend to be ready
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is ready${NC}"
        break
    fi
    echo "Waiting for backend... ($((attempt+1))/$max_attempts)"
    sleep 2
    ((attempt++))
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}✗ Backend failed to start${NC}"
    exit 1
fi

# Wait for frontend to be ready
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is ready${NC}"
        break
    fi
    echo "Waiting for frontend... ($((attempt+1))/$max_attempts)"
    sleep 2
    ((attempt++))
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}✗ Frontend failed to start${NC}"
    exit 1
fi

echo ""

echo "Step 3: Testing API Endpoints..."
echo "---------------------------------"

# Test health endpoint
test_endpoint "http://localhost:8000/health" "Health check endpoint"

# Test root endpoint
test_endpoint "http://localhost:8000/" "Root endpoint"

# Test documents list endpoint
test_endpoint "http://localhost:8000/documents" "List documents endpoint"

# Test stats endpoint
test_endpoint "http://localhost:8000/stats" "Stats endpoint"

echo ""

echo "Step 4: Testing Document Upload..."
echo "-----------------------------------"

# Upload test document
echo -n "Uploading test document... "
upload_response=$(curl -s -w "\n%{http_code}" -X POST \
    -F "file=@data/test_docs/test_query.txt" \
    http://localhost:8000/upload)

upload_status=$(echo "$upload_response" | tail -n1)

if [ "$upload_status" = "200" ]; then
    print_result 0 "Document upload"
else
    print_result 1 "Document upload (Status: $upload_status)"
fi

echo ""

echo "Step 5: Testing Query Functionality..."
echo "---------------------------------------"

# Wait a moment for indexing
sleep 2

# Test query
echo -n "Testing query endpoint... "
query_response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"question": "What is the purpose of the test document?"}' \
    http://localhost:8000/query)

query_status=$(echo "$query_response" | tail -n1)
query_body=$(echo "$query_response" | head -n-1)

if [ "$query_status" = "200" ]; then
    # Check if response contains expected fields
    if echo "$query_body" | grep -q "answer" && echo "$query_body" | grep -q "sources"; then
        print_result 0 "Query endpoint (with valid response)"
        echo "Sample answer: $(echo "$query_body" | grep -o '"answer":"[^"]*"' | head -c 100)..."
    else
        print_result 1 "Query endpoint (missing expected fields)"
    fi
else
    print_result 1 "Query endpoint (Status: $query_status)"
fi

echo ""

echo "Step 6: Running Backend Unit Tests..."
echo "--------------------------------------"

# Run pytest in backend container
if docker-compose exec -T backend pytest tests/ -v --tb=short; then
    print_result 0 "Backend unit tests"
else
    print_result 1 "Backend unit tests"
fi

echo ""

echo "Step 7: Testing MLOps Pipeline..."
echo "----------------------------------"

echo "Running training pipeline..."
if docker-compose --profile training up --abort-on-container-exit mlops 2>&1 | grep -q "Training Pipeline Complete"; then
    print_result 0 "MLOps training pipeline"
else
    print_result 1 "MLOps training pipeline"
fi

echo ""

echo "Step 8: Verifying Vector Database..."
echo "-------------------------------------"

# Check stats after training
stats_response=$(curl -s http://localhost:8000/stats)

if echo "$stats_response" | grep -q "total_documents"; then
    doc_count=$(echo "$stats_response" | grep -o '"total_documents":[0-9]*' | grep -o '[0-9]*')
    if [ "$doc_count" -gt 0 ]; then
        print_result 0 "Vector database has indexed documents ($doc_count chunks)"
    else
        print_result 1 "Vector database is empty"
    fi
else
    print_result 1 "Unable to retrieve stats"
fi

echo ""

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    echo ""
    echo "The AI Document Helper system is working correctly!"
    echo ""
    echo "You can now:"
    echo "  - Access the UI at: http://localhost:3000"
    echo "  - View API docs at: http://localhost:8000/docs"
    echo "  - Upload documents and ask questions!"
    exit 0
else
    echo -e "${RED}Some tests failed. Please check the output above.${NC}"
    exit 1
fi
