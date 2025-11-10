#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course.
#
# WeApRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#

"""
chat_client
~~~~~~~~~~~~~~~~~

This module provides a P2P chat client for the hybrid chat application.

Hybrid Chat Application Architecture:
1. Client-Server Phase:
   - Register peer: send IP and port to tracker
   - Tracker update: tracker maintains peer list
   - Peer discovery: request list of available peers
   - Connection setup: use peer list to establish P2P connections

2. P2P Chat Phase:
   - Direct messaging: send messages directly between peers
   - Broadcast: send messages to all connected peers
   - Channel management: organize chat channels
   - Notifications: alert when new messages arrive

Protocol Commands:
- MSG <peer_id> <message> - Send direct message to specific peer
- BROADCAST <message> - Broadcast message to all peers
- PEERS - List connected peers
- QUIT - Exit chat
"""

import socket
import threading
import json
import argparse
import time
import sys


class ChatClient:
    """P2P Chat Client with tracker integration."""

    def __init__(self, peer_id, listen_port, tracker_host='127.0.0.1', tracker_port=5000):
        """
        Initialize chat client.

        :param peer_id: Unique identifier for this peer
        :param listen_port: Port to listen for incoming P2P connections
        :param tracker_host: Tracker server host
        :param tracker_port: Tracker server port
        """
        self.peer_id = peer_id
        self.listen_port = listen_port
        self.tracker_host = tracker_host
        self.tracker_port = tracker_port

        self.listen_socket = None
        self.running = False

        # Connected peers: peer_id -> socket
        self.peer_connections = {}
        self.peer_info = {}  # peer_id -> {'ip': ip, 'port': port}
        self.lock = threading.Lock()

        # Message history
        self.messages = []

    def start(self):
        """Start the chat client."""
        print("=" * 60)
        print("P2P Chat Client")
        print("=" * 60)
        print("Peer ID: {}".format(self.peer_id))
        print("Listening on port: {}".format(self.listen_port))
        print("=" * 60)

        # Register with tracker
        if not self._register_with_tracker():
            print("[Client] Failed to register with tracker")
            return

        # Start listening for incoming P2P connections
        self.running = True
        listen_thread = threading.Thread(target=self._listen_for_peers, daemon=True)
        listen_thread.start()

        # Get peer list from tracker
        self._update_peer_list()

        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=self._send_heartbeat, daemon=True)
        heartbeat_thread.start()

        # Start interactive CLI
        self._run_cli()

    def stop(self):
        """Stop the chat client."""
        self.running = False

        # Unregister from tracker
        self._unregister_from_tracker()

        # Close all peer connections
        with self.lock:
            for peer_id, conn in self.peer_connections.items():
                try:
                    conn.close()
                except:
                    pass

        # Close listen socket
        if self.listen_socket:
            self.listen_socket.close()

        print("[Client] Stopped")

    def _register_with_tracker(self):
        """
        Register this peer with the tracker server.

        :return: True if successful, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.tracker_host, self.tracker_port))

            # Get local IP
            local_ip = socket.gethostbyname(socket.gethostname())
            if local_ip.startswith('127.'):
                # Try to get a better IP
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(('8.8.8.8', 80))
                    local_ip = s.getsockname()[0]
                    s.close()
                except:
                    local_ip = '127.0.0.1'

            # Send REGISTER command
            command = "REGISTER {} {} {}".format(self.peer_id, local_ip, self.listen_port)
            sock.sendall(command.encode('utf-8'))

            # Receive response
            response = sock.recv(4096).decode('utf-8')
            result = json.loads(response)

            sock.close()

            if result.get('status') == 'success':
                print("[Client] Registered with tracker successfully")
                print("[Client] Total peers in network: {}".format(result.get('peer_count', 0)))
                return True
            else:
                print("[Client] Registration failed: {}".format(result.get('message')))
                return False

        except Exception as e:
            print("[Client] Error registering with tracker: {}".format(e))
            return False

    def _unregister_from_tracker(self):
        """Unregister this peer from the tracker."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.tracker_host, self.tracker_port))

            command = "UNREGISTER {}".format(self.peer_id)
            sock.sendall(command.encode('utf-8'))

            sock.close()
            print("[Client] Unregistered from tracker")

        except Exception as e:
            print("[Client] Error unregistering: {}".format(e))

    def _send_heartbeat(self):
        """Send periodic heartbeat to tracker."""
        while self.running:
            time.sleep(60)  # Send heartbeat every minute

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.tracker_host, self.tracker_port))

                command = "HEARTBEAT {}".format(self.peer_id)
                sock.sendall(command.encode('utf-8'))

                sock.close()

            except Exception as e:
                print("[Client] Error sending heartbeat: {}".format(e))

    def _update_peer_list(self):
        """Get updated peer list from tracker."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.tracker_host, self.tracker_port))

            command = "GET_PEERS"
            sock.sendall(command.encode('utf-8'))

            response = sock.recv(4096).decode('utf-8')
            result = json.loads(response)

            sock.close()

            if result.get('status') == 'success':
                peers = result.get('peers', [])

                with self.lock:
                    for peer in peers:
                        peer_id = peer['peer_id']
                        if peer_id != self.peer_id:
                            self.peer_info[peer_id] = {
                                'ip': peer['ip'],
                                'port': peer['port']
                            }

                print("[Client] Updated peer list: {} peers available".format(len(self.peer_info)))

        except Exception as e:
            print("[Client] Error updating peer list: {}".format(e))

    def _listen_for_peers(self):
        """Listen for incoming P2P connections."""
        try:
            self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listen_socket.bind(('0.0.0.0', self.listen_port))
            self.listen_socket.listen(10)

            print("[Client] Listening for P2P connections on port {}".format(self.listen_port))

            while self.running:
                try:
                    conn, addr = self.listen_socket.accept()
                    print("[Client] Incoming P2P connection from {}:{}".format(addr[0], addr[1]))

                    # Handle peer in a new thread
                    peer_thread = threading.Thread(
                        target=self._handle_peer_connection,
                        args=(conn, addr),
                        daemon=True
                    )
                    peer_thread.start()

                except socket.error:
                    if self.running:
                        print("[Client] Socket error in listen loop")
                        break

        except Exception as e:
            print("[Client] Error in listen thread: {}".format(e))

    def _handle_peer_connection(self, conn, addr):
        """
        Handle incoming P2P connection.

        :param conn: Peer socket
        :param addr: Peer address
        """
        try:
            while self.running:
                data = conn.recv(4096)
                if not data:
                    break

                message = data.decode('utf-8')
                self._process_peer_message(message, addr)

        except Exception as e:
            print("[Client] Error handling peer connection: {}".format(e))
        finally:
            conn.close()

    def _process_peer_message(self, message, addr):
        """
        Process message from peer.

        :param message: Message string
        :param addr: Peer address
        """
        try:
            msg_data = json.loads(message)
            msg_type = msg_data.get('type')
            from_peer = msg_data.get('from')
            content = msg_data.get('content')

            if msg_type == 'direct':
                print("\n[{}] Direct message: {}".format(from_peer, content))
                self.messages.append({
                    'type': 'direct',
                    'from': from_peer,
                    'content': content,
                    'time': time.time()
                })

            elif msg_type == 'broadcast':
                print("\n[{}] Broadcast: {}".format(from_peer, content))
                self.messages.append({
                    'type': 'broadcast',
                    'from': from_peer,
                    'content': content,
                    'time': time.time()
                })

            print("> ", end='')
            sys.stdout.flush()

        except Exception as e:
            print("[Client] Error processing message: {}".format(e))

    def _connect_to_peer(self, peer_id):
        """
        Establish P2P connection to a peer.

        :param peer_id: Target peer ID
        :return: Socket connection or None
        """
        if peer_id not in self.peer_info:
            print("[Client] Peer {} not found".format(peer_id))
            return None

        try:
            peer = self.peer_info[peer_id]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((peer['ip'], peer['port']))

            with self.lock:
                self.peer_connections[peer_id] = sock

            print("[Client] Connected to peer: {}".format(peer_id))
            return sock

        except Exception as e:
            print("[Client] Error connecting to peer {}: {}".format(peer_id, e))
            return None

    def send_direct_message(self, peer_id, message):
        """
        Send direct message to a specific peer.

        :param peer_id: Target peer ID
        :param message: Message content
        """
        # Get or create connection to peer
        with self.lock:
            conn = self.peer_connections.get(peer_id)

        if not conn:
            conn = self._connect_to_peer(peer_id)
            if not conn:
                return

        try:
            msg_data = {
                'type': 'direct',
                'from': self.peer_id,
                'content': message
            }
            msg_json = json.dumps(msg_data)
            conn.sendall(msg_json.encode('utf-8'))

            print("[Client] Sent direct message to {}".format(peer_id))

        except Exception as e:
            print("[Client] Error sending message: {}".format(e))

    def broadcast_message(self, message):
        """
        Broadcast message to all known peers.

        :param message: Message content
        """
        msg_data = {
            'type': 'broadcast',
            'from': self.peer_id,
            'content': message
        }
        msg_json = json.dumps(msg_data)

        sent_count = 0

        for peer_id in list(self.peer_info.keys()):
            try:
                with self.lock:
                    conn = self.peer_connections.get(peer_id)

                if not conn:
                    conn = self._connect_to_peer(peer_id)
                    if not conn:
                        continue

                conn.sendall(msg_json.encode('utf-8'))
                sent_count += 1

            except Exception as e:
                print("[Client] Error broadcasting to {}: {}".format(peer_id, e))

        print("[Client] Broadcast sent to {} peers".format(sent_count))

    def _run_cli(self):
        """Run interactive command-line interface."""
        print("\n" + "=" * 60)
        print("Chat Commands:")
        print("  /msg <peer_id> <message>  - Send direct message")
        print("  /broadcast <message>      - Broadcast to all peers")
        print("  /peers                    - List available peers")
        print("  /refresh                  - Refresh peer list")
        print("  /history                  - Show message history")
        print("  /quit                     - Exit chat")
        print("=" * 60 + "\n")

        while self.running:
            try:
                # Python 2/3 compatibility
                try:
                    command = raw_input("> ").strip()
                except NameError:
                    command = input("> ").strip()

                if not command:
                    continue

                if command.startswith('/msg '):
                    parts = command.split(None, 2)
                    if len(parts) >= 3:
                        peer_id = parts[1]
                        message = parts[2]
                        self.send_direct_message(peer_id, message)
                    else:
                        print("Usage: /msg <peer_id> <message>")

                elif command.startswith('/broadcast '):
                    message = command[11:].strip()
                    if message:
                        self.broadcast_message(message)
                    else:
                        print("Usage: /broadcast <message>")

                elif command == '/peers':
                    with self.lock:
                        if self.peer_info:
                            print("\nAvailable peers:")
                            for peer_id, info in self.peer_info.items():
                                status = "connected" if peer_id in self.peer_connections else "available"
                                print("  {} - {}:{} [{}]".format(
                                    peer_id, info['ip'], info['port'], status))
                            print()
                        else:
                            print("No peers available")

                elif command == '/refresh':
                    self._update_peer_list()

                elif command == '/history':
                    if self.messages:
                        print("\nMessage history:")
                        for msg in self.messages[-20:]:  # Show last 20 messages
                            print("  [{}] {}: {}".format(
                                msg['type'], msg['from'], msg['content']))
                        print()
                    else:
                        print("No message history")

                elif command == '/quit':
                    print("Exiting...")
                    self.stop()
                    break

                else:
                    print("Unknown command. Type /help for available commands")

            except KeyboardInterrupt:
                print("\nExiting...")
                self.stop()
                break
            except Exception as e:
                print("Error: {}".format(e))


def main():
    """Main entry point for chat client."""
    parser = argparse.ArgumentParser(
        prog='ChatClient',
        description='P2P Chat Client for Hybrid Chat Application',
        epilog='Supports direct messaging and broadcast'
    )
    parser.add_argument('peer_id', help='Unique peer identifier')
    parser.add_argument('--port', type=int, default=6000,
                       help='Port to listen for P2P connections (default: 6000)')
    parser.add_argument('--tracker-host', default='127.0.0.1',
                       help='Tracker server host (default: 127.0.0.1)')
    parser.add_argument('--tracker-port', type=int, default=5000,
                       help='Tracker server port (default: 5000)')

    args = parser.parse_args()

    client = ChatClient(
        peer_id=args.peer_id,
        listen_port=args.port,
        tracker_host=args.tracker_host,
        tracker_port=args.tracker_port
    )

    try:
        client.start()
    except KeyboardInterrupt:
        print("\n[Client] Shutting down...")
        client.stop()


if __name__ == "__main__":
    main()
