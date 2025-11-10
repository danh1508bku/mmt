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
start_authapp
~~~~~~~~~~~~~~~~~

This module provides an authentication web application using the WeApRous framework.

It implements:
- Task 1A: Authentication Handling - POST /login with username/password validation
- Task 1B: Cookie-based Access Control - GET / with cookie validation

RFC 6265 - HTTP Cookie:
    Set-Cookie: cookie-name=cookie-value; Path=/; HttpOnly; Secure

RFC 7235 - HTTP Authentication:
    401 Unauthorized MUST include WWW-Authenticate header
"""

import os
import argparse

from daemon.weaprous import WeApRous
from daemon.response import Response

PORT = 8000  # Default port

app = WeApRous()


@app.route('/login', methods=['POST'])
def login(headers=None, body=None, cookies=None, request=None):
    """
    Handle user login via POST request.

    Task 1A - Authentication Handling:
    - If username=admin and password=password: return index.html with Set-Cookie: auth=true
    - If invalid credentials: return 401 Unauthorized

    :param headers: Request headers dictionary
    :param body: Request body string
    :param cookies: Request cookies dictionary
    :param request: Full request object
    :return: Response dictionary with status, cookies, and body
    """
    print("[AuthApp] POST /login - Processing login request")

    # Parse form data from body
    if body:
        form_data = request.parse_form_data(body)
        username = form_data.get('username', '')
        password = form_data.get('password', '')

        print("[AuthApp] Login attempt - username: {}".format(username))

        # Task 1A: Validate credentials
        if username == 'admin' and password == 'password':
            print("[AuthApp] Login successful - Setting auth cookie")

            # Read index.html
            try:
                with open('www/index.html', 'rb') as f:
                    index_content = f.read()

                # Return success response with Set-Cookie header (RFC 6265)
                return {
                    'status': 200,
                    'reason': 'OK',
                    'cookies': {
                        'auth': {
                            'value': 'true',
                            'path': '/',
                            'httponly': True,
                            # 'secure': True  # Uncomment for HTTPS
                        }
                    },
                    'content_type': 'text/html',
                    'body': index_content
                }
            except Exception as e:
                print("[AuthApp] Error reading index.html: {}".format(e))
                return {
                    'status': 500,
                    'reason': 'Internal Server Error',
                    'body': '500 Internal Server Error'
                }

    # Task 1A: Invalid credentials - return 401 Unauthorized (RFC 7235)
    print("[AuthApp] Login failed - Invalid credentials")
    resp = Response()
    return {
        'raw': resp.build_unauthorized(realm="Authentication Required")
    }


@app.route('/', methods=['GET'])
def index(headers=None, body=None, cookies=None, request=None):
    """
    Handle root path GET request.

    Task 1B - Cookie-based Access Control:
    - If cookie auth=true exists: return index.html
    - If cookie missing/invalid: return 401 Unauthorized

    :param headers: Request headers dictionary
    :param body: Request body string
    :param cookies: Request cookies dictionary
    :param request: Full request object
    :return: Response dictionary with status and body
    """
    print("[AuthApp] GET / - Checking authentication")

    # Task 1B: Check for auth cookie
    if cookies and cookies.get('auth') == 'true':
        print("[AuthApp] Authenticated - Serving index.html")

        # Read and serve index.html
        try:
            with open('www/index.html', 'rb') as f:
                index_content = f.read()

            return {
                'status': 200,
                'reason': 'OK',
                'content_type': 'text/html',
                'body': index_content
            }
        except Exception as e:
            print("[AuthApp] Error reading index.html: {}".format(e))
            return {
                'status': 500,
                'reason': 'Internal Server Error',
                'body': '500 Internal Server Error'
            }

    # Task 1B: Missing or invalid auth cookie - return 401 Unauthorized (RFC 7235)
    print("[AuthApp] Authentication required - No valid auth cookie")
    resp = Response()
    return {
        'raw': resp.build_unauthorized(realm="Authentication Required")
    }


@app.route('/login', methods=['GET'])
def login_page(headers=None, body=None, cookies=None, request=None):
    """
    Serve the login page.

    :param headers: Request headers dictionary
    :param body: Request body string
    :param cookies: Request cookies dictionary
    :param request: Full request object
    :return: Response dictionary with login form
    """
    print("[AuthApp] GET /login - Serving login page")

    try:
        with open('www/login.html', 'rb') as f:
            login_content = f.read()

        return {
            'status': 200,
            'reason': 'OK',
            'content_type': 'text/html',
            'body': login_content
        }
    except Exception as e:
        print("[AuthApp] Error reading login.html: {}".format(e))
        return {
            'status': 404,
            'reason': 'Not Found',
            'body': '404 Not Found'
        }


@app.route('/logout', methods=['GET', 'POST'])
def logout(headers=None, body=None, cookies=None, request=None):
    """
    Handle logout - clear auth cookie.

    :param headers: Request headers dictionary
    :param body: Request body string
    :param cookies: Request cookies dictionary
    :param request: Full request object
    :return: Response dictionary with cleared cookie
    """
    print("[AuthApp] Logout - Clearing auth cookie")

    try:
        with open('www/login.html', 'rb') as f:
            login_content = f.read()

        return {
            'status': 200,
            'reason': 'OK',
            'cookies': {
                'auth': {
                    'value': '',
                    'path': '/',
                    'max_age': 0  # Expire immediately
                }
            },
            'content_type': 'text/html',
            'body': login_content
        }
    except Exception as e:
        print("[AuthApp] Error reading login.html: {}".format(e))
        return {
            'status': 200,
            'reason': 'OK',
            'body': 'Logged out successfully'
        }


if __name__ == "__main__":
    # Parse command-line arguments to configure server IP and port
    parser = argparse.ArgumentParser(
        prog='AuthApp',
        description='Authentication Web Application with Cookie Session',
        epilog='Implements RFC 6265 (HTTP Cookie) and RFC 7235 (HTTP Authentication)'
    )
    parser.add_argument('--server-ip', default='0.0.0.0',
                       help='Server IP address (default: 0.0.0.0)')
    parser.add_argument('--server-port', type=int, default=PORT,
                       help='Server port (default: 8000)')

    args = parser.parse_args()
    ip = args.server_ip
    port = args.server_port

    print("=" * 60)
    print("WeApRous Authentication Application")
    print("=" * 60)
    print("Task 1A: POST /login - Authentication Handling")
    print("  Credentials: username=admin, password=password")
    print("Task 1B: GET / - Cookie-based Access Control")
    print("  Requires: Cookie auth=true")
    print("=" * 60)
    print("Starting server on {}:{}".format(ip, port))
    print("=" * 60)

    # Prepare and launch the authentication application
    app.prepare_address(ip, port)
    app.run()
