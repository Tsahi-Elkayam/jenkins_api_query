#!/usr/bin/env python3
"""
Jenkins Jobs Display Module
This module displays detailed Jenkins jobs information.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader, format_status, format_percentage

def display_jobs_overview(info):
    """
    Display jobs overview in console tables

    Args:
        info (dict): Jobs overview information

    Returns:
        bool: Success status
    """
    if "error" in info:
        print(f"{Colors.ERROR}Error: {info['error']}{Colors.RESET}")
        return False

    # Print summary table
    summary_data = [
        ['Total Jobs', info.get('total_jobs', 0)],
        ['Success Rate', format_percentage(info.get('success_rate', 0))]
    ]

    # Add status counts
    status_counts = info.get('status_counts', {})
    for status, count in status_counts.items():
        if count > 0:
            summary_data.append([status.title(), count])

    print(format_subheader("Jenkins Jobs Overview"))
    print(tabulate(summary_data, headers=['Metric', 'Value'], tablefmt='grid'))

    # Print jobs table
    jobs = info.get('jobs', [])
    if not jobs:
        print("No jobs found")
        return True

    # Prepare data for tabulate
    table_data = []
    for job in jobs:
        table_data.append([
            job.get('name', 'Unknown'),
            format_status(job.get('color', 'Unknown')),
            job.get('lastBuildNumber', 'N/A'),
            job.get('lastBuildTime', 'N/A'),
            job.get('lastBuildResult', 'N/A'),
            job.get('lastBuildDuration', 'N/A')
        ])

    # Sort by status and then by name
    try:
        table_data.sort(key=lambda x: (x[1], x[0]))
    except Exception:
        pass

    # Limit to 20 jobs for display to avoid flooding the console
    if len(table_data) > 20:
        table_data = table_data[:20]
        print(f"\n{Colors.INFO}Jobs (showing first 20 of {len(jobs)} jobs):{Colors.RESET}")
    else:
        print(format_subheader("Jenkins Jobs"))

    print(tabulate(
        table_data,
        headers=['Job Name', 'Status', 'Last Build', 'Build Time', 'Result', 'Duration'],
        tablefmt='grid'
    ))

    return True

def display_job_types(info):
    """
    Display job types distribution in a console table

    Args:
        info (dict): Job types information

    Returns:
        bool: Success status
    """
    if "error" in info:
        print(f"{Colors.ERROR}Error: {info['error']}{Colors.RESET}")
        return False

    # Print job types table
    job_types = info.get('job_types', [])
    if not job_types:
        print(f"\n{Colors.WARNING}No job type information available{Colors.RESET}")
        return True

    # Prepare data for tabulate
    table_data = []
    for job_type in job_types:
        table_data.append([
            job_type.get('type', 'Unknown'),
            job_type.get('count', 0),
            f"{job_type.get('percentage', 0):.1f}%"
        ])

    print(format_subheader("Jenkins Job Types Distribution"))
    print(tabulate(
        table_data,
        headers=['Job Type', 'Count', 'Percentage'],
        tablefmt='grid'
    ))

    return True

def display_recent_builds(info):
    """
    Display recent builds in a console table

    Args:
        info (dict): Recent builds information

    Returns:
        bool: Success status
    """
    if "error" in info:
        print(f"{Colors.ERROR}Error: {info['error']}{Colors.RESET}")
        return False

    # Print recent builds table
    builds = info.get('builds', [])
    if not builds:
        print(f"\n{Colors.WARNING}No recent builds found{Colors.RESET}")
        return True

    # Prepare data for tabulate
    table_data = []
    for build in builds:
        # Format result with color
        result = build.get('result', 'N/A')
        if result == 'SUCCESS':
            result_str = f"{Colors.STATUS_SUCCESS}Success{Colors.RESET}"
        elif result == 'FAILURE':
            result_str = f"{Colors.STATUS_FAILED}Failure{Colors.RESET}"
        elif result == 'UNSTABLE':
            result_str = f"{Colors.STATUS_UNSTABLE}Unstable{Colors.RESET}"
        elif result == 'ABORTED':
            result_str = f"{Colors.WARNING}Aborted{Colors.RESET}"
        else:
            result_str = result

        table_data.append([
            build.get('job_name', 'Unknown'),
            build.get('build_number', 'N/A'),
            result_str,
            build.get('timestamp', 'N/A'),
            build.get('duration', 'N/A')
        ])

    print(format_subheader("Recent Builds"))
    print(tabulate(
        table_data,
        headers=['Job Name', 'Build #', 'Result', 'When', 'Duration'],
        tablefmt='grid'
    ))

    return True
