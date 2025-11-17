#!/usr/bin/env python3
"""
Python test script for API endpoints
Provides more detailed testing than the bash script
"""

import requests
import json
import time
import sys
from pathlib import Path

API_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'

def print_test(name, passed, message=""):
    status = f"{Colors.GREEN}✓ PASSED{Colors.NC}" if passed else f"{Colors.RED}✗ FAILED{Colors.NC}"
    print(f"{status}: {name}")
    if message:
        print(f"  {message}")

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        data = response.json()
        
        passed = (
            response.status_code == 200 and
            "status" in data and
            "services" in data
        )
        
        if passed:
            services = data["services"]
            all_healthy = all(services.values())
            print_test("Health Check", all_healthy, 
                      f"Services: {json.dumps(services, indent=2)}")
        else:
            print_test("Health Check", False, "Invalid response format")
        
        return passed
    except Exception as e:
        print_test("Health Check", False, str(e))
        return False

def test_upload():
    """Test document upload"""
    try:
        test_file = Path("data/test_docs/test_query.txt")
        
        if not test_file.exists():
            print_test("Document Upload", False, "Test file not found")
            return False
        
        with open(test_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{API_URL}/upload", files=files, timeout=30)
        
        passed = response.status_code == 200
        
        if passed:
            data = response.json()
            print_test("Document Upload", True, 
                      f"Uploaded {data.get('filename')} with {data.get('chunks')} chunks")
        else:
            print_test("Document Upload", False, 
                      f"Status: {response.status_code}, Response: {response.text}")
        
        return passed
    except Exception as e:
        print_test("Document Upload", False, str(e))
        return False

def test_query():
    """Test query endpoint"""
    try:
        # Wait a moment for indexing
        time.sleep(2)
        
        payload = {
            "question": "What is the purpose of the test document?"
        }
        
        response = requests.post(
            f"{API_URL}/query",
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            print_test("Query", False, f"Status: {response.status_code}")
            return False
        
        data = response.json()
        
        passed = (
            "answer" in data and
            "sources" in data and
            len(data["answer"]) > 0
        )
        
        if passed:
            answer_preview = data["answer"][:100] + "..." if len(data["answer"]) > 100 else data["answer"]
            print_test("Query", True, f"Answer: {answer_preview}")
            print(f"  Sources: {len(data['sources'])} documents")
        else:
            print_test("Query", False, "Invalid response format")
        
        return passed
    except Exception as e:
        print_test("Query", False, str(e))
        return False

def test_stats():
    """Test stats endpoint"""
    try:
        response = requests.get(f"{API_URL}/stats", timeout=5)
        data = response.json()
        
        passed = (
            response.status_code == 200 and
            "total_documents" in data
        )
        
        if passed:
            print_test("Stats", True, 
                      f"Total chunks: {data['total_documents']}")
        else:
            print_test("Stats", False, "Invalid response")
        
        return passed
    except Exception as e:
        print_test("Stats", False, str(e))
        return False

def test_list_documents():
    """Test document listing"""
    try:
        response = requests.get(f"{API_URL}/documents", timeout=5)
        
        passed = (
            response.status_code == 200 and
            isinstance(response.json(), list)
        )
        
        if passed:
            docs = response.json()
            print_test("List Documents", True, f"Found {len(docs)} documents")
        else:
            print_test("List Documents", False)
        
        return passed
    except Exception as e:
        print_test("List Documents", False, str(e))
        return False

def main():
    print("=" * 50)
    print("AI Document Helper - API Tests")
    print("=" * 50)
    print()
    
    # Wait for services
    print("Waiting for services to be ready...")
    max_attempts = 30
    for i in range(max_attempts):
        try:
            requests.get(f"{API_URL}/health", timeout=2)
            print(f"{Colors.GREEN}✓ Services are ready{Colors.NC}")
            break
        except:
            if i < max_attempts - 1:
                print(f"Waiting... ({i+1}/{max_attempts})")
                time.sleep(2)
            else:
                print(f"{Colors.RED}✗ Services failed to start{Colors.NC}")
                sys.exit(1)
    
    print()
    
    # Run tests
    tests = [
        ("Health Check", test_health),
        ("List Documents", test_list_documents),
        ("Stats", test_stats),
        ("Document Upload", test_upload),
        ("Query", test_query),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\nTesting: {name}")
        print("-" * 50)
        result = test_func()
        results.append(result)
        print()
    
    # Summary
    print("=" * 50)
    print("Test Summary")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    print(f"{Colors.GREEN}Passed: {passed}/{total}{Colors.NC}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}All tests passed! ✓{Colors.NC}")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}Some tests failed{Colors.NC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
