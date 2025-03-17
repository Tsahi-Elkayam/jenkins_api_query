#!/usr/bin/env python3
"""
Jenkins Failed Jobs Display Module
This module displays information about failing Jenkins jobs.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader, format_percentage

def display_failed_jobs(info):
    """
    Display failing jobs in a console table

    Args:
        info (dict): Failed jobs information

    Returns:
        bool: Success status
    """
    if "error" in info:
        print(f"{Colors.ERROR}Error: {info['error']}{Colors.RESET}")
        return False

    # Get failed jobs data
    failed_jobs = info.get('failed_jobs', [])
    if not failed_jobs:
        print(f"\n{Colors.STATUS_SUCCESS}No failing jobs found! 🎉{Colors.RESET}")
        return True

    # Prepare data for table
    table_data = []
    for job in failed_jobs:
        # Format success rate with color
        success_rate = job.get('success_rate', 0)
        success_rate_str = format_percentage(success_rate)

        table_data.append([
            job.get('job_name', 'Unknown'),
            job.get('last_failed', 'Unknown'),
            job.get('fail_count', 0),
            success_rate_str,
            job.get('last_success', 'Unknown'),
            job.get('common_failure_reason', 'Unknown')[:60] + ('...' if len(job.get('common_failure_reason', '')) > 60 else '')
        ])

    # Table is already sorted by last failed time
    print(format_subheader(f"Failed Jobs ({len(failed_jobs)} jobs)"))
    print(tabulate(
        table_data,
        headers=['Job Name', 'Last Failed', 'Fail Count', 'Success Rate', 'Last Success', 'Common Failure Reason'],
        tablefmt='grid'
    ))

    return True
