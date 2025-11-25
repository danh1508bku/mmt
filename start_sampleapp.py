#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
#
# WeApRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#


"""
start_sampleapp
~~~~~~~~~~~~~~~~~

This module provides a hybrid chat application with tracker and P2P capabilities.
It implements cookie-based authentication, peer discovery, and channel-based messaging.
"""

import json
import socket
import argparse
import threading
import datetime

from daemon.weaprous import WeApRous

PORT = 8000  # Default port

# Global data structures for tracker
active_peers = []  # List of {ip, port, name} dicts
peer_connections = {}  # Map of peer_id -> socket
channels = {
    'general': {'id': 'general', 'name': 'General', 'messages': []},
}
channel_lock = threading.Lock()
peers_lock = threading.Lock()

app = WeApRous()

def parse_form_data(body):
    """Parse URL-encoded form data from request body."""
    params = {}
    if not body:
        return params

    for pair in body.split('&'):
        if '=' in pair:
            key, value = pair.split('=', 1)
            # Basic URL decode for common characters
            value = value.replace('+', ' ').replace('%40', '@')
            params[key] = value
    return params

@app.route('/login', methods=['POST'])
def login(request=None, response=None):
    """
    Handle user login via POST request with cookie-based session (RFC 6265).

    Expected body: username=admin&password=password
    Returns: 200 OK with auth cookie on success, 401 Unauthorized on failure
    """
    print("[SampleApp] POST /login")

    # Parse the request body
    params = parse_form_data(request.body)
    username = params.get('username', '')
    password = params.get('password', '')

    print("[SampleApp] Login attempt: username={}".format(username))

    # Validate credentials
    if username == 'admin' and password == 'password':
        # Successful login - set auth cookie (RFC 6265)
        response.status_code = 200
        response.reason = "OK"
        response.cookies['auth'] = 'true'
        response.headers['Content-Type'] = 'text/html'

        # Return success page with redirect
        response._content = b'''<html>
<head><title>Login Successful</title></head>
<body>
<h1>Login Successful</h1>
<p>Redirecting to chat...</p>
<script>setTimeout(function(){ window.location.href = '/'; }, 1000);</script>
</body>
</html>'''

        return response.build_response_header(request) + response._content
    else:
        # Failed login - return 401 Unauthorized (RFC 7235)
        response.status_code = 401
        response.reason = "Unauthorized"
        response.headers['WWW-Authenticate'] = 'Basic realm="NetApp"'
        response.headers['Content-Type'] = 'text/html'
        response._content = b'''<html>
<head><title>Login Failed</title></head>
<body>
<h1>401 Unauthorized</h1>
<p>Invalid credentials. <a href="/login.html">Try again</a></p>
</body>
</html>'''

        return response.build_response_header(request) + response._content

@app.route('/submit-info', methods=['POST', 'GET'])
def submit_info(request=None, response=None):
    """
    Register peer with tracker.

    POST body: ip=<peer_ip>&port=<peer_port>&name=<peer_name>
    Returns: JSON with success status
    """
    print("[SampleApp] {} /submit-info".format(request.method))

    if request.method == 'POST':
        params = parse_form_data(request.body)
        peer_ip = params.get('ip', '')
        peer_port = params.get('port', '')
        peer_name = params.get('name', 'Anonymous')

        peer_info = {
            'ip': peer_ip,
            'port': peer_port,
            'name': peer_name,
            'joined': datetime.datetime.utcnow().isoformat()
        }

        with peers_lock:
            active_peers.append(peer_info)

        print("[SampleApp] Peer registered: {}".format(peer_info))

        result = json.dumps({'status': 'success', 'peer': peer_info})
    else:
        result = json.dumps({'status': 'error', 'message': 'Use POST method'})

    response.status_code = 200
    response.reason = "OK"
    response.headers['Content-Type'] = 'application/json'
    response._content = result.encode('utf-8')

    return response.build_response_header(request) + response._content

@app.route('/add-list', methods=['POST'])
def add_list(request=None, response=None):
    """
    Add peer to active peers list (alias for submit-info).
    """
    return submit_info(request, response)

@app.route('/get-list', methods=['GET'])
def get_list(request=None, response=None):
    """
    Get list of active peers.

    Returns: JSON array of active peers
    """
    print("[SampleApp] GET /get-list")

    with peers_lock:
        result = json.dumps({'status': 'success', 'peers': active_peers})

    response.status_code = 200
    response.reason = "OK"
    response.headers['Content-Type'] = 'application/json'
    response._content = result.encode('utf-8')

    return response.build_response_header(request) + response._content

@app.route('/connect-peer', methods=['POST'])
def connect_peer(request=None, response=None):
    """
    Establish P2P connection to a peer.

    POST body: peer_ip=<ip>&peer_port=<port>
    Returns: JSON with connection status
    """
    print("[SampleApp] POST /connect-peer")

    params = parse_form_data(request.body)
    peer_ip = params.get('peer_ip', '')
    peer_port = int(params.get('peer_port', '0'))

    try:
        # Attempt to connect to peer
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect((peer_ip, peer_port))

        peer_id = "{}:{}".format(peer_ip, peer_port)
        peer_connections[peer_id] = peer_socket

        result = json.dumps({
            'status': 'success',
            'peer_id': peer_id,
            'message': 'Connected to peer'
        })

        print("[SampleApp] Connected to peer {}".format(peer_id))
    except Exception as e:
        result = json.dumps({
            'status': 'error',
            'message': 'Failed to connect: {}'.format(str(e))
        })
        print("[SampleApp] Connection failed: {}".format(e))

    response.status_code = 200
    response.reason = "OK"
    response.headers['Content-Type'] = 'application/json'
    response._content = result.encode('utf-8')

    return response.build_response_header(request) + response._content

