#!/usr/bin/env python3
"""
Jenkins Nodes Display Module
This module displays detailed Jenkins nodes information.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader

def display_nodes_overview(info):
    """
    Display nodes overview in console tables

    Args:
        info (dict): Nodes overview information

    Returns:
        bool: Success status
    """
    if "error" in info:
        print(f"{Colors.ERROR}Error: {info['error']}{Colors.RESET}")
        return False

    # Print summary table
    summary_data = [
        ['Total Nodes', info.get('total_nodes', 0)],
        ['Online Nodes', info.get('status_counts', {}).get('online', 0)],
        ['Offline Nodes', info.get('status_counts', {}).get('offline', 0)],
        ['Temporarily Offline Nodes', info.get('status_counts', {}).get('temp_offline', 0)],
        ['Total Executors', info.get('total_executors', 0)],
        ['Busy Executors', info.get('busy_executors', 0)],
        ['Idle Executors', info.get('idle_executors', 0)],
        ['Executor Utilization', f"{(info.get('busy_executors', 0) / info.get('total_executors', 1) * 100):.1f}%" if info.get('total_executors', 0) > 0 else '0%']
    ]

    print(format_subheader("Jenkins Nodes Summary"))
    print(tabulate(summary_data, headers=['Metric', 'Value'], tablefmt='grid'))

    # Print connection types distribution
    conn_types = info.get('connection_types', {})
    if conn_types:
        conn_types_data = [[conn_type, count] for conn_type, count in conn_types.items()]
        conn_types_data.sort(key=lambda x: x[1], reverse=True)

        print(format_subheader("Connection Types Distribution"))
        print(tabulate(conn_types_data, headers=['Connection Type', 'Count'], tablefmt='grid'))

    # Print nodes table
    nodes = info.get('nodes', [])
    if not nodes:
        print(f"\n{Colors.WARNING}No nodes found{Colors.RESET}")
        return True

    # Prepare data for tabulate
    table_data = []
    for node in nodes:
        # Format status with color
        status = node.get('status', 'Unknown')
        if status == 'Online':
            status_str = f"{Colors.STATUS_ONLINE}Online{Colors.RESET}"
        elif status == 'Offline':
            status_str = f"{Colors.STATUS_OFFLINE}Offline{Colors.RESET}"
        elif status == 'Temporarily Offline':
            status_str = f"{Colors.STATUS_TEMP_OFFLINE}Temporarily Offline{Colors.RESET}"
        else:
            status_str = status

        # Format utilization percentage
        if node.get('num_executors', 0) > 0:
            utilization = f"{(node.get('busy_executors', 0) / node.get('num_executors', 1) * 100):.1f}%"
        else:
            utilization = "N/A"

        table_data.append([
            node.get('name', 'Unknown'),
            status_str,
            f"{node.get('busy_executors', 0)}/{node.get('num_executors', 0)}",
            utilization,
            node.get('connection_type', 'Unknown'),
            node.get('disk_space', 'Unknown'),
            node.get('os_full_name', node.get('architecture', 'Unknown')),
            node.get('response_time', 'Unknown')
        ])

    # Sort by status (online first) and then by name
    try:
        table_data.sort(key=lambda x: (0 if 'Online' in x[1] else 1 if 'Temporarily Offline' in x[1] else 2, x[0]))
    except Exception:
        # If sorting fails, just continue without sorting
        pass

    # If more than 20 nodes, only show a subset
    if len(table_data) > 20:
        print(f"\n{Colors.INFO}Jenkins Nodes (showing first 20 of {len(nodes)} nodes):{Colors.RESET}")
        limited_data = table_data[:20]
    else:
        print(format_subheader("Jenkins Nodes"))
        limited_data = table_data

    print(tabulate(
        limited_data,
        headers=['Node Name', 'Status', 'Executors (Busy/Total)', 'Utilization', 'Type', 'Disk Space', 'OS', 'Response Time'],
        tablefmt='grid'
    ))

    return True

def display_node_labels_distribution(info):
    """
    Display node labels distribution in a console table

    Args:
        info (dict): Nodes information with labels

    Returns:
        bool: Success status
    """
    if "error" in info:
        print(f"{Colors.ERROR}Error: {info['error']}{Colors.RESET}")
        return False

    # Print labels table
    labels = []

    # Check different possible label structures based on the data source
    if 'labels' in info:
        labels = info.get('labels', [])
    elif 'all_labels' in info:
        all_labels = info.get('all_labels', [])
        nodes = info.get('nodes', [])

        # Generate label usage statistics from all_labels
        for label in all_labels:
            # Count nodes with this label
            nodes_with_label = sum(1 for node in nodes if 'labels' in node and label in node.get('labels', '').split())

            # Skip if no nodes have this label
            if nodes_with_label == 0:
                continue

            # Extract executors with this label
            online_nodes = sum(1 for node in nodes if 'labels' in node and label in node.get('labels', '').split() and node.get('status') == 'Online')

            # Count total executors
            total_executors = sum(node.get('num_executors', 0) for node in nodes if 'labels' in node and label in node.get('labels', '').split())

            labels.append({
                'name': label,
                'node_count': nodes_with_label,
                'online_nodes': online_nodes,
                'offline_nodes': nodes_with_label - online_nodes,
                'total_executors': total_executors
            })

    if not labels:
        print(f"\n{Colors.WARNING}No label information available{Colors.RESET}")
        return True

    # Prepare data for tabulate
    table_data = []
    for label in labels:
        # Calculate node availability percentage
        node_availability = (label.get('online_nodes', 0) / label.get('node_count', 1) * 100) if label.get('node_count', 0) > 0 else 0

        # Format availability with color
        if node_availability >= 90:
            avail_str = f"{Colors.STATUS_SUCCESS}{node_availability:.1f}%{Colors.RESET}"
        elif node_availability >= 70:
            avail_str = f"{Colors.STATUS_UNSTABLE}{node_availability:.1f}%{Colors.RESET}"
        else:
            avail_str = f"{Colors.STATUS_FAILED}{node_availability:.1f}%{Colors.RESET}"

        table_data.append([
            label.get('name', 'Unknown'),
            label.get('node_count', 0),
            label.get('online_nodes', 0),
            label.get('offline_nodes', 0),
            avail_str,
            label.get('total_executors', 0)
        ])

    # Sort by node count (descending)
    table_data.sort(key=lambda x: x[1], reverse=True)

    # Limit to top 20 labels if more
    if len(table_data) > 20:
        print(f"\n{Colors.INFO}Jenkins Node Labels Distribution (showing top 20 of {len(labels)} labels):{Colors.RESET}")
        table_data = table_data[:20]
    else:
        print(format_subheader("Jenkins Node Labels Distribution"))

    print(tabulate(
        table_data,
        headers=['Label', 'Nodes', 'Online', 'Offline', 'Availability', 'Total Executors'],
        tablefmt='grid'
    ))

    return True
