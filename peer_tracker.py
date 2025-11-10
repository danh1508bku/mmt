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
peer_tracker
~~~~~~~~~~~~~~~~~

This module provides a peer tracker server for the hybrid chat application.

The tracker server manages peer registration and discovery:
- Peer registration: peers send their IP and port to the tracker
- Tracker update: tracker maintains list of active peers
- Peer discovery: peers can request the list of available peers
- Connection setup: peers use this list to establish P2P connections

Protocol Commands:
- REGISTER <peer_id> <ip> <port> - Register a new peer
- GET_PEERS - Get list of all active peers
- UNREGISTER <peer_id> - Unregister a peer
- HEARTBEAT <peer_id> - Keep-alive signal from peer
"""

import socket
import threading
import json
import time
import argparse


class PeerTracker:
    """Peer Tracker Server for managing peer connections."""

    def __init__(self, host='0.0.0.0', port=5000):
        """
        Initialize the peer tracker.

        :param host: Host address to bind
        :param port: Port to listen on
        """
        self.host = host
        self.port = port
        self.peers = {}  # peer_id -> {'ip': ip, 'port': port, 'last_seen': timestamp}
        self.lock = threading.Lock()
        self.server_socket = None
        self.running = False

        # Timeout for inactive peers (seconds)
        self.peer_timeout = 300  # 5 minutes

    def start(self):
        """Start the tracker server."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(50)
            self.running = True

            print("=" * 60)
            print("Peer Tracker Server Started")
            print("=" * 60)
            print("Listening on {}:{}".format(self.host, self.port))
            print("=" * 60)

            # Start cleanup thread for inactive peers
            cleanup_thread = threading.Thread(target=self._cleanup_inactive_peers, daemon=True)
            cleanup_thread.start()

            # Accept connections
            while self.running:
                try:
                    conn, addr = self.server_socket.accept()
                    print("[Tracker] Connection from {}:{}".format(addr[0], addr[1]))

                    # Handle client in a new thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(conn, addr),
                        daemon=True
                    )
                    client_thread.start()

                except socket.error as e:
                    if self.running:
                        print("[Tracker] Socket error: {}".format(e))

        except Exception as e:
            print("[Tracker] Error starting server: {}".format(e))
        finally:
            self.stop()

    def stop(self):
        """Stop the tracker server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("[Tracker] Server stopped")

    def _handle_client(self, conn, addr):
        """
        Handle a client connection.

        :param conn: Client socket
        :param addr: Client address
        """
        try:
            # Receive message
            data = conn.recv(4096).decode('utf-8')
            if not data:
                return

            print("[Tracker] Received: {}".format(data.strip()))

            # Parse command
            parts = data.strip().split()
            if not parts:
                self._send_response(conn, {'status': 'error', 'message': 'Empty command'})
                return

            command = parts[0].upper()

            if command == 'REGISTER':
                self._handle_register(conn, parts)
            elif command == 'GET_PEERS':
                self._handle_get_peers(conn, parts)
            elif command == 'UNREGISTER':
                self._handle_unregister(conn, parts)
            elif command == 'HEARTBEAT':
                self._handle_heartbeat(conn, parts)
            else:
                self._send_response(conn, {'status': 'error', 'message': 'Unknown command'})

        except Exception as e:
            print("[Tracker] Error handling client: {}".format(e))
            self._send_response(conn, {'status': 'error', 'message': str(e)})
        finally:
            conn.close()

    def _handle_register(self, conn, parts):
        """
        Handle REGISTER command.

        Format: REGISTER <peer_id> <ip> <port>
        """
        if len(parts) < 4:
            self._send_response(conn, {
                'status': 'error',
                'message': 'Invalid format. Use: REGISTER <peer_id> <ip> <port>'
            })
            return

        peer_id = parts[1]
        peer_ip = parts[2]
        peer_port = int(parts[3])

        with self.lock:
            self.peers[peer_id] = {
                'ip': peer_ip,
                'port': peer_port,
                'last_seen': time.time()
            }

        print("[Tracker] Registered peer: {} ({}:{})".format(peer_id, peer_ip, peer_port))
        print("[Tracker] Total active peers: {}".format(len(self.peers)))

        self._send_response(conn, {
            'status': 'success',
            'message': 'Peer registered successfully',
            'peer_count': len(self.peers)
        })

    def _handle_get_peers(self, conn, parts):
        """
        Handle GET_PEERS command.

        Returns list of all active peers.
        """
        with self.lock:
            peer_list = [
                {
                    'peer_id': peer_id,
                    'ip': info['ip'],
                    'port': info['port']
                }
                for peer_id, info in self.peers.items()
            ]

        print("[Tracker] Sending peer list ({} peers)".format(len(peer_list)))

        self._send_response(conn, {
            'status': 'success',
            'peers': peer_list,
            'peer_count': len(peer_list)
        })

    def _handle_unregister(self, conn, parts):
        """
        Handle UNREGISTER command.

        Format: UNREGISTER <peer_id>
        """
        if len(parts) < 2:
            self._send_response(conn, {
                'status': 'error',
                'message': 'Invalid format. Use: UNREGISTER <peer_id>'
            })
            return

        peer_id = parts[1]

        with self.lock:
            if peer_id in self.peers:
                del self.peers[peer_id]
                print("[Tracker] Unregistered peer: {}".format(peer_id))
                print("[Tracker] Total active peers: {}".format(len(self.peers)))
                self._send_response(conn, {
                    'status': 'success',
                    'message': 'Peer unregistered successfully'
                })
            else:
                self._send_response(conn, {
                    'status': 'error',
                    'message': 'Peer not found'
                })

    def _handle_heartbeat(self, conn, parts):
        """
        Handle HEARTBEAT command.

        Format: HEARTBEAT <peer_id>
        """
        if len(parts) < 2:
            self._send_response(conn, {
                'status': 'error',
                'message': 'Invalid format. Use: HEARTBEAT <peer_id>'
            })
            return

        peer_id = parts[1]

        with self.lock:
            if peer_id in self.peers:
                self.peers[peer_id]['last_seen'] = time.time()
                self._send_response(conn, {
                    'status': 'success',
                    'message': 'Heartbeat received'
                })
            else:
                self._send_response(conn, {
                    'status': 'error',
                    'message': 'Peer not found'
                })

    def _send_response(self, conn, response_dict):
        """
        Send JSON response to client.

        :param conn: Client socket
        :param response_dict: Response dictionary to send
        """
        try:
            response_json = json.dumps(response_dict)
            conn.sendall(response_json.encode('utf-8'))
        except Exception as e:
            print("[Tracker] Error sending response: {}".format(e))

    def _cleanup_inactive_peers(self):
        """
        Periodically cleanup inactive peers.

        Runs in a background thread.
        """
        while self.running:
            time.sleep(60)  # Check every minute

            current_time = time.time()
            with self.lock:
                inactive_peers = [
                    peer_id for peer_id, info in self.peers.items()
                    if current_time - info['last_seen'] > self.peer_timeout
                ]

                for peer_id in inactive_peers:
                    print("[Tracker] Removing inactive peer: {}".format(peer_id))
                    del self.peers[peer_id]

                if inactive_peers:
                    print("[Tracker] Total active peers: {}".format(len(self.peers)))


def main():
    """Main entry point for peer tracker server."""
    parser = argparse.ArgumentParser(
        prog='PeerTracker',
        description='Peer Tracker Server for Hybrid Chat Application',
        epilog='Manages peer registration and discovery for P2P chat'
    )
    parser.add_argument('--host', default='0.0.0.0',
                       help='Host address to bind (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000,
                       help='Port to listen on (default: 5000)')

    args = parser.parse_args()

    tracker = PeerTracker(host=args.host, port=args.port)

    try:
        tracker.start()
    except KeyboardInterrupt:
        print("\n[Tracker] Shutting down...")
        tracker.stop()


if __name__ == "__main__":
    main()
