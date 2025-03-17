#!/usr/bin/env python3
"""
Jenkins Nodes Summary Display Module
This module displays summarized Jenkins nodes information.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader, format_percentage

def display_nodes_summary(info):
    """
    Display Jenkins nodes summary in a console table

    Args:
        info (dict): Nodes information summary

    Returns:
        bool: Success status
    """
    if not info or "error" in info:
        print(f"{Colors.ERROR}Error: {info.get('error', 'Unknown error retrieving nodes information')}{Colors.RESET}")
        return False

    # Format table data
    node_status = info.get('node_status', {})

    table_data = [
        ['Total Nodes', info.get('total_nodes', 0)],
        ['Online', f"{Colors.STATUS_ONLINE}{node_status.get('online', 0)}{Colors.RESET}"],
        ['Offline', f"{Colors.STATUS_OFFLINE}{node_status.get('offline', 0)}{Colors.RESET}"],
        ['Temporarily Offline', f"{Colors.STATUS_TEMP_OFFLINE}{node_status.get('temp_offline', 0)}{Colors.RESET}"],
        ['Total Executors', info.get('total_executors', 0)],
        ['Busy Executors', info.get('busy_executors', 0)],
        ['Idle Executors', info.get('idle_executors', 0)],
        ['Executor Utilization', format_percentage(info.get('executor_utilization', 0))],
        ['Total Labels', info.get('total_labels', 0)]
    ]

    print(format_subheader("Jenkins Nodes Summary"))
    print(tabulate(table_data, headers=['Metric', 'Value'], tablefmt='grid'))

    # Show OS distribution if available
    os_distribution = info.get('os_distribution', {})
    if os_distribution:
        os_table = [[os_type, count] for os_type, count in os_distribution.items()]
        os_table.sort(key=lambda x: x[1], reverse=True)

        # Add color to OS types
        for i, row in enumerate(os_table):
            if row[0] == 'Windows':
                os_table[i][0] = f"{Colors.INFO}Windows{Colors.RESET}"
            elif row[0] == 'Linux':
                os_table[i][0] = f"{Colors.STATUS_SUCCESS}Linux{Colors.RESET}"
            elif row[0] == 'Mac':
                os_table[i][0] = f"{Colors.STATUS_UNSTABLE}Mac{Colors.RESET}"

        print(format_subheader("OS Distribution"))
        print(tabulate(os_table, headers=['OS Type', 'Count'], tablefmt='grid'))

    # Show connection types if available
    connection_types = info.get('connection_types', {})
    if connection_types:
        conn_table = [[conn_type, count] for conn_type, count in connection_types.items()]
        conn_table.sort(key=lambda x: x[1], reverse=True)

        print(format_subheader("Connection Types"))
        print(tabulate(conn_table, headers=['Connection Type', 'Count'], tablefmt='grid'))

    # Add visual representation of node status
    total_nodes = info.get('total_nodes', 0)
    if total_nodes > 0:
        online = node_status.get('online', 0)
        offline = node_status.get('offline', 0)
        temp_offline = node_status.get('temp_offline', 0)

        bar_length = 50

        online_bars = int(bar_length * online / total_nodes)
        temp_offline_bars = int(bar_length * temp_offline / total_nodes)
        offline_bars = bar_length - online_bars - temp_offline_bars

        status_bar = (f"{Colors.STATUS_ONLINE}{'█' * online_bars}"
                      f"{Colors.STATUS_TEMP_OFFLINE}{'█' * temp_offline_bars}"
                      f"{Colors.STATUS_OFFLINE}{'█' * offline_bars}{Colors.RESET}")

        print("\nNode Status Distribution:")
        print(status_bar)
        print(f"{Colors.STATUS_ONLINE}■ Online ({online}) "
              f"{Colors.STATUS_TEMP_OFFLINE}■ Temp Offline ({temp_offline}) "
              f"{Colors.STATUS_OFFLINE}■ Offline ({offline}){Colors.RESET}")

    return True
