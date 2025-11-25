# Multi-Process HTTP System with Hybrid Chat Application

A complete implementation of a multi-process HTTP system built entirely on raw TCP sockets, featuring a proxy server, backend HTTP server, and a hybrid chat application with both client-server and P2P capabilities.

## Architecture

The system consists of three main processes:

1. **Proxy Server** (`start_proxy.py`) - Routes requests based on Host headers
2. **Backend Server** (`start_backend.py`) - Serves static files and handles HTTP requests
3. **WebApp (WeApRous)** (`start_sampleapp.py`) - RESTful API endpoints for chat and tracker

## Features

### Core HTTP Infrastructure
- ✅ Raw TCP socket implementation (no external web frameworks)
- ✅ Multi-threaded connection handling
- ✅ Host-based request routing with load balancing
- ✅ Static file serving (HTML, CSS, JS, images)
- ✅ Cookie-based session management (RFC 6265)
- ✅ HTTP authentication support (RFC 7235, RFC 2617)
- ✅ Proper MIME type detection and Content-Type headers

### Chat Application
- ✅ Cookie-based login authentication
- ✅ Channel-based messaging (persistent chat history)
- ✅ Peer tracker for discovery
- ✅ P2P connection establishment
- ✅ Broadcast and direct messaging
- ✅ Real-time message updates
- ✅ Active peers list

## Quick Start

### 1. Start the Proxy Server
```bash
python start_proxy.py --server-ip 0.0.0.0 --server-port 8080
```

### 2. Start the Backend Server
```bash
python start_backend.py --server-ip 0.0.0.0 --server-port 9000
```

### 3. Start the Chat Application
```bash
python start_sampleapp.py --server-ip 0.0.0.0 --server-port 8000
```

### 4. Access the Application
Open your browser and navigate to:
- **Via Proxy**: `http://localhost:8080` or `http://127.0.0.1:8080`
- **Direct Backend**: `http://localhost:9000` or `http://127.0.0.1:9000`
- **Direct Chat App**: `http://localhost:8000` or `http://127.0.0.1:8000`

**Note**: When accessing via proxy (port 8080), you need to ensure your browser sends the correct Host header. For local testing, it's easier to access the backend directly on port 9000.

## Default Credentials

- **Username**: `admin`
- **Password**: `password`

## Directory Structure

```
mmt/
├── daemon/                 # Core HTTP modules
│   ├── proxy.py           # Proxy server implementation
│   ├── backend.py         # Backend server with threading
│   ├── httpadapter.py     # HTTP request/response handler
│   ├── request.py         # Request parser (headers, cookies, body)
│   ├── response.py        # Response builder (headers, MIME, content)
│   ├── weaprous.py        # Decorator-based routing framework
│   └── dictionary.py      # Case-insensitive dict for headers
├── config/
│   └── proxy.conf         # Proxy routing configuration
├── www/                   # Static HTML pages
│   ├── index.html         # Chat UI (protected)
│   └── login.html         # Login page
├── static/                # Static assets
│   ├── css/
│   │   └── styles.css
│   └── images/
│       └── welcome.png
├── start_proxy.py         # Proxy server entry point
├── start_backend.py       # Backend server entry point
└── start_sampleapp.py     # Chat application entry point
```

## API Endpoints

### Authentication
- `POST /login` - Login with credentials, sets auth cookie

### Tracker (Client-Server)
- `POST /submit-info` - Register peer with tracker
- `POST /add-list` - Add peer to active list
- `GET /get-list` - Retrieve list of active peers

### P2P Messaging
- `POST /connect-peer` - Establish P2P connection
- `POST /broadcast-peer` - Broadcast message to all peers
- `POST /send-peer` - Send message to specific peer

### Channels
- `GET /channels` - List available channels
- `GET /channel/general/messages` - Get messages from a channel
- `POST /channel/general/message` - Post message to a channel

## Configuration

### Proxy Configuration (`config/proxy.conf`)

```nginx
host "localhost:8080" {
    proxy_pass http://127.0.0.1:9000;
}

host "127.0.0.1:8080" {
    proxy_pass http://127.0.0.1:9000;
}

host "app1.local" {
    proxy_pass http://127.0.0.1:9001;
}

host "app2.local" {
    proxy_pass http://127.0.0.1:9002;
    proxy_pass http://127.0.0.1:9003;
    dist_policy round-robin
}
```

## RFC Compliance

### RFC 6265 - HTTP State Management (Cookies)
- Cookie parsing from `Cookie` header
- `Set-Cookie` header formatting with attributes:
  - `Path=/` - Cookie available site-wide
  - `HttpOnly` - Prevent JavaScript access
  - `SameSite=Lax` - CSRF protection

### RFC 7235 - HTTP Authentication Framework
- `401 Unauthorized` status for protected resources
- `WWW-Authenticate` header for challenges
- Support for Basic authentication scheme

### RFC 2617 - HTTP Authentication (Basic/Digest)
- Basic authentication support
- Base64 credential encoding
- Realm-based authentication

## Implementation Details

### Cookie-Based Authentication
1. User submits login form to `POST /login`
2. Server validates credentials
3. On success: Sets `auth=true` cookie and redirects to chat
4. Protected pages (`/`, `/index.html`) check for valid auth cookie
5. Invalid/missing cookie → `401 Unauthorized`

### Multi-Threading
- Each client connection spawns a daemon thread
- Backend and proxy both use threaded model
- Thread-safe data structures with locks for shared state

### Static File Serving
- MIME type detection based on file extension
- Base directory selection:
  - `text/html` → `www/`
  - `text/css` → `static/`
  - `image/*` → `static/`
  - `application/javascript` → `static/js/`

### Chat Architecture
- **Tracker mode**: Central server tracks active peers
- **P2P mode**: Direct socket connections between peers
- **Hybrid**: Tracker for discovery, P2P for messaging
- **Channels**: Server-side message persistence

## Testing

### 1. Test Login
```bash
curl -X POST http://localhost:8000/login \
  -d "username=admin&password=password" \
  -v
```

### 2. Test Protected Resource
```bash
curl http://localhost:9000/ -v
# Should return 401 without cookie

curl http://localhost:9000/ \
  -H "Cookie: auth=true" -v
# Should return chat interface
```

### 3. Test Chat Message
```bash
curl -X POST http://localhost:8000/channel/general/message \
  -d "username=TestUser&message=Hello World" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

### 4. Test Peer Registration
```bash
curl -X POST http://localhost:8000/submit-info \
  -d "ip=127.0.0.1&port=5000&name=Peer1"
```

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8080

# Kill the process
kill -9 <PID>
```

### Permission Denied
```bash
# Use ports > 1024 or run with sudo
sudo python start_proxy.py
```

### Connection Refused
- Ensure all three processes are running
- Check firewall settings
- Verify IP addresses in proxy.conf match your network

## Security Considerations

⚠️ **This is a educational implementation. Not production-ready.**

- No HTTPS/TLS support
- Simple credential validation
- No SQL injection protection
- No XSS sanitization
- No rate limiting
- No session timeout

## License

Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
This file is part of the CO3093/CO3094 course.

## Contributors

- Implementation based on WeApRous framework
- Multi-process HTTP system design
- Hybrid chat application architecture
