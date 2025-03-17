#!/usr/bin/env python3
"""
Jenkins Build Statistics Display Module
This module displays build durations and frequencies.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader, format_duration

def display_build_durations(info):
    """
    Display jobs with longest build durations

    Args:
        info (dict): Build duration information

    Returns:
        bool: Success status
    """
    if "error" in info:
        print(f"{Colors.ERROR}Error: {info['error']}{Colors.RESET}")
        return False

    # Get build duration data
    job_durations = info.get('job_durations', [])
    if not job_durations:
        print(f"\n{Colors.WARNING}No build duration information available{Colors.RESET}")
        return True

    # Prepare data for table
    table_data = []
    for job in job_durations:
        # Format durations
        avg_duration = format_duration(job.get('avg_duration', 0))
        min_duration = format_duration(job.get('min_duration', 0))
        max_duration = format_duration(job.get('max_duration', 0))
        last_duration = format_duration(job.get('last_duration', 0))

        # Format trend with color and arrow
        trend = job.get('trend', 0)
        trend_direction = job.get('trend_direction', 'stable')

        if trend_direction == 'up':
            trend_str = f"{Colors.DISK_HIGH}↑ {trend:.1f}%{Colors.RESET}"
        elif trend_direction == 'down':
            trend_str = f"{Colors.DISK_LOW}↓ {trend:.1f}%{Colors.RESET}"
        else:
            trend_str = f"{Colors.RESET}→ {trend:.1f}%{Colors.RESET}"

        table_data.append([
            job.get('job_name', 'Unknown'),
            avg_duration,
            min_duration,
            max_duration,
            last_duration,
            trend_str
        ])

    # Table is already sorted by average duration
    print(format_subheader("Build Duration Table (Jobs with Longest Builds)"))
    print(tabulate(
        table_data,
        headers=['Job Name', 'Average', 'Shortest', 'Longest', 'Last Build', 'Trend'],
        tablefmt='grid'
    ))

    return True

def display_build_frequencies(info):
    """
    Display most frequently built jobs

    Args:
        info (dict): Build frequency information

    Returns:
        bool: Success status
    """
    if "error" in info:
        print(f"{Colors.ERROR}Error: {info['error']}{Colors.RESET}")
        return False

    # Get build frequency data
    job_frequencies = info.get('job_frequencies', [])
    if not job_frequencies:
        print(f"\n{Colors.WARNING}No build frequency information available{Colors.RESET}")
        return True

    # Prepare data for table
    table_data = []
    for job in job_frequencies:
        # Format average builds per day
        avg_per_day = job.get('avg_builds_per_day', 0)
        if avg_per_day >= 10:
            avg_str = f"{Colors.DISK_HIGH}{avg_per_day:.1f}{Colors.RESET}"
        elif avg_per_day >= 5:
            avg_str = f"{Colors.DISK_MEDIUM}{avg_per_day:.1f}{Colors.RESET}"
        else:
            avg_str = f"{avg_per_day:.1f}"

        table_data.append([
            job.get('job_name', 'Unknown'),
            job.get('total_builds', 0),
            job.get('builds_today', 0),
            job.get('builds_this_week', 0),
            job.get('builds_this_month', 0),
            avg_str
        ])

    # Table is already sorted by builds today
    print(format_subheader("Build Frequency Table (Most Frequently Built Jobs)"))
    print(tabulate(
        table_data,
        headers=['Job Name', 'Total Builds', 'Today', 'This Week', 'This Month', 'Avg Per Day'],
        tablefmt='grid'
    ))

    return True
