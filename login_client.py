#!/usr/bin/env python3
"""
Jenkins Login Client
This module provides functionality to authenticate with Jenkins.
"""

import requests
import urllib3
import json
from utils.api_helpers import get_jenkins_api_url, extract_crumb, extract_jenkins_version

class JenkinsClient:
    """Simple Jenkins client for authentication and basic API calls"""

    def __init__(self, skip_ssl_verify=True):
        """
        Initialize Jenkins client

        Args:
            skip_ssl_verify: Whether to skip SSL certificate verification
        """
        self.session = requests.Session()
        self.url = None
        self.username = None
        self.crumb = None
        self.debug_mode = True  # Set to False in production

        # Disable SSL verification if requested
        if skip_ssl_verify:
            self.session.verify = False
            # Suppress SSL warnings
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def login(self, url, username, password):
        """
        Login to Jenkins and return basic information

        Args:
            url: Jenkins URL
            username: Username for authentication
            password: Password for authentication

        Returns:
            dict: Login result information
        """
        try:
            # Ensure URL has correct format
            if not (url.startswith('http://') or url.startswith('https://')):
                url = f'https://{url}'

            # Add trailing slash if missing
            if not url.endswith('/'):
                url = f'{url}/'

            self.url = url
            self.username = username

            # Set auth for the session
            self.session.auth = (username, password)

            # Check if we can connect
            print(f"Connecting to Jenkins at {url}")
            response = self.session.get(f"{url}api/json")

            if response.status_code == 200:
                server_info = response.json()
                print(f"Successfully connected to Jenkins API")

                # Get user info
                user_response = self.session.get(f"{url}me/api/json")
                if user_response.status_code == 200:
                    user_info = user_response.json()
                    print(f"Successfully retrieved user info for {user_info.get('fullName', username)}")
                else:
                    user_info = {}
                    print(f"Failed to retrieve user info: {user_response.status_code}")

                # Get version from headers or API
                jenkins_version = extract_jenkins_version(response)
                print(f"Jenkins version: {jenkins_version}")

                # Get CSRF crumb if available
                self.crumb = extract_crumb(self.session, self.url)
                if self.crumb:
                    print("Successfully obtained CSRF crumb")
                else:
                    print("No CSRF crumb available or couldn't retrieve it")

                # Return the basic information
                return {
                    'success': True,
                    'url': url,
                    'user': user_info.get('fullName', username),
                    'version': jenkins_version
                }
            else:
                print(f"Failed to connect to Jenkins API: {response.status_code}")
                return {
                    'success': False,
                    'message': f"Login failed with status code: {response.status_code}"
                }

        except requests.exceptions.RequestException as e:
            print(f"Connection error: {str(e)}")
            return {
                'success': False,
                'message': f"Connection error: {str(e)}"
            }

    def get_api_url(self, endpoint):
        """
        Get full API URL for the given endpoint

        Args:
            endpoint: API endpoint

        Returns:
            str: Full API URL
        """
        return get_jenkins_api_url(self.url, endpoint)

    def get_crumb_header(self):
        """
        Get CSRF crumb header for POST requests

        Returns:
            dict: Crumb header or empty dict if not available
        """
        return self.crumb or {}

    def fetch_jenkins_data(self, endpoint, params=None):
        """
        Fetch data from Jenkins API with detailed error handling

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            dict: Response data or error information
        """
        url = self.get_api_url(endpoint)

        if self.debug_mode:
            print(f"Fetching data from: {url}")

        try:
            # Add headers if we have a crumb
            headers = self.get_crumb_header()

            # Make the request
            response = self.session.get(url, params=params, headers=headers)

            if response.status_code == 200:
                # Try to parse JSON
                try:
                    return response.json()
                except json.JSONDecodeError:
                    # If not JSON, return the text content
                    return {"content": response.text}
            else:
                if self.debug_mode:
                    print(f"Error fetching {url}: HTTP {response.status_code}")
                return {"error": f"HTTP error {response.status_code}"}

        except requests.RequestException as e:
            if self.debug_mode:
                print(f"Request error for {url}: {str(e)}")
            return {"error": f"Request failed: {str(e)}"}
