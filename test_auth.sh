#!/bin/bash
#
# Test script for HTTP Authentication Application
# Tests Task 1A and 1B
#

echo "======================================================================"
echo "HTTP Authentication Test Script"
echo "======================================================================"
echo ""
echo "This script tests the authentication webapp."
echo "Make sure start_authapp.py is running on localhost:8000"
echo ""
echo "Press Enter to continue or Ctrl+C to exit..."
read

echo ""
echo "======================================================================"
echo "Test 1A: POST /login with correct credentials"
echo "======================================================================"
echo "Expected: 200 OK with Set-Cookie: auth=true"
echo ""
curl -X POST http://localhost:8000/login \
     -d "username=admin&password=password" \
     -v \
     2>&1 | grep -E "(HTTP|Set-Cookie)"

echo ""
echo ""
echo "======================================================================"
echo "Test 1A: POST /login with incorrect credentials"
echo "======================================================================"
echo "Expected: 401 Unauthorized with WWW-Authenticate header"
echo ""
curl -X POST http://localhost:8000/login \
     -d "username=wrong&password=wrong" \
     -v \
     2>&1 | grep -E "(HTTP|WWW-Authenticate)"

echo ""
echo ""
echo "======================================================================"
echo "Test 1B: GET / with valid auth cookie"
echo "======================================================================"
echo "Expected: 200 OK with index.html content"
echo ""
curl http://localhost:8000/ \
     -H "Cookie: auth=true" \
     -v \
     2>&1 | grep -E "(HTTP|Content-Type)"

echo ""
echo ""
echo "======================================================================"
echo "Test 1B: GET / without auth cookie"
echo "======================================================================"
echo "Expected: 401 Unauthorized with WWW-Authenticate header"
echo ""
curl http://localhost:8000/ \
     -v \
     2>&1 | grep -E "(HTTP|WWW-Authenticate)"

echo ""
echo ""
echo "======================================================================"
echo "Test Complete"
echo "======================================================================"
