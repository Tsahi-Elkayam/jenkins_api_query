#!/usr/bin/env python3
"""
Jenkins Queue Display Module
This module displays Jenkins build queue information.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader

def display_queue_summary(info):
    """
    Display Jenkins queue summary in a console table

    Args:
        info (dict): Queue information summary

    Returns:
        bool: Success status
    """
    if not info or "error" in info:
        print(f"{Colors.ERROR}Error: {info.get('error', 'Unknown error retrieving queue information')}{Colors.RESET}")
        return False

    # Format table data
    items_in_queue = info.get('items_in_queue', 0)

    # Choose color based on queue size
    if items_in_queue >= 20:
        queue_color = Colors.ERROR
    elif items_in_queue >= 10:
        queue_color = Colors.WARNING
    else:
        queue_color = Colors.RESET

    table_data = [
        ['Items in Queue', f"{queue_color}{items_in_queue}{Colors.RESET}"],
        ['Average Wait Time', info.get('avg_wait_time', 'Unknown')]
    ]

    print(format_subheader("Jenkins Queue Summary"))
    print(tabulate(table_data, headers=['Metric', 'Value'], tablefmt='grid'))

    # Show blocking reasons if available
    blocking_reasons = info.get('blocking_reasons', {})
    if blocking_reasons:
        reasons_table = [[reason, count] for reason, count in blocking_reasons.items()]

        print(format_subheader("Blocking Reasons"))
        print(tabulate(reasons_table, headers=['Reason', 'Count'], tablefmt='grid'))

    # Show detailed queue items if available
    queue_items = info.get('queue_items', [])
    if queue_items:
        items_table = []
        for item in queue_items:
            # Format wait time with color based on duration
            wait_time = item.get('wait_time', 'Unknown')
            if 'hour' in wait_time.lower():
                wait_time_str = f"{Colors.ERROR}{wait_time}{Colors.RESET}"
            elif 'minute' in wait_time.lower() and any(d.isdigit() and int(d) > 10 for d in wait_time):
                wait_time_str = f"{Colors.WARNING}{wait_time}{Colors.RESET}"
            else:
                wait_time_str = wait_time

            items_table.append([
                item.get('job_name', 'Unknown'),
                wait_time_str,
                item.get('why_blocked', 'Unknown'),
                item.get('cause', 'Unknown')
            ])

        print(format_subheader("Queued Items"))
        print(tabulate(
            items_table,
            headers=['Job Name', 'Wait Time', 'Blocking Reason', 'Trigger Cause'],
            tablefmt='grid'
        ))

    return True
