# 🚀 QUICK START GUIDE

## Cách chạy nhanh nhất (3 bước)

### 📌 Option 1: HTTP Authentication Server

```bash
# Bước 1: Khởi động server
python start_authapp.py --server-port 8000

# Bước 2: Test với browser
# Mở http://localhost:8000/login
# Login: admin / password

# Bước 3: Hoặc test với curl
curl -X POST http://localhost:8000/login -d "username=admin&password=password" -v
curl http://localhost:8000/ -H "Cookie: auth=true" -v
```

### 📌 Option 2: Hybrid Chat Application

```bash
# Terminal 1: Start tracker
python peer_tracker.py --port 5000

# Terminal 2: Start peer Alice
python chat_client.py alice --port 6001

# Terminal 3: Start peer Bob
python chat_client.py bob --port 6002

# Trong Alice terminal:
> /msg bob Hello Bob!
> /broadcast Hi everyone!

# Trong Bob terminal:
> /msg alice Hi Alice!
```

---

## 🎯 Test theo đúng yêu cầu đề bài

### Task 1A: POST /login Authentication

```bash
# Test 1: Đúng credentials
curl -X POST http://localhost:8000/login \
     -d "username=admin&password=password" \
     -i

# Expected output:
# HTTP/1.1 200 OK
# Set-Cookie: auth=true; Path=/; HttpOnly
# Content-Type: text/html
# [index.html content]

# Test 2: Sai credentials
curl -X POST http://localhost:8000/login \
     -d "username=wrong&password=wrong" \
     -i

# Expected output:
# HTTP/1.1 401 Unauthorized
# WWW-Authenticate: Basic realm="Authentication Required"
```

### Task 1B: GET / Cookie Access Control

```bash
# Test 1: Có cookie hợp lệ
curl http://localhost:8000/ \
     -H "Cookie: auth=true" \
     -i

# Expected output:
# HTTP/1.1 200 OK
# Content-Type: text/html
# [index.html content]

# Test 2: Không có cookie
curl http://localhost:8000/ -i

# Expected output:
# HTTP/1.1 401 Unauthorized
# WWW-Authenticate: Basic realm="Authentication Required"
```

### Chat Application: Client-Server Phase

```bash
# Test REGISTER
echo "REGISTER testpeer 127.0.0.1 6001" | nc localhost 5000

# Expected output:
# {"status": "success", "message": "Peer registered successfully", "peer_count": 1}

# Test GET_PEERS
echo "GET_PEERS" | nc localhost 5000

# Expected output:
# {"status": "success", "peers": [{"peer_id": "testpeer", "ip": "127.0.0.1", "port": 6001}], "peer_count": 1}
```

### Chat Application: P2P Phase

```bash
# Trong peer Alice:
> /peers                    # Xem danh sách peers
> /msg bob Hello!           # Direct message (P2P, không qua server)
> /broadcast Hi all!        # Broadcast tới tất cả peers

# Trong peer Bob (sẽ nhận được):
[alice] Direct message: Hello!
[alice] Broadcast: Hi all!
```

---

## 📊 Kiểm tra implementation đúng yêu cầu

### Checklist Task 1A + 1B

- [x] POST /login với admin/password → 200 + Set-Cookie
- [x] POST /login với sai info → 401 Unauthorized
- [x] GET / với cookie → 200 + index.html
- [x] GET / không cookie → 401 Unauthorized
- [x] Set-Cookie header theo RFC 6265
- [x] WWW-Authenticate header theo RFC 7235

### Checklist Hybrid Chat

**Client-Server Phase:**
- [x] Đăng ký peer (REGISTER)
- [x] Tracker lưu danh sách peers
- [x] Peer discovery (GET_PEERS)
- [x] Connection setup dựa vào peer list

**P2P Chat Phase:**
- [x] Direct messaging P2P (không qua server)
- [x] Broadcast messaging
- [x] Message display
- [x] Notifications khi có tin mới
- [x] Channel/peer management

### Checklist Kỹ thuật

- [x] Socket TCP/IP programming
- [x] Multi-threading (concurrent clients)
- [x] Application protocol design
- [x] Error handling
- [x] RFC 6265 (HTTP Cookie) compliance
- [x] RFC 7235 (HTTP Auth) compliance

---

## 🐛 Troubleshooting

### Lỗi "Address already in use"
```bash
# Tìm process đang dùng port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Lỗi "ModuleNotFoundError"
```bash
# Kiểm tra imports
python test_imports.py

# Nếu lỗi MutableMapping (Python 3.10+)
# → Đã fix trong daemon/dictionary.py

# Nếu lỗi urlparse (Python 3)
# → Đã fix trong start_proxy.py
```

### Chat không nhận tin
```bash
# 1. Kiểm tra tracker đang chạy
netstat -an | grep 5000

# 2. Refresh peer list
> /refresh

# 3. Kiểm tra kết nối
> /peers
```

---

## 📚 Files quan trọng

| File | Mục đích |
|------|----------|
| `start_authapp.py` | HTTP Authentication Server (Task 1A+1B) |
| `peer_tracker.py` | Peer Tracker (Client-Server phase) |
| `chat_client.py` | P2P Chat Client |
| `CHECKLIST.md` | So sánh yêu cầu vs implementation |
| `USAGE.txt` | Hướng dẫn chi tiết |
| `demo_auth.sh` | Demo authentication |
| `demo_chat.sh` | Demo chat app |

---

## 🎓 Kết luận

### Đã implement đầy đủ:

✅ **Task 1A - Authentication Handling**
- POST /login với validation
- Set-Cookie theo RFC 6265
- 401 Unauthorized theo RFC 7235

✅ **Task 1B - Cookie-based Access Control**
- GET / với cookie validation
- Access control logic
- Proper error responses

✅ **Hybrid Chat Application**
- Client-Server phase: registration, discovery
- P2P phase: direct + broadcast messaging
- Multi-threading, error handling

### Compliance:

✅ RFC 6265 - HTTP Cookie (Set-Cookie header)
✅ RFC 7235 - HTTP Authentication (401 + WWW-Authenticate)
✅ PEP8 - Code style
✅ PEP257 - Docstrings

**TẤT CẢ YÊU CẦU ĐỀ BÀI ĐÃ HOÀN THÀNH 100%** 🎉
