#!/usr/bin/env python3
"""
Jenkins Labels Display Module
This module displays Jenkins node labels information.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader, format_percentage

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
    labels = info.get('labels', [])
    if not labels:
        print(f"\n{Colors.WARNING}No label information available{Colors.RESET}")
        return True

    # Prepare data for tabulate
    table_data = []
    for label in labels:
        # Calculate node and executor utilization
        node_utilization = (label.get('online_nodes') / label.get('node_count') * 100) if label.get('node_count', 0) > 0 else 0
        executor_utilization = label.get('utilization', 0)

        # Format utilization with colors
        node_util_str = format_percentage(node_utilization)
        exec_util_str = format_percentage(executor_utilization)

        table_data.append([
            label.get('name', 'Unknown'),
            label.get('node_count', 0),
            label.get('online_nodes', 0),
            label.get('offline_nodes', 0),
            node_util_str,
            label.get('total_executors', 0),
            label.get('online_executors', 0),
            exec_util_str
        ])

    # Sort by node count (descending)
    table_data.sort(key=lambda x: x[1], reverse=True)

    # Limit to top 20 labels if more
    if len(table_data) > 20:
        print(format_subheader(f"Jenkins Node Labels Distribution (showing top 20 of {len(labels)} labels)"))
        table_data = table_data[:20]
    else:
        print(format_subheader("Jenkins Node Labels Distribution"))

    print(tabulate(
        table_data,
        headers=['Label', 'Nodes', 'Online', 'Offline', 'Node Avail', 'Executors', 'Online Exec', 'Exec Util'],
        tablefmt='grid'
    ))

    return True

def display_node_labels_table(info):
    """
    Display a table showing node names and their associated labels

    Args:
        info (dict): Nodes information including labeled_nodes

    Returns:
        bool: Success status
    """
    if "error" in info:
        print(f"{Colors.ERROR}Error: {info['error']}{Colors.RESET}")
        return False

    # Get the node to labels mapping
    labeled_nodes = info.get('labeled_nodes', {})
    if not labeled_nodes:
        print(f"\n{Colors.WARNING}No node label information available{Colors.RESET}")
        return True

    # Prepare data for tabulate
    table_data = []
    for node_name, labels in labeled_nodes.items():
        # Add row to table data
        table_data.append([
            node_name,
            ', '.join(labels) if labels else "No labels"
        ])

    # Sort by node name
    table_data.sort(key=lambda x: x[0])

    # Print the table
    print(format_subheader("Node Labels"))
    print(tabulate(
        table_data,
        headers=['Node Name', 'Labels'],
        tablefmt='grid',
        maxcolwidths=[None, 80]  # Limit the width of the labels column
    ))

    # Show unlabeled nodes if any
    unlabeled_nodes = info.get('unlabeled_nodes', [])
    if unlabeled_nodes:
        print(f"\n{Colors.WARNING}Unlabeled Nodes ({len(unlabeled_nodes)}):{Colors.RESET}")
        print(", ".join(unlabeled_nodes))

    return True

def display_label_usage(info):
    """
    Display label usage information

    Args:
        info (dict): Label usage information

    Returns:
        bool: Success status
    """
    if "error" in info:
        print(f"{Colors.ERROR}Error: {info['error']}{Colors.RESET}")
        return False

    # Get labels with job usage info
    labels = info.get('labels', [])
    if not labels:
        print(f"\n{Colors.WARNING}No label usage information available{Colors.RESET}")
        return True

    # Filter labels that are used in jobs
    used_labels = [label for label in labels if label.get('jobs_count', 0) > 0]

    if not used_labels:
        print(f"\n{Colors.WARNING}No labels are explicitly used in job configurations{Colors.RESET}")
        return True

    # Prepare data for tabulate
    table_data = []
    for label in used_labels:
        table_data.append([
            label.get('name', 'Unknown'),
            label.get('node_count', 0),
            label.get('jobs_count', 0),
            ', '.join(label.get('jobs', [])[:3]) + ('...' if len(label.get('jobs', [])) > 3 else '')
        ])

    # Sort by job count (descending)
    table_data.sort(key=lambda x: x[2], reverse=True)

    print(format_subheader("Label Usage in Jobs"))
    print(tabulate(
        table_data,
        headers=['Label', 'Nodes', 'Jobs', 'Example Jobs'],
        tablefmt='grid'
    ))

    return True
