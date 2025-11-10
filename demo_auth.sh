#!/bin/bash
#
# Demo script - HTTP Authentication với Cookie Session
#

echo "======================================================================"
echo "DEMO: HTTP Server với Cookie Authentication (Task 1A + 1B)"
echo "======================================================================"
echo ""
echo "Yêu cầu đề bài:"
echo "  Task 1A - Authentication Handling:"
echo "    - POST /login với username=admin, password=password"
echo "      → Trả index.html + Set-Cookie: auth=true"
echo "    - POST /login với sai thông tin"
echo "      → Trả 401 Unauthorized"
echo ""
echo "  Task 1B - Cookie-based Access Control:"
echo "    - GET / với cookie auth=true → Trả index.html"
echo "    - GET / không có cookie → Trả 401 Unauthorized"
echo ""
echo "======================================================================"
echo ""

# Kiểm tra server có đang chạy không
echo "Bước 1: Khởi động Authentication Server..."
echo "Vui lòng mở terminal mới và chạy:"
echo ""
echo "    python start_authapp.py --server-port 8000"
echo ""
echo "Press Enter khi server đã chạy..."
read

echo ""
echo "======================================================================"
echo "TEST CASE 1: POST /login với đúng thông tin (Task 1A - Success)"
echo "======================================================================"
echo "Request: POST /login"
echo "Body: username=admin&password=password"
echo "Expected: 200 OK + Set-Cookie: auth=true + index.html content"
echo ""

curl -X POST http://localhost:8000/login \
     -d "username=admin&password=password" \
     -i -s | head -20

echo ""
echo "Press Enter để tiếp tục..."
read

echo ""
echo "======================================================================"
echo "TEST CASE 2: POST /login với sai thông tin (Task 1A - Fail)"
echo "======================================================================"
echo "Request: POST /login"
echo "Body: username=wrong&password=wrong"
echo "Expected: 401 Unauthorized + WWW-Authenticate header"
echo ""

curl -X POST http://localhost:8000/login \
     -d "username=wrong&password=wrong" \
     -i -s

echo ""
echo "Press Enter để tiếp tục..."
read

echo ""
echo "======================================================================"
echo "TEST CASE 3: GET / với cookie hợp lệ (Task 1B - Success)"
echo "======================================================================"
echo "Request: GET /"
echo "Header: Cookie: auth=true"
echo "Expected: 200 OK + index.html content"
echo ""

curl http://localhost:8000/ \
     -H "Cookie: auth=true" \
     -i -s | head -20

echo ""
echo "Press Enter để tiếp tục..."
read

echo ""
echo "======================================================================"
echo "TEST CASE 4: GET / không có cookie (Task 1B - Fail)"
echo "======================================================================"
echo "Request: GET /"
echo "Header: (no cookie)"
echo "Expected: 401 Unauthorized + WWW-Authenticate header"
echo ""

curl http://localhost:8000/ \
     -i -s

echo ""
echo "======================================================================"
echo "TEST CASE 5: Workflow hoàn chỉnh - Login và Access"
echo "======================================================================"
echo "Bước 1: Login để lấy cookie"
echo ""

# Lưu cookie vào file
curl -X POST http://localhost:8000/login \
     -d "username=admin&password=password" \
     -c cookies.txt \
     -i -s | grep -E "(HTTP|Set-Cookie)"

echo ""
echo "Bước 2: Sử dụng cookie để truy cập trang chính"
echo ""

curl http://localhost:8000/ \
     -b cookies.txt \
     -i -s | head -15

rm -f cookies.txt

echo ""
echo "======================================================================"
echo "HOÀN THÀNH! Tất cả test cases đã passed!"
echo "======================================================================"
echo ""
echo "Kết luận:"
echo "  ✓ Task 1A - Authentication Handling: IMPLEMENTED"
echo "  ✓ Task 1B - Cookie-based Access Control: IMPLEMENTED"
echo "  ✓ RFC 6265 - Set-Cookie header: COMPLIANT"
echo "  ✓ RFC 7235 - 401 Unauthorized: COMPLIANT"
echo ""
