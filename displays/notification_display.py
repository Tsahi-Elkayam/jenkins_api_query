#!/usr/bin/env python3
"""
Jenkins Notification Systems Display Module
This module displays information about notification systems in Jenkins.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader

def display_notification_info(info):
    """
    Display information about notification systems in Jenkins

    Args:
        info (dict): Notification systems information

    Returns:
        bool: Success status
    """
    if "error" in info:
        print(f"{Colors.ERROR}Error: {info['error']}{Colors.RESET}")
        return False

    # Prepare summary table
    slack_enabled = info.get('slack', {}).get('enabled', False)
    teams_enabled = info.get('teams', {}).get('enabled', False)
    email_enabled = info.get('email', {}).get('enabled', False)
    other_count = len(info.get('other', []))

    summary_data = [
        ['Slack', 'Enabled' if slack_enabled else 'Disabled'],
        ['Microsoft Teams', 'Enabled' if teams_enabled else 'Disabled'],
        ['Email', 'Enabled' if email_enabled else 'Disabled']
    ]

    # Add color to status
    for i, row in enumerate(summary_data):
        if row[1] == 'Enabled':
            summary_data[i][1] = f"{Colors.STATUS_SUCCESS}Enabled{Colors.RESET}"
        else:
            summary_data[i][1] = f"{Colors.WARNING}Disabled{Colors.RESET}"

    # Add other notification systems
    if other_count > 0:
        other_systems = [system.get('name', 'Unknown') for system in info.get('other', [])]
        summary_data.append(['Other Systems', ', '.join(other_systems)])

    print(format_subheader("Jenkins Notification Systems"))
    print(tabulate(summary_data, headers=['System', 'Status'], tablefmt='grid'))

    # Display Slack configuration if enabled
    slack_info = info.get('slack', {})
    if slack_enabled:
        slack_table = []

        if 'workspace' in slack_info:
            slack_table.append(['Workspace', slack_info.get('workspace', '')])

        if 'default_channel' in slack_info:
            slack_table.append(['Default Channel', slack_info.get('default_channel', '')])

        if 'token_configured' in slack_info:
            token_status = "Configured" if slack_info.get('token_configured', False) else "Not configured"
            slack_table.append(['Integration Token', token_status])

        if 'version' in slack_info:
            slack_table.append(['Plugin Version', slack_info.get('version', 'Unknown')])

        if slack_table:
            print(format_subheader("Slack Configuration"))
            print(tabulate(slack_table, headers=['Setting', 'Value'], tablefmt='grid'))

    # Display Teams configuration if enabled
    teams_info = info.get('teams', {})
    if teams_enabled:
        teams_table = []

        if 'webhook' in teams_info:
            teams_table.append(['Webhook URL', teams_info.get('webhook', '')])

        if 'webhook_configured' in teams_info:
            webhook_status = "Configured" if teams_info.get('webhook_configured', False) else "Not configured"
            teams_table.append(['Webhook Status', webhook_status])

        if 'version' in teams_info:
            teams_table.append(['Plugin Version', teams_info.get('version', 'Unknown')])

        if teams_table:
            print(format_subheader("Microsoft Teams Configuration"))
            print(tabulate(teams_table, headers=['Setting', 'Value'], tablefmt='grid'))

    # Display notification usage in jobs
    usage_info = info.get('usage', {})
    if usage_info and usage_info.get('total_jobs_checked', 0) > 0:
        usage_table = []
        total_jobs = usage_info.get('total_jobs_checked', 0)

        if total_jobs > 0:
            # Calculate percentages
            slack_pct = (usage_info.get('slack', 0) / total_jobs * 100) if total_jobs > 0 else 0
            teams_pct = (usage_info.get('teams', 0) / total_jobs * 100) if total_jobs > 0 else 0
            email_pct = (usage_info.get('email', 0) / total_jobs * 100) if total_jobs > 0 else 0
            other_pct = (usage_info.get('other', 0) / total_jobs * 100) if total_jobs > 0 else 0

            usage_table = [
                ['Slack', usage_info.get('slack', 0), f"{slack_pct:.1f}%"],
                ['Microsoft Teams', usage_info.get('teams', 0), f"{teams_pct:.1f}%"],
                ['Email', usage_info.get('email', 0), f"{email_pct:.1f}%"],
                ['Other', usage_info.get('other', 0), f"{other_pct:.1f}%"]
            ]

            print(format_subheader(f"Notification Usage in Jobs (Sample of {total_jobs} jobs)"))
            print(tabulate(usage_table, headers=['System', 'Jobs', 'Percentage'], tablefmt='grid'))

    return True
