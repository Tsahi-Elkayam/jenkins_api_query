#!/usr/bin/env python3
"""
Jenkins Executor Usage Display Module
This module displays Jenkins executor usage information.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader, format_percentage

def display_executor_usage(info):
    """
    Display executor usage in a console table

    Args:
        info (dict): Executor usage information

    Returns:
        bool: Success status
    """
    if "error" in info:
        print(f"{Colors.ERROR}Error: {info['error']}{Colors.RESET}")
        return False

    # Get executor usage data
    executor_usage = info.get('executor_usage', [])
    if not executor_usage:
        print(f"\n{Colors.WARNING}No executor usage information available{Colors.RESET}")
        return True

    # Print summary first
    total_executors = info.get('total_executors', 0)
    busy_executors = info.get('busy_executors', 0)
    idle_executors = info.get('idle_executors', 0)
    overall_utilization = info.get('overall_utilization', 0)

    summary_data = [
        ['Total Executors', total_executors],
        ['Busy Executors', busy_executors],
        ['Idle Executors', idle_executors],
        ['Overall Utilization', format_percentage(overall_utilization)]
    ]

    print(format_subheader("Executor Usage Summary"))
    print(tabulate(summary_data, headers=['Metric', 'Value'], tablefmt='grid'))

    # Prepare data for node executors table
    table_data = []
    for node in executor_usage:
        # Format utilization with color
        utilization = node.get('utilization', 0)
        util_str = format_percentage(utilization)

        table_data.append([
            node.get('node_name', 'Unknown'),
            f"{node.get('busy_executors', 0)}/{node.get('total_executors', 0)}",
            util_str,
            node.get('most_running_job', '-')
        ])

    # Keep original sorting (by utilization descending)
    print(format_subheader("Executor Usage By Node"))
    print(tabulate(
        table_data,
        headers=['Node Name', 'Busy/Total', 'Utilization', 'Most Running Job'],
        tablefmt='grid'
    ))

    # Show visual representation of executor usage
    print("\nExecutor Utilization:")
    bar_length = 50
    used_bars = int(bar_length * overall_utilization / 100)
    free_bars = bar_length - used_bars

    # Choose color based on utilization
    if overall_utilization >= 90:
        bar_color = Colors.DISK_HIGH
    elif overall_utilization >= 70:
        bar_color = Colors.DISK_MEDIUM
    else:
        bar_color = Colors.DISK_LOW

    print(f"{bar_color}{'█' * used_bars}{Colors.RESET}{'░' * free_bars} {overall_utilization:.1f}%")
    print(f"{Colors.DISK_HIGH}■ High (>90%){Colors.RESET}   {Colors.DISK_MEDIUM}■ Medium (70-90%){Colors.RESET}   {Colors.DISK_LOW}■ Low (<70%){Colors.RESET}")

    return True
