#!/usr/bin/env python3
"""
Jenkins Information Display Module
This module displays detailed Jenkins system information.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader

def display_jenkins_info(info):
    """
    Display Jenkins system information in a console table

    Args:
        info (dict): Jenkins system information

    Returns:
        bool: Success status
    """
    if 'error' in info:
        print(f"{Colors.ERROR}Error: {info['error']}{Colors.RESET}")
        return False

    # Create table data
    table_data = [
        ['Jenkins Version', info.get('version', 'Unknown')],
        ['Node Name', info.get('nodeName', 'Unknown')],
        ['Node Description', info.get('nodeDescription', 'Unknown')],
        ['Jenkins URL', info.get('jenkinsUrl', 'Unknown')],
        ['Jenkins Home', info.get('jenkinsHome', 'Unknown')],
        ['Jenkins WAR File', info.get('jenkinsWarFile', 'Unknown')],
        ['System Config File', info.get('systemConfigFile', 'Unknown')],
        ['Temp Directory', info.get('tempDir', 'Unknown')],
        ['Log Level', info.get('logLevel', 'Unknown')],
        ['Update Center URL', info.get('updateCenterSite', 'Unknown')],
        ['Agent Protocols', info.get('agentProtocols', 'Unknown')],
        ['Context Path', info.get('contextPath', 'Unknown')],
        ['Uptime', info.get('uptime', 'Unknown')],
        ['Startup Time', info.get('startupTime', 'Unknown')],
        ['Java Runtime', info.get('javaRuntimeName', 'Unknown')],
        ['Java Version', info.get('javaVersion', 'Unknown')],
        ['Java Virtual Machine', info.get('javaVmName', 'Unknown')],
        ['Java Home', info.get('javaHome', 'Unknown')],
        ['Java Vendor', info.get('javaVendor', 'Unknown')],
        ['OS Name', info.get('osName', 'Unknown')],
        ['OS Version', info.get('osVersion', 'Unknown')],
        ['OS Architecture', info.get('osArch', 'Unknown')],
        ['Timezone', info.get('timezone', 'Unknown')],
        ['Servlet Container', info.get('servletContainer', 'Unknown')],
        ['Servlet Version', info.get('servletContainerVersion', 'Unknown')],
        ['Session Timeout', info.get('sessionTimeout', 'Unknown')],
        ['Security Enabled', 'Yes' if info.get('useSecurity', False) else 'No'],
        ['Security Realm', info.get('securityRealm', 'Unknown')],
        ['Authorization Strategy', info.get('authorizationStrategy', 'Unknown')],
        ['CSRF Protection', info.get('crumbIssuer', 'Unknown')],
        ['Running Mode', info.get('runningMode', 'Unknown')],
        ['Slave Agent Port', info.get('slaveAgentPort', 'Unknown')],
        ['Primary View', info.get('primaryView', 'Unknown')],
        ['Total Views', info.get('views', 'Unknown')]
    ]

    # Filter out unknown/empty values
    filtered_data = [row for row in table_data if row[1] and row[1] != 'Unknown']

    # Add color to security-related fields
    for i, row in enumerate(filtered_data):
        if row[0] == 'Security Enabled' and row[1] == 'No':
            filtered_data[i][1] = f"{Colors.ERROR}No{Colors.RESET}"
        elif row[0] == 'Security Enabled' and row[1] == 'Yes':
            filtered_data[i][1] = f"{Colors.STATUS_SUCCESS}Yes{Colors.RESET}"
        elif row[0] == 'CSRF Protection' and row[1] == 'Disabled':
            filtered_data[i][1] = f"{Colors.ERROR}Disabled{Colors.RESET}"
        elif row[0] == 'CSRF Protection' and row[1] == 'Enabled':
            filtered_data[i][1] = f"{Colors.STATUS_SUCCESS}Enabled{Colors.RESET}"

    # Print as a table
    print(format_subheader("Jenkins System Information"))
    print(tabulate(filtered_data, headers=['Property', 'Value'], tablefmt='grid'))
    return True
