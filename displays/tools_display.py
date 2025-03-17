#!/usr/bin/env python3
"""
Jenkins Tools Display Module
This module displays information about tools configured in Jenkins.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader

def display_tools_info(info):
    """
    Display information about configured tools in Jenkins

    Args:
        info (dict): Tools information

    Returns:
        bool: Success status
    """
    if "error" in info:
        print(f"{Colors.ERROR}Error: {info['error']}{Colors.RESET}")
        return False

    # Display summary
    total_tools = info.get('total_tools', 0)
    jdk_count = len(info.get('jdk', []))
    git_count = len(info.get('git', []))
    maven_count = len(info.get('maven', []))
    ant_count = len(info.get('ant', []))
    gradle_count = len(info.get('gradle', []))

    summary_data = [
        ['Total Tools', total_tools],
        ['JDK', jdk_count],
        ['Git', git_count],
        ['Maven', maven_count],
        ['Ant', ant_count],
        ['Gradle', gradle_count]
    ]

    # Add other tool types
    for tool_type in ['docker', 'nodejs', 'sonarqube']:
        count = len(info.get(tool_type, []))
        if count > 0:
            # Format tool type name
            type_name = tool_type.replace('sonarqube', 'SonarQube').replace('nodejs', 'NodeJS')
            summary_data.append([type_name, count])

    print(format_subheader("Jenkins Tools Summary"))
    print(tabulate(summary_data, headers=['Tool Type', 'Count'], tablefmt='grid'))

    # Display auto-install status
    auto_install = info.get('uses_auto_install', False)
    if auto_install:
        print(f"\n{Colors.INFO}Auto-installation: {Colors.STATUS_SUCCESS}Enabled{Colors.RESET}")

    # Display tools by type
    tool_types = {
        'JDK': info.get('jdk', []),
        'Git': info.get('git', []),
        'Maven': info.get('maven', []),
        'Ant': info.get('ant', []),
        'Gradle': info.get('gradle', []),
        'Docker': info.get('docker', []),
        'NodeJS': info.get('nodejs', []),
        'SonarQube': info.get('sonarqube', [])
    }

    for tool_type, tools in tool_types.items():
        if not tools:
            continue

        # Prepare tools table
        tools_table = []
        for tool in tools:
            row = [
                tool.get('name', 'Unknown'),
                tool.get('path', 'Auto-installed') if 'path' in tool else ('Auto-installed' if tool.get('auto_install', False) else 'Default')
            ]

            # Add version if available
            if 'version' in tool:
                row.append(tool.get('version', ''))

            tools_table.append(row)

        # Add headers
        headers = ['Name', 'Path']
        if any('version' in tool for tool in tools):
            headers.append('Version')

        print(format_subheader(f"{tool_type} Installations"))
        print(tabulate(tools_table, headers=headers, tablefmt='grid'))

    # Display tool usage in jobs
    tool_usage = info.get('tool_usage', {})
    if tool_usage:
        usage_table = []
        for tool_type, jobs in tool_usage.items():
            # Skip if no jobs using this tool
            if not jobs:
                continue

            # Format tool type
            type_name = tool_type.replace('sonarqube', 'SonarQube').replace('nodejs', 'NodeJS').title()

            usage_table.append([
                type_name,
                len(jobs),
                ', '.join(jobs) if len(jobs) <= 3 else ', '.join(jobs[:3]) + '...'
            ])

        if usage_table:
            print(format_subheader("Tool Usage in Jobs"))
            print(tabulate(usage_table, headers=['Tool', 'Jobs', 'Example Jobs'], tablefmt='grid'))

    return True
