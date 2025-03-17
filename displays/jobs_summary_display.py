#!/usr/bin/env python3
"""
Jenkins Jobs Summary Display Module
This module displays summarized Jenkins jobs information.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader, format_percentage

def display_jobs_summary(info):
    """
    Display Jenkins jobs summary in a console table

    Args:
        info (dict): Jobs information summary

    Returns:
        bool: Success status
    """
    if not info or "error" in info:
        print(f"{Colors.ERROR}Error: {info.get('error', 'Unknown error retrieving jobs information')}{Colors.RESET}")
        return False

    # Format table data
    status = info.get('status', {})

    table_data = [
        ['Total Jobs', info.get('total', 0)],
        ['Successful', f"{Colors.STATUS_SUCCESS}{status.get('successful', 0)}{Colors.RESET}"],
        ['Failed', f"{Colors.STATUS_FAILED}{status.get('failed', 0)}{Colors.RESET}"],
        ['Unstable', f"{Colors.STATUS_UNSTABLE}{status.get('unstable', 0)}{Colors.RESET}"],
        ['Disabled', f"{Colors.STATUS_DISABLED}{status.get('disabled', 0)}{Colors.RESET}"],
        ['Building', f"{Colors.STATUS_BUILDING}{status.get('building', 0)}{Colors.RESET}"],
        ['Not Built', status.get('not_built', 0)],
        ['Success Rate', format_percentage(info.get('success_rate', 0))],
        ['Builds in Last 24h', info.get('builds_last_24h', 0)]
    ]

    print(format_subheader("Jenkins Jobs Summary"))
    print(tabulate(table_data, headers=['Metric', 'Value'], tablefmt='grid'))

    # Show recent build results if available
    build_results = info.get('recent_build_results', {})
    if build_results:
        build_table = [
            ['Successful', f"{Colors.STATUS_SUCCESS}{build_results.get('SUCCESS', 0)}{Colors.RESET}"],
            ['Failed', f"{Colors.STATUS_FAILED}{build_results.get('FAILURE', 0)}{Colors.RESET}"],
            ['Unstable', f"{Colors.STATUS_UNSTABLE}{build_results.get('UNSTABLE', 0)}{Colors.RESET}"],
            ['Aborted', f"{Colors.STATUS_DISABLED}{build_results.get('ABORTED', 0)}{Colors.RESET}"]
        ]

        print(format_subheader("Recent Build Results"))
        print(tabulate(build_table, headers=['Result', 'Count'], tablefmt='grid'))

    # Show job types if available
    job_types = info.get('job_types', {})
    if job_types:
        # Convert to list and sort by count
        types_table = [[job_type, count] for job_type, count in job_types.items()]
        types_table.sort(key=lambda x: x[1], reverse=True)

        print(format_subheader("Job Types Distribution"))
        print(tabulate(types_table, headers=['Job Type', 'Count'], tablefmt='grid'))

    # Add visual representation of job status distribution
    total = info.get('total', 0)
    if total > 0:
        success_count = status.get('successful', 0)
        failed_count = status.get('failed', 0)
        unstable_count = status.get('unstable', 0)
        other_count = total - success_count - failed_count - unstable_count

        bar_length = 50

        success_bars = int(bar_length * success_count / total)
        failed_bars = int(bar_length * failed_count / total)
        unstable_bars = int(bar_length * unstable_count / total)
        other_bars = bar_length - success_bars - failed_bars - unstable_bars

        status_bar = (f"{Colors.STATUS_SUCCESS}{'█' * success_bars}"
                     f"{Colors.STATUS_FAILED}{'█' * failed_bars}"
                     f"{Colors.STATUS_UNSTABLE}{'█' * unstable_bars}"
                     f"{Colors.RESET}{'█' * other_bars}")

        print("\nJob Status Distribution:")
        print(status_bar)
        print(f"{Colors.STATUS_SUCCESS}■ Success ({success_count}) "
              f"{Colors.STATUS_FAILED}■ Failed ({failed_count}) "
              f"{Colors.STATUS_UNSTABLE}■ Unstable ({unstable_count}) "
              f"{Colors.RESET}■ Other ({other_count})")

    return True
