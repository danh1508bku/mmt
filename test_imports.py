#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify all imports work correctly.
"""

import sys

print("=" * 60)
print("Testing Python Compatibility and Imports")
print("=" * 60)
print("Python version: {}".format(sys.version))
print()

# Test daemon imports
try:
    from daemon.dictionary import CaseInsensitiveDict
    print("✓ daemon.dictionary imported successfully")
except Exception as e:
    print("✗ daemon.dictionary failed: {}".format(e))

try:
    from daemon.request import Request
    print("✓ daemon.request imported successfully")
except Exception as e:
    print("✗ daemon.request failed: {}".format(e))

try:
    from daemon.response import Response
    print("✓ daemon.response imported successfully")
except Exception as e:
    print("✗ daemon.response failed: {}".format(e))

try:
    from daemon.httpadapter import HttpAdapter
    print("✓ daemon.httpadapter imported successfully")
except Exception as e:
    print("✗ daemon.httpadapter failed: {}".format(e))

try:
    from daemon.weaprous import WeApRous
    print("✓ daemon.weaprous imported successfully")
except Exception as e:
    print("✗ daemon.weaprous failed: {}".format(e))

try:
    from daemon import create_backend
    print("✓ daemon.backend imported successfully")
except Exception as e:
    print("✗ daemon.backend failed: {}".format(e))

try:
    from daemon import create_proxy
    print("✓ daemon.proxy imported successfully")
except Exception as e:
    print("✗ daemon.proxy failed: {}".format(e))

# Test standalone modules
try:
    import peer_tracker
    print("✓ peer_tracker imported successfully")
except Exception as e:
    print("✗ peer_tracker failed: {}".format(e))

try:
    import chat_client
    print("✓ chat_client imported successfully")
except Exception as e:
    print("✗ chat_client failed: {}".format(e))

try:
    import start_authapp
    print("✓ start_authapp imported successfully")
except Exception as e:
    print("✗ start_authapp failed: {}".format(e))

try:
    from apps.sampleApp import create_sampleapp
    print("✓ apps.sampleApp imported successfully")
except Exception as e:
    print("✗ apps.sampleApp failed: {}".format(e))

print()
print("=" * 60)
print("All imports tested!")
print("=" * 60)
