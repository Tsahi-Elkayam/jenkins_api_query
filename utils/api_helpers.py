#!/usr/bin/env python3
"""
API Helpers Module for Jenkins Dashboard
This module provides helper functions for working with the Jenkins API.
"""

import requests
import json
import re
import time
from urllib.parse import urljoin

def get_jenkins_api_url(base_url, endpoint):
    """
    Build a proper Jenkins API URL

    Args:
        base_url: Base Jenkins URL
        endpoint: API endpoint

    Returns:
        str: Complete API URL
    """
    # Ensure base URL ends with a slash
    if not base_url.endswith('/'):
        base_url = f"{base_url}/"

    # Remove leading slash from endpoint if present
    if endpoint.startswith('/'):
        endpoint = endpoint[1:]

    # Join the URL parts
    return urljoin(base_url, endpoint)

def handle_api_response(response):
    """
    Process API response and handle different content types

    Args:
        response: Requests response object

    Returns:
        dict: Processed response data
    """
    # Check status code first
    if response.status_code != 200:
        return {"error": f"API call failed with status code: {response.status_code}"}

    # Process based on content type
    content_type = response.headers.get('Content-Type', '')

    if 'application/json' in content_type:
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response"}
    elif 'text/html' in content_type:
        return {"content": response.text, "html": True}
    else:
        return {"content": response.text}

def retry_api_call(func, max_retries=3, retry_delay=2, *args, **kwargs):
    """
    Retry an API call function with exponential backoff

    Args:
        func: Function to call
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries in seconds
        *args, **kwargs: Arguments to pass to the function

    Returns:
        Whatever the function returns
    """
    retries = 0
    while retries <= max_retries:
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            retries += 1
            if retries > max_retries:
                raise

            # Calculate delay with exponential backoff
            delay = retry_delay * (2 ** (retries - 1))
            print(f"API call failed, retrying in {delay} seconds... ({retries}/{max_retries})")
            time.sleep(delay)

def extract_crumb(session, jenkins_url):
    """
    Extract CSRF crumb from Jenkins for authenticated requests

    Args:
        session: Requests session object
        jenkins_url: Jenkins base URL

    Returns:
        dict: Crumb header dict or empty dict if not available
    """
    try:
        url = get_jenkins_api_url(jenkins_url, "crumbIssuer/api/json")
        response = session.get(url)

        if response.status_code == 200:
            data = response.json()
            if 'crumb' in data and 'crumbRequestField' in data:
                return {data['crumbRequestField']: data['crumb']}
    except Exception:
        pass

    return {}

def extract_jenkins_version(response):
    """
    Extract Jenkins version from API response headers

    Args:
        response: Requests response object

    Returns:
        str: Jenkins version or 'Unknown'
    """
    # Try X-Jenkins header first
    jenkins_version = response.headers.get('X-Jenkins', None)

    # If not found in headers, try looking in response content
    if not jenkins_version and 'jenkins-version' in response.headers:
        jenkins_version = response.headers.get('jenkins-version')

    # If still not found, try to extract from HTML if it's HTML response
    if not jenkins_version and 'text/html' in response.headers.get('Content-Type', ''):
        version_match = re.search(r'Jenkins ver\. ([0-9.]+)', response.text)
        if version_match:
            jenkins_version = version_match.group(1)

    return jenkins_version or 'Unknown'

def paginate_jenkins_api(session, base_url, endpoint, item_key='items', batch_size=100, max_items=1000):
    """
    Handle paginated Jenkins API responses

    Args:
        session: Requests session object
        base_url: Jenkins base URL
        endpoint: API endpoint
        item_key: JSON key containing the items
        batch_size: Number of items per request
        max_items: Maximum total items to retrieve

    Returns:
        list: Combined results from all pages
    """
    all_items = []
    offset = 0

    while offset < max_items:
        # Calculate the limit for this request
        limit = min(batch_size, max_items - offset)

        # Build the URL for this page
        paginated_endpoint = f"{endpoint}?start={offset}&limit={limit}"
        url = get_jenkins_api_url(base_url, paginated_endpoint)

        # Make the request
        response = session.get(url)
        if response.status_code != 200:
            break

        try:
            data = response.json()
            current_batch = data.get(item_key, [])
            all_items.extend(current_batch)

            # Break if we got fewer items than requested (end of data)
            if len(current_batch) < limit:
                break

            offset += limit
        except Exception:
            break

    return all_items

def build_tree_parameter(fields, depth=1):
    """
    Build a Jenkins API tree parameter for selective field retrieval

    Args:
        fields: Dictionary mapping field names to subfields
               Use empty list for a field with no subfields
               Use nested dict for deeper levels
        depth: Current depth level (internal use)

    Returns:
        str: Formatted tree parameter
    """
    if depth > 10:  # Prevent excessive recursion
        return ""

    parts = []

    for field, subfields in fields.items():
        if not subfields:  # No subfields
            parts.append(field)
        elif isinstance(subfields, list):
            parts.append(f"{field}[{','.join(subfields)}]")
        elif isinstance(subfields, dict):
            subtree = build_tree_parameter(subfields, depth + 1)
            parts.append(f"{field}[{subtree}]")

    return ','.join(parts)
