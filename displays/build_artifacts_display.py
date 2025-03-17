#!/usr/bin/env python3
"""
Jenkins Build Artifacts Display Module
This module displays information about artifacts produced by Jenkins builds.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader, format_size

def display_build_artifacts(info):
    """
    Display build artifacts in a console table

    Args:
        info (dict): Build artifacts information

    Returns:
        bool: Success status
    """
    if "error" in info:
        print(f"{Colors.ERROR}Error: {info['error']}{Colors.RESET}")
        return False

    # Get artifacts data
    artifacts = info.get('artifacts', [])
    if not artifacts:
        print(f"\n{Colors.WARNING}No build artifacts information available{Colors.RESET}")
        return True

    # Prepare data for table
    table_data = []
    for artifact in artifacts:
        # Format size
        size = artifact.get('size', 0)
        size_str = format_size(size)

        table_data.append([
            artifact.get('job_name', 'Unknown'),
            artifact.get('artifact_name', 'Unknown'),
            size_str,
            artifact.get('build_number', 'Unknown'),
            artifact.get('age', 'Unknown'),
            artifact.get('download_count', 0)
        ])

    # Table is already sorted by size
    print(format_subheader("Build Artifacts Table"))
    print(tabulate(
        table_data,
        headers=['Job Name', 'Artifact Name', 'Size', 'Build #', 'Age', 'Downloads'],
        tablefmt='grid'
    ))

    return True
