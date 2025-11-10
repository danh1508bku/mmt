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
daemon.request
~~~~~~~~~~~~~~~~~

This module provides a Request object to manage and persist 
request settings (cookies, auth, proxies).
"""
from .dictionary import CaseInsensitiveDict

class Request():
    """The fully mutable "class" `Request <Request>` object,
    containing the exact bytes that will be sent to the server.

    Instances are generated from a "class" `Request <Request>` object, and
    should not be instantiated manually; doing so may produce undesirable
    effects.

    Usage::

      >>> import deamon.request
      >>> req = request.Request()
      ## Incoming message obtain aka. incoming_msg
      >>> r = req.prepare(incoming_msg)
      >>> r
      <Request>
    """
    __attrs__ = [
        "method",
        "url",
        "headers",
        "body",
        "reason",
        "cookies",
        "body",
        "routes",
        "hook",
    ]

    def __init__(self):
        #: HTTP verb to send to the server.
        self.method = None
        #: HTTP URL to send the request to.
        self.url = None
        #: dictionary of HTTP headers.
        self.headers = None
        #: HTTP path
        self.path = None        
        # The cookies set used to create Cookie header
        self.cookies = None
        #: request body to send to the server.
        self.body = None
        #: Routes
        self.routes = {}
        #: Hook point for routed mapped-path
        self.hook = None

    def extract_request_line(self, request):
        try:
            lines = request.splitlines()
            first_line = lines[0]
            method, path, version = first_line.split()

            if path == '/':
                path = '/index.html'
        except Exception:
            return None, None

        return method, path, version
             
    def prepare_headers(self, request):
        """Prepares the given HTTP headers."""
        lines = request.split('\r\n')
        headers = {}
        for line in lines[1:]:
            if ': ' in line:
                key, val = line.split(': ', 1)
                headers[key.lower()] = val
        return headers

    def prepare(self, request, routes=None):
        """Prepares the entire request with the given parameters."""

        # Prepare the request line from the request header
        self.method, self.path, self.version = self.extract_request_line(request)
        print("[Request] {} path {} version {}".format(self.method, self.path, self.version))

        #
        # @bksysnet Preapring the webapp hook with WeApRous instance
        # The default behaviour with HTTP server is empty routed
        #
        # TODO manage the webapp hook in this mounting point
        #

        if not routes == {}:
            self.routes = routes
            self.hook = routes.get((self.method, self.path))
            #
            # self.hook manipulation goes here
            # ...
            #

        self.headers = self.prepare_headers(request)

        # Parse cookies from Cookie header
        cookie_header = self.headers.get('cookie', '')
        self.cookies = self.parse_cookies(cookie_header)

        # Parse body for POST/PUT requests
        self.body = self.parse_body(request)

        return

    def parse_cookies(self, cookie_string):
        """Parse cookies from Cookie header string.

        Implements RFC 6265 cookie parsing.

        :param cookie_string: Cookie header value
        :return: Dictionary of cookie name-value pairs
        """
        cookies = {}
        if not cookie_string:
            return cookies

        # Split by semicolon and parse each cookie
        for cookie in cookie_string.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                name, value = cookie.split('=', 1)
                cookies[name.strip()] = value.strip()

        return cookies

    def parse_body(self, request):
        """Parse request body from HTTP request.

        Extracts the body content after the header section.

        :param request: Full HTTP request string
        :return: Body content as string
        """
        # HTTP request format: headers\r\n\r\nbody
        if '\r\n\r\n' in request:
            _, body = request.split('\r\n\r\n', 1)
            return body
        return ''

    def parse_form_data(self, body):
        """Parse URL-encoded form data.

        :param body: URL-encoded body string
        :return: Dictionary of form fields
        """
        form_data = {}
        if not body:
            return form_data

        for pair in body.split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                # URL decode
                import urllib
                try:
                    from urllib import unquote
                except ImportError:
                    from urllib.parse import unquote
                form_data[unquote(key)] = unquote(value)

        return form_data

    def prepare_body(self, data, files, json=None):
        """Prepare request body with content length."""
        if self.body:
            self.prepare_content_length(self.body)
        return

    def prepare_content_length(self, body):
        """Set Content-Length header."""
        if body:
            self.headers["Content-Length"] = str(len(body))
        else:
            self.headers["Content-Length"] = "0"
        return

    def prepare_auth(self, auth, url=""):
        """Prepare request authentication.

        :param auth: Authentication credentials
        :param url: Target URL
        """
        # Basic authentication implementation
        if auth:
            import base64
            username, password = auth
            credentials = "{}:{}".format(username, password)
            b64_credentials = base64.b64encode(credentials.encode()).decode()
            self.headers["Authorization"] = "Basic {}".format(b64_credentials)
        return

    def prepare_cookies(self, cookies):
        """Set Cookie header from dictionary.

        :param cookies: Dictionary of cookie name-value pairs
        """
        if cookies:
            cookie_string = '; '.join(['{}={}'.format(k, v) for k, v in cookies.items()])
            self.headers["Cookie"] = cookie_string
