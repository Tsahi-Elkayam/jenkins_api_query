#!/usr/bin/env python3
"""
Jenkins System Information Display Module
This module displays basic Jenkins system information.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader

def display_system_summary(info):
    """
    Display Jenkins system summary in a console table

    Args:
        info (dict): System information summary

    Returns:
        bool: Success status
    """
    if not info or "error" in info:
        print(f"{Colors.ERROR}Error: {info.get('error', 'Unknown error retrieving system information')}{Colors.RESET}")
        return False

    # Format table data
    table_data = [
        ['Jenkins Version', info.get('version', 'Unknown')],
        ['System Status', 'Active' if info.get('mode') != 'QUIET' else 'Quiet'],
        ['Security Enabled', f"{Colors.STATUS_SUCCESS}Yes{Colors.RESET}" if info.get('useSecurity') else f"{Colors.ERROR}No{Colors.RESET}"],
        ['Uptime', info.get('uptime', 'Unknown')],
        ['Java Version', info.get('javaVersion', 'Unknown')],
        ['Operating System', f"{info.get('osName', 'Unknown')} {info.get('osVersion', '')}"],
        ['OS Architecture', info.get('osArch', 'Unknown')],
        ['Jenkins Home', info.get('jenkinsHome', 'Unknown')],
        ['Timezone', info.get('timezone', 'Unknown')],
        ['Primary View', info.get('primaryView', 'Unknown')],
        ['Total Views', info.get('views', 'Unknown')]
    ]

    # Filter out empty or Unknown values
    filtered_data = [row for row in table_data if row[1] and row[1] != 'Unknown']

    print(format_subheader("Jenkins System Summary"))
    print(tabulate(filtered_data, headers=['Property', 'Value'], tablefmt='grid'))
    return True
