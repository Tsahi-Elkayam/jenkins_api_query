#!/usr/bin/env python3
"""
Jenkins Security Configuration Display Module
This module displays Jenkins security configuration information.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader

def display_security_config(info):
    """
    Display Jenkins security configuration

    Args:
        info (dict): Security configuration information

    Returns:
        bool: Success status
    """
    if "error" in info:
        print(f"{Colors.ERROR}Error: {info['error']}{Colors.RESET}")
        return False

    # Display main security settings
    security_data = [
        ['Authorization Strategy', info.get('authorization_strategy', 'Unknown')],
        ['Security Realm', info.get('security_realm', 'Unknown')],
        ['CSRF Protection', 'Enabled' if info.get('csrf_protection', False) else 'Disabled'],
        ['Agent Security', info.get('agent_security', 'Unknown')],
        ['API Token Settings', info.get('api_token_settings', 'Unknown')]
    ]

    # Color the critical security settings
    for i, row in enumerate(security_data):
        if row[0] == 'CSRF Protection' and row[1] == 'Disabled':
            security_data[i][1] = f"{Colors.ERROR}Disabled{Colors.RESET}"
        elif row[0] == 'CSRF Protection' and row[1] == 'Enabled':
            security_data[i][1] = f"{Colors.STATUS_SUCCESS}Enabled{Colors.RESET}"

    print(format_subheader("Jenkins Security Configuration"))
    print(tabulate(security_data, headers=['Setting', 'Value'], tablefmt='grid'))

    # Display security headers
    headers = info.get('headers', {})
    if headers and headers != "Unknown":
        headers_data = [
            ['Content-Security-Policy', 'Present' if headers.get('content_security_policy', False) else 'Missing'],
            ['X-Content-Type-Options', 'Present' if headers.get('x_content_type_options', False) else 'Missing'],
            ['X-Frame-Options', 'Present' if headers.get('x_frame_options', False) else 'Missing']
        ]

        # Color the headers
        for i, row in enumerate(headers_data):
            if row[1] == 'Missing':
                headers_data[i][1] = f"{Colors.ERROR}Missing{Colors.RESET}"
            else:
                headers_data[i][1] = f"{Colors.STATUS_SUCCESS}Present{Colors.RESET}"

        print(format_subheader("Security Headers"))
        print(tabulate(headers_data, headers=['Header', 'Status'], tablefmt='grid'))

    # Display recommended settings
    recommendations = info.get('recommendations', [])
    if recommendations:
        rec_data = []
        for rec in recommendations:
            name = rec.get('name', 'Unknown')
            value = 'Enabled' if rec.get('value', False) else 'Disabled'
            recommended = 'Enabled' if rec.get('recommended', True) else 'Disabled'
            status = rec.get('status', 'Unknown')

            # Color the status
            status_str = status
            if status == 'Good':
                status_str = f"{Colors.STATUS_SUCCESS}Good{Colors.RESET}"
            elif status == 'Warning':
                status_str = f"{Colors.WARNING}Warning{Colors.RESET}"

            rec_data.append([name, value, recommended, status_str])

        print(format_subheader("Security Recommendations"))
        print(tabulate(rec_data, headers=['Setting', 'Current', 'Recommended', 'Status'], tablefmt='grid'))

    return True
