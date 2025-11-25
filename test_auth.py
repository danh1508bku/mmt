#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for HTTP authentication system
Tests RFC 2617, 7235, and 6265 implementation
"""

import urllib
import urllib2
import base64

def test_proxy_auth():
    """Test Proxy Authentication (RFC 7235)"""
    print("\n=== Testing Proxy Authentication (RFC 7235) ===")

    # Test without proxy auth - should get 407
    try:
        req = urllib2.Request("http://127.0.0.1:8080/")
        response = urllib2.urlopen(req)
        print("FAIL: Should have received 407")
    except urllib2.HTTPError as e:
        if e.code == 407:
            print("PASS: Received 407 Proxy Authentication Required")
            print("Headers:", e.headers.dict)
        else:
            print("FAIL: Received {} instead of 407".format(e.code))

    # Test with valid proxy auth
    try:
        proxy_auth = base64.b64encode("admin:password")
        req = urllib2.Request("http://127.0.0.1:8080/")
        req.add_header("Proxy-Authorization", "Basic " + proxy_auth)
        response = urllib2.urlopen(req)
        print("PASS: Proxy authentication successful")
    except urllib2.HTTPError as e:
        print("Status:", e.code)
        print("Headers:", e.headers.dict)

def test_login_cookie():
    """Test Login with Cookie Session (RFC 2617 + 6265)"""
    print("\n=== Testing Login with Cookie Session (RFC 2617 + 6265) ===")

    # Test POST /login with wrong credentials - should get 401
    print("\n1. Testing wrong credentials...")
    data = urllib.urlencode({'username': 'wrong', 'password': 'wrong'})
    req = urllib2.Request("http://127.0.0.1:9000/login", data)
    try:
        response = urllib2.urlopen(req)
        print("FAIL: Should have received 401")
    except urllib2.HTTPError as e:
        if e.code == 401:
            print("PASS: Received 401 Unauthorized")
            if 'www-authenticate' in e.headers.dict:
                print("PASS: WWW-Authenticate header present:", e.headers.dict['www-authenticate'])
        else:
            print("FAIL: Received {} instead of 401".format(e.code))

    # Test POST /login with correct credentials
    print("\n2. Testing correct credentials...")
    data = urllib.urlencode({'username': 'admin', 'password': 'password'})
    req = urllib2.Request("http://127.0.0.1:9000/login", data)
    try:
        response = urllib2.urlopen(req)
        print("PASS: Login successful")
        if 'set-cookie' in response.headers.dict:
            print("PASS: Set-Cookie header present:", response.headers.dict['set-cookie'])
            cookie = response.headers.dict['set-cookie']

            # Extract auth cookie
            auth_cookie = None
            for part in cookie.split(';'):
                if 'auth=' in part:
                    auth_cookie = part.strip()

            if auth_cookie:
                print("\n3. Testing access with cookie...")
                req2 = urllib2.Request("http://127.0.0.1:9000/")
                req2.add_header("Cookie", auth_cookie)
                response2 = urllib2.urlopen(req2)
                print("PASS: Accessed / with cookie, status:", response2.code)
    except Exception as e:
        print("Error:", e)

def test_protected_resource():
    """Test Protected Resource without Cookie (RFC 2617)"""
    print("\n=== Testing Protected Resource without Cookie (RFC 2617) ===")

    try:
        req = urllib2.Request("http://127.0.0.1:9000/")
        response = urllib2.urlopen(req)
        print("FAIL: Should have received 401")
    except urllib2.HTTPError as e:
        if e.code == 401:
            print("PASS: Received 401 Unauthorized")
            if 'www-authenticate' in e.headers.dict:
                print("PASS: WWW-Authenticate header present:", e.headers.dict['www-authenticate'])
        else:
            print("FAIL: Received {} instead of 401".format(e.code))

if __name__ == "__main__":
    print("=" * 60)
    print("HTTP Authentication Test Suite")
    print("=" * 60)

    print("\nNOTE: Make sure backend is running on port 9000")
    print("      python start_backend.py --server-ip 0.0.0.0 --server-port 9000")
    print("\nNOTE: Make sure proxy is running on port 8080")
    print("      python start_proxy.py --server-ip 0.0.0.0 --server-port 8080")

    raw_input("\nPress Enter to continue...")

    # Test direct backend (no proxy)
    test_protected_resource()
    test_login_cookie()

    # Test via proxy
    test_proxy_auth()

    print("\n" + "=" * 60)
    print("Test Suite Completed")
    print("=" * 60)
