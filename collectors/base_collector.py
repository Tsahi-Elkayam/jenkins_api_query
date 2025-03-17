#!/usr/bin/env python3
"""
Base Collector Module for Jenkins Dashboard
This module provides a base class for all data collectors.
"""

import requests
import re
from datetime import datetime

class BaseCollector:
    """Base class for all Jenkins data collectors"""

    def __init__(self, client):
        """
        Initialize with a JenkinsClient instance

        Args:
            client: Authenticated JenkinsClient instance
        """
        self.client = client
        self.session = client.session
        self.url = client.url

    def fetch_jenkins_data(self, endpoint, params=None, depth=0):
        """
        Fetch data from Jenkins API with error handling

        Args:
            endpoint: API endpoint (relative to Jenkins URL)
            params: Query parameters
            depth: API depth parameter

        Returns:
            dict: JSON response or error dictionary
        """
        try:
            # Build URL
            if endpoint.startswith('http'):
                url = endpoint
            else:
                # Add leading slash if missing
                if not endpoint.startswith('/'):
                    endpoint = f"/{endpoint}"
                url = f"{self.url.rstrip('/')}{endpoint}"

            # Add depth parameter if specified
            if params is None:
                params = {}
            if depth > 0 and 'depth' not in params:
                params['depth'] = depth

            # Make the request
            response = self.session.get(url, params=params)

            # Handle response
            if response.status_code == 200:
                if 'application/json' in response.headers.get('Content-Type', ''):
                    return response.json()
                return {"content": response.text, "html": True}
            else:
                return {"error": f"Failed with status code: {response.status_code}"}

        except requests.exceptions.RequestException as e:
            return {"error": f"Connection error: {str(e)}"}
        except Exception as e:
            return {"error": f"Error: {str(e)}"}

    def extract_property(self, html, key):
        """
        Extract a property from HTML content

        Args:
            html: HTML content
            key: Property key to extract

        Returns:
            str: Property value or 'Unknown'
        """
        try:
            # Find the property in the page
            if key not in html:
                return "Unknown"

            patterns = [
                f"{key}</td><td[^>]*>(.*?)</td>",
                f"{key}:</td><td[^>]*>(.*?)</td>",
                f"{key}:(.*?)<",
            ]

            for pattern in patterns:
                match = re.search(pattern, html, re.DOTALL)
                if match:
                    value = match.group(1).strip()
                    # Clean up HTML tags
                    value = re.sub(r'<[^>]+>', '', value)

                    # Clean up "Hidden value" text
                    if "Hidden value, click to show this value" in value:
                        parts = value.split("Hidden value, click to show this value")
                        if len(parts) > 1 and parts[1].strip():
                            return parts[1].strip()

                    return value

            return "Unknown"
        except Exception:
            return "Unknown"

    def format_timestamp(self, timestamp):
        """
        Format timestamp to human-readable date

        Args:
            timestamp: Milliseconds since epoch

        Returns:
            str: Formatted date and time
        """
        try:
            # Convert milliseconds to seconds
            timestamp_sec = timestamp / 1000
            dt = datetime.fromtimestamp(timestamp_sec)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            return 'N/A'

    def format_duration(self, duration):
        """
        Format duration to human-readable time

        Args:
            duration: Duration in milliseconds

        Returns:
            str: Formatted duration
        """
        try:
            # Convert milliseconds to seconds
            seconds = duration / 1000
            # Format duration
            if seconds < 60:
                return f"{seconds:.1f} sec"
            elif seconds < 3600:
                minutes = seconds / 60
                return f"{minutes:.1f} min"
            else:
                hours = seconds / 3600
                return f"{hours:.1f} hrs"
        except (ValueError, TypeError):
            return 'N/A'

    def format_bytes(self, bytes_value, precision=2):
        """
        Format bytes to human-readable size

        Args:
            bytes_value: Size in bytes
            precision: Number of decimal places

        Returns:
            str: Formatted size string
        """
        try:
            if bytes_value == 0:
                return "0 B"

            size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
            i = 0

            while bytes_value >= 1024 and i < len(size_names) - 1:
                bytes_value /= 1024
                i += 1

            return f"{bytes_value:.{precision}f} {size_names[i]}"
        except Exception:
            return "Unknown"
