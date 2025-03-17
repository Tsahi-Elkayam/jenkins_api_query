#!/usr/bin/env python3
"""
Jenkins OS Distribution Display Functions
This module contains functions to display OS distribution information.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_header, format_subheader

def display_os_distribution(os_info, detailed=False):
    """
    Display OS distribution information

    Args:
        os_info: Dictionary containing OS distribution information
        detailed: Whether to show detailed information
    """
    print(format_subheader("OS Distribution"))

    # Basic OS type distribution (Windows, Linux, etc.)
    os_type_counts = {}
    nodes = os_info.get('nodes', [])

    for node in nodes:
        os_name = node.get('os_name', 'Unknown')
        if os_name in os_type_counts:
            os_type_counts[os_name] += 1
        else:
            os_type_counts[os_name] = 1

    # Create a table for OS types
    os_type_table = []
    for os_type, count in sorted(os_type_counts.items(), key=lambda x: x[1], reverse=True):
        os_type_table.append([os_type, count])

    print(tabulate(os_type_table, headers=["OS Type", "Count"], tablefmt="grid"))

    # If detailed view is requested, show the detailed OS distribution
    if detailed and 'os_distribution' in os_info:
        display_detailed_os_distribution(os_info['os_distribution'])

def display_detailed_os_distribution(os_distribution):
    """
    Display detailed OS distribution with specific versions

    Args:
        os_distribution: Dictionary containing OS distribution by version
    """
    print(format_subheader("Detailed OS Distribution"))

    # Create a table for detailed OS distribution
    os_detailed_table = []
    for os_version, count in sorted(os_distribution.items(), key=lambda x: x[1], reverse=True):
        os_detailed_table.append([os_version, count])

    print(tabulate(os_detailed_table, headers=["OS Version", "Count"], tablefmt="grid"))

def display_linux_details(linux_info):
    """
    Display Linux distribution details

    Args:
        linux_info: Dictionary containing Linux distribution information
    """
    if not linux_info or not linux_info.get('distributions'):
        return

    print(format_subheader("Linux Distribution Details"))

    distributions = linux_info.get('distributions', {})
    dist_table = []

    for dist_name, dist_data in sorted(distributions.items(), key=lambda x: x[1]['count'], reverse=True):
        dist_table.append([
            dist_name,
            dist_data.get('count', 0),
            dist_data.get('major_versions', 'Unknown'),
            dist_data.get('latest_version', 'Unknown')
        ])

    print(tabulate(dist_table,
                  headers=["Distribution", "Count", "Major Versions", "Latest Version"],
                  tablefmt="grid"))

def display_os_details_table(os_info):
    """
    Display a detailed table of all nodes with OS information

    Args:
        os_info: Dictionary containing OS information
    """
    print(format_subheader("Nodes OS Details"))

    nodes = os_info.get('nodes', [])
    os_details_table = []

    for node in nodes:
        os_details_table.append([
            node.get('name', 'Unknown'),
            node.get('os_full_name', 'Unknown'),
            node.get('architecture', 'Unknown').replace(node.get('os_full_name', ''), '').strip(),
            node.get('jvm_version', 'Unknown')
        ])

    # Sort by OS name then by node name
    os_details_table.sort(key=lambda x: (x[1], x[0]))

    # Show first 20 nodes only to avoid overwhelming output
    if len(os_details_table) > 20:
        print(f"Showing first 20 of {len(os_details_table)} nodes:")
        os_details_table = os_details_table[:20]

    print(tabulate(os_details_table,
                  headers=["Node Name", "OS Version", "Architecture", "JVM Version"],
                  tablefmt="grid"))

def display_os_distribution_summary(os_summary):
    """
    Display a summary table of OS distribution with specific versions

    Args:
        os_summary: Dictionary containing OS distribution summary
    """
    print(format_header("JENKINS OS DISTRIBUTION SUMMARY"))

    os_distribution = os_summary.get('os_distribution', {})
    if not os_distribution:
        print(f"{Colors.WARNING}No OS distribution data available{Colors.RESET}")
        return

    # Create a table for OS distribution summary
    os_summary_table = []
    for os_version, count in sorted(os_distribution.items(), key=lambda x: x[1], reverse=True):
        os_summary_table.append([os_version, count])

    print(tabulate(os_summary_table, headers=["OS Version", "Count"], tablefmt="grid"))