@app.route('/broadcast-peer', methods=['POST'])
def broadcast_peer(request=None, response=None):
    """
    Broadcast message to all connected peers via P2P.

    POST body: message=<text>
    Returns: JSON with broadcast status
    """
    print("[SampleApp] POST /broadcast-peer")

    params = parse_form_data(request.body)
    message = params.get('message', '')

    success_count = 0
    for peer_id, peer_socket in peer_connections.items():
        try:
            peer_socket.sendall(message.encode('utf-8'))
            success_count += 1
        except Exception as e:
            print("[SampleApp] Broadcast to {} failed: {}".format(peer_id, e))

    result = json.dumps({
        'status': 'success',
        'sent_to': success_count,
        'total_peers': len(peer_connections)
    })

    response.status_code = 200
    response.reason = "OK"
    response.headers['Content-Type'] = 'application/json'
    response._content = result.encode('utf-8')

    return response.build_response_header(request) + response._content

@app.route('/send-peer', methods=['POST'])
def send_peer(request=None, response=None):
    """
    Send message to specific peer via P2P.

    POST body: peer_id=<id>&message=<text>
    Returns: JSON with send status
    """
    print("[SampleApp] POST /send-peer")

    params = parse_form_data(request.body)
    peer_id = params.get('peer_id', '')
    message = params.get('message', '')

    if peer_id in peer_connections:
        try:
            peer_connections[peer_id].sendall(message.encode('utf-8'))
            result = json.dumps({'status': 'success', 'message': 'Sent to {}'.format(peer_id)})
        except Exception as e:
            result = json.dumps({'status': 'error', 'message': str(e)})
    else:
        result = json.dumps({'status': 'error', 'message': 'Peer not connected'})

    response.status_code = 200
    response.reason = "OK"
    response.headers['Content-Type'] = 'application/json'
    response._content = result.encode('utf-8')

    return response.build_response_header(request) + response._content

@app.route('/channels', methods=['GET'])
def get_channels(request=None, response=None):
    """
    Get list of available channels.

    Returns: JSON array of channels
    """
    print("[SampleApp] GET /channels")

    with channel_lock:
        channel_list = [
            {'id': ch_id, 'name': ch['name']}
            for ch_id, ch in channels.items()
        ]

    result = json.dumps({'status': 'success', 'channels': channel_list})

    response.status_code = 200
    response.reason = "OK"
    response.headers['Content-Type'] = 'application/json'
    response._content = result.encode('utf-8')

    return response.build_response_header(request) + response._content

@app.route('/channel/general/messages', methods=['GET'])
def get_channel_messages(request=None, response=None):
    """
    Get messages from a channel.

    Returns: JSON array of messages
    """
    print("[SampleApp] GET /channel/general/messages")

    channel_id = 'general'

    with channel_lock:
        if channel_id in channels:
            messages = channels[channel_id].get('messages', [])
            result = json.dumps({'status': 'success', 'messages': messages})
        else:
            result = json.dumps({'status': 'error', 'message': 'Channel not found'})

    response.status_code = 200
    response.reason = "OK"
    response.headers['Content-Type'] = 'application/json'
    response._content = result.encode('utf-8')

    return response.build_response_header(request) + response._content

@app.route('/channel/general/message', methods=['POST'])
def post_channel_message(request=None, response=None):
    """
    Post message to a channel.

    POST body: username=<name>&message=<text>
    Returns: JSON with post status
    """
    print("[SampleApp] POST /channel/general/message")

    channel_id = 'general'
    params = parse_form_data(request.body)
    username = params.get('username', 'Anonymous')
    message_text = params.get('message', '')

    message = {
        'username': username,
        'message': message_text,
        'timestamp': datetime.datetime.utcnow().isoformat()
    }

    with channel_lock:
        if channel_id in channels:
            channels[channel_id]['messages'].append(message)
            result = json.dumps({'status': 'success', 'message': message})
        else:
            result = json.dumps({'status': 'error', 'message': 'Channel not found'})

    response.status_code = 200
    response.reason = "OK"
    response.headers['Content-Type'] = 'application/json'
    response._content = result.encode('utf-8')

    return response.build_response_header(request) + response._content

@app.route('/hello', methods=['GET', 'PUT'])
def hello(request=None, response=None):
    """
    Simple hello endpoint for testing.
    """
    print("[SampleApp] {} /hello".format(request.method))

    result = json.dumps({'status': 'success', 'message': 'Hello, world!'})

    response.status_code = 200
    response.reason = "OK"
    response.headers['Content-Type'] = 'application/json'
    response._content = result.encode('utf-8')

    return response.build_response_header(request) + response._content

if __name__ == "__main__":
    # Parse command-line arguments to configure server IP and port
    parser = argparse.ArgumentParser(prog='SampleApp', description='Hybrid Chat Application', epilog='WeApRous backend daemon')
    parser.add_argument('--server-ip', default='0.0.0.0')
    parser.add_argument('--server-port', type=int, default=PORT)

    args = parser.parse_args()
    ip = args.server_ip
    port = args.server_port

    # Prepare and launch the RESTful application
    app.prepare_address(ip, port)
    print("[SampleApp] Starting chat application on {}:{}".format(ip, port))
    app.run()
