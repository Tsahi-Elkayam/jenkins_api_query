#!/usr/bin/env python3
"""
Jenkins Hardware Information Display Module
This module displays hardware information about Jenkins nodes.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader, format_percentage

def display_hardware_summary(info):
    """
    Display hardware summary in a console table

    Args:
        info (dict): Hardware information

    Returns:
        bool: Success status
    """
    if not info or "error" in info:
        print(f"{Colors.ERROR}Error: {info.get('error', 'Unknown error retrieving hardware information')}{Colors.RESET}")
        return False

    # Get summary data
    summary = info.get('summary', {})

    # Format summary table
    summary_data = [
        ['Total Nodes', summary.get('total_nodes', 0)],
        ['Online Nodes', summary.get('online_nodes', 0)],
        ['Offline Nodes', summary.get('offline_nodes', 0)],
        ['Total CPU Cores', summary.get('total_cpu_cores', 0)],
        ['Total Memory', summary.get('total_memory_formatted', 'Unknown')],
        ['Total Disk Space', summary.get('total_disk_space_formatted', 'Unknown')]
    ]

    print(format_subheader("Jenkins Hardware Summary"))
    print(tabulate(summary_data, headers=['Metric', 'Value'], tablefmt='grid'))

    # Format node hardware table
    nodes = info.get('nodes', [])
    if not nodes:
        print(f"\n{Colors.WARNING}No node hardware information available{Colors.RESET}")
        return True

    # Prepare data for tabulate
    node_data = []
    for node in nodes:
        # Format status with color
        status = node.get('status', 'Unknown')
        if status == 'Online':
            status_str = f"{Colors.STATUS_ONLINE}Online{Colors.RESET}"
        else:
            status_str = f"{Colors.STATUS_OFFLINE}Offline{Colors.RESET}"

        # Format memory usage with color
        memory_usage = node.get('memory_usage_percent', 'Unknown')
        if memory_usage != 'Unknown':
            memory_usage_str = format_percentage(memory_usage, reverse=True)
        else:
            memory_usage_str = 'Unknown'

        # Format disk usage with color
        disk_usage = node.get('disk_usage_percent', 'Unknown')
        if disk_usage != 'Unknown':
            disk_usage_str = format_percentage(disk_usage, reverse=True)
        else:
            disk_usage_str = 'Unknown'

        node_data.append([
            node.get('name', 'Unknown'),
            status_str,
            node.get('cpu_cores', 'Unknown'),
            node.get('cpu_load', 'Unknown'),
            node.get('memory_total', 'Unknown'),
            memory_usage_str,
            node.get('disk_space', 'Unknown'),
            disk_usage_str,
            node.get('response_time', 'Unknown'),
        ])

    # Sort by status first (online nodes first) then by name
    node_data.sort(key=lambda x: (0 if 'Online' in x[1] else 1, x[0]))

    print(format_subheader("Node Hardware Details"))
    print(tabulate(
        node_data,
        headers=['Node Name', 'Status', 'CPU Cores', 'CPU Load', 'Memory', 'Mem Usage', 'Disk Space', 'Disk Usage', 'Response Time'],
        tablefmt='grid'
    ))

    return True
