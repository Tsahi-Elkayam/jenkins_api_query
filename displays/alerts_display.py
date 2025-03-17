#!/usr/bin/env python3
"""
Jenkins Alerts Display Module
This module displays alerts and warnings for Jenkins.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_header, format_subheader

def display_alerts(alerts_info):
    """
    Display alerts and warnings in console tables with color

    Args:
        alerts_info (dict): Alerts information summary

    Returns:
        bool: Success status
    """
    if not alerts_info:
        return False

    critical_count = alerts_info.get('critical_count', 0)
    warning_count = alerts_info.get('warning_count', 0)
    total_count = alerts_info.get('total_count', 0)

    if critical_count == 0 and warning_count == 0:
        print(format_header("JENKINS SYSTEM HEALTH"))
        print(f"{Colors.STATUS_SUCCESS}✅ GOOD - No alerts or warnings detected{Colors.RESET}")
        return True

    # Display summary
    print(format_header("JENKINS SYSTEM HEALTH"))

    if critical_count > 0:
        print(f"{Colors.CRITICAL}❗ CRITICAL ISSUES DETECTED: {critical_count} critical alerts{Colors.RESET}")

    if warning_count > 0:
        print(f"{Colors.WARNING}⚠️ WARNINGS DETECTED: {warning_count} warnings{Colors.RESET}")

    print(f"Total: {total_count} issues found\n")

    # Display critical alerts
    if critical_count > 0:
        critical_data = []
        for alert in alerts_info.get('critical_alerts', []):
            icon = alert.get('icon', '🔴')
            critical_data.append([
                f"{icon} {alert.get('category', 'Unknown')}",
                alert.get('message', 'Unknown'),
                alert.get('details', ''),
                alert.get('impact', 'HIGH')
            ])

        print(f"{Colors.CRITICAL}CRITICAL ALERTS:{Colors.RESET}")

        # Apply color to the entire table
        table = tabulate(
            critical_data,
            headers=['Category', 'Alert', 'Details', 'Impact'],
            tablefmt='grid'
        )

        # Display with red background for critical alerts
        print(f"{Back.RED}{Fore.WHITE}{table}{Style.RESET_ALL}")

    # Display warnings
    if warning_count > 0:
        warning_data = []
        for warning in alerts_info.get('warnings', []):
            icon = warning.get('icon', '🔶')
            warning_data.append([
                f"{icon} {warning.get('category', 'Unknown')}",
                warning.get('message', 'Unknown'),
                warning.get('details', ''),
                warning.get('impact', 'MEDIUM')
            ])

        print(f"\n{Colors.WARNING}WARNINGS:{Colors.RESET}")

        # Apply color to the entire table
        table = tabulate(
            warning_data,
            headers=['Category', 'Warning', 'Details', 'Impact'],
            tablefmt='grid'
        )

        # Display with yellow background for warnings
        print(f"{Back.YELLOW}{Fore.BLACK}{table}{Style.RESET_ALL}")

    # Add recommendations section if there are issues
    if total_count > 0:
        print(format_subheader("Recommended Actions"))

        # Group by category for targeted recommendations
        categories = set()

        for alert in alerts_info.get('critical_alerts', []):
            categories.add(alert.get('category'))

        for warning in alerts_info.get('warnings', []):
            categories.add(warning.get('category'))

        for category in sorted(categories):
            if category == 'Disk Space':
                print(f"• {Colors.DISK_HIGH}Disk Space:{Colors.RESET} Run cleanup on Jenkins workspace and build artifacts")
            elif category == 'Node Status':
                print(f"• {Colors.STATUS_OFFLINE}Node Status:{Colors.RESET} Check node connectivity and agent logs")
            elif category == 'Job Status' or category == 'Build Success':
                print(f"• {Colors.STATUS_FAILED}Job Status:{Colors.RESET} Investigate failed builds and fix underlying issues")
            elif category == 'Build Queue':
                print(f"• {Colors.WARNING}Build Queue:{Colors.RESET} Consider adding more executors or optimizing build times")
            elif category == 'Plugin Updates' or category == 'Security Updates':
                print(f"• {Colors.ERROR}Plugin Updates:{Colors.RESET} Schedule a maintenance window to update plugins")
            elif category == 'Java Version':
                print(f"• {Colors.INFO}Java Version:{Colors.RESET} Plan an upgrade to a newer Java version")
            elif category == 'Executor Usage':
                print(f"• {Colors.WARNING}Executor Usage:{Colors.RESET} Add more executors or optimize build schedules")
            else:
                print(f"• {category}: Review and address issues")

    return True
