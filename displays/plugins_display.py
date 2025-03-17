#!/usr/bin/env python3
"""
Jenkins Plugins Display Module
This module displays information about Jenkins plugins.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader

def display_plugins_summary(info):
    """
    Display Jenkins plugins summary in a console table

    Args:
        info (dict): Plugins information summary

    Returns:
        bool: Success status
    """
    if not info or "error" in info:
        print(f"{Colors.ERROR}Error: {info.get('error', 'Unknown error retrieving plugins information')}{Colors.RESET}")
        return False

    # Format table data
    table_data = [
        ['Total Plugins', info.get('total_plugins', 0)],
        ['Active Plugins', info.get('active_plugins', 0)]
    ]

    # Add updates count with color based on number
    updates_available = info.get('updates_available', 0)
    if updates_available > 20:
        table_data.append(['Updates Available', f"{Colors.ERROR}{updates_available}{Colors.RESET}"])
    elif updates_available > 10:
        table_data.append(['Updates Available', f"{Colors.WARNING}{updates_available}{Colors.RESET}"])
    else:
        table_data.append(['Updates Available', updates_available])

    print(format_subheader("Jenkins Plugins Summary"))
    print(tabulate(table_data, headers=['Metric', 'Value'], tablefmt='grid'))

    # Show categories if available
    categories = info.get('categories', {})
    if categories:
        # Sort by count
        categories_table = sorted([[cat, count] for cat, count in categories.items()],
                                key=lambda x: x[1], reverse=True)

        # Show top 10 categories
        if len(categories_table) > 10:
            print(format_subheader("Top 10 Plugin Categories"))
            categories_table = categories_table[:10]
        else:
            print(format_subheader("Plugin Categories"))

        print(tabulate(categories_table, headers=['Category', 'Count'], tablefmt='grid'))

    # Show plugins with updates if available
    updates = info.get('update_list', [])
    if updates:
        updates_table = []
        for plugin in updates:
            updates_table.append([
                plugin.get('name', 'Unknown'),
                plugin.get('current_version', 'Unknown'),
                plugin.get('new_version', 'Unknown')
            ])

        # Show top 10 updates
        if len(updates_table) > 10:
            print(format_subheader(f"Plugin Updates Available (showing 10 of {len(updates)})"))
            updates_table = updates_table[:10]
        else:
            print(format_subheader("Plugin Updates Available"))

        print(tabulate(updates_table, headers=['Plugin', 'Current Version', 'New Version'], tablefmt='grid'))

    # Show recent plugins if available
    recent = info.get('recent_plugins', [])
    if recent:
        recent_table = []
        for plugin in recent:
            recent_table.append([
                plugin.get('name', 'Unknown'),
                plugin.get('version', 'Unknown')
            ])

        print(format_subheader("Recently Installed/Updated Plugins"))
        print(tabulate(recent_table, headers=['Plugin', 'Version'], tablefmt='grid'))

    return True
