#!/usr/bin/env python3
"""
Jenkins Disk Usage Display Module
This module displays information about Jenkins disk usage.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader, format_size, format_percentage

def display_disk_summary(info):
    """
    Display Jenkins disk usage summary in a console table

    Args:
        info (dict): Disk usage information summary

    Returns:
        bool: Success status
    """
    if not info or "error" in info:
        print(f"{Colors.ERROR}Error: {info.get('error', 'Unknown error retrieving disk information')}{Colors.RESET}")
        return False

    # Format table data
    table_data = [
        ['Total Disk Space', f"{info.get('total_disk_gb', 0):.2f} GB"],
        ['Used Disk Space', f"{info.get('used_disk_gb', 0):.2f} GB"],
        ['Free Disk Space', f"{info.get('free_disk_gb', 0):.2f} GB"],
        ['Usage Percentage', format_percentage(info.get('usage_percent', 0), reverse=True)]
    ]

    # Add JENKINS_HOME size if available
    if info.get('jenkins_home_size') != "Unknown":
        # Format the size
        jenkins_home_formatted = format_size(info.get('jenkins_home_size', 0))
        table_data.append(['JENKINS_HOME Size', jenkins_home_formatted])

    # Add job and build disk usage if available
    if info.get('job_disk_usage') != "Unknown":
        # Format the size
        try:
            job_usage_formatted = format_size(info.get('job_disk_usage', 0))
            table_data.append(['Job Disk Usage', job_usage_formatted])
        except:
            table_data.append(['Job Disk Usage', info.get('job_disk_usage', 'Unknown')])

    if info.get('build_disk_usage') != "Unknown":
        try:
            build_usage_formatted = format_size(info.get('build_disk_usage', 0))
            table_data.append(['Build Disk Usage', build_usage_formatted])
        except:
            table_data.append(['Build Disk Usage', info.get('build_disk_usage', 'Unknown')])

    print(format_subheader("Jenkins Disk Usage Summary"))
    print(tabulate(table_data, headers=['Metric', 'Value'], tablefmt='grid'))

    # Show top jobs by size if available
    top_jobs = info.get('top_jobs_by_size', [])
    if top_jobs:
        jobs_table = []
        for job in top_jobs:
            jobs_table.append([
                job.get('name', 'Unknown'),
                format_size(job.get('size', 0))
            ])

        print(format_subheader("Top Jobs by Disk Usage"))
        print(tabulate(jobs_table, headers=['Job Name', 'Size'], tablefmt='grid'))

    # Add a visual disk usage bar
    used_percent = info.get('usage_percent', 0)
    bar_length = 50
    used_bars = int(bar_length * used_percent / 100)
    free_bars = bar_length - used_bars

    if used_percent >= 90:
        bar_color = Colors.DISK_CRITICAL
    elif used_percent >= 80:
        bar_color = Colors.DISK_HIGH
    elif used_percent >= 70:
        bar_color = Colors.DISK_MEDIUM
    else:
        bar_color = Colors.DISK_LOW

    disk_bar = f"{bar_color}{'█' * used_bars}{Colors.RESET}{'░' * free_bars} {used_percent:.1f}%"

    print("\nDisk Usage:")
    print(disk_bar)

    return True
