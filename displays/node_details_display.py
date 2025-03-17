#!/usr/bin/env python3
"""
Jenkins Node Details Display
This module handles displaying detailed node information in table format.
"""

from utils.formatting import Colors, format_header, format_subheader
from texttable import Texttable

def display_os_details(os_details):
    """
    Display OS details for nodes in a tabular format

    Args:
        os_details: OS details information
    """
    if "error" in os_details:
        print(f"{Colors.ERROR}Error: {os_details['error']}{Colors.RESET}")
        return

    print(format_subheader("Jenkins Nodes OS Information"))

    # Create table
    table = Texttable()
    table.set_deco(Texttable.HEADER | Texttable.VLINES | Texttable.HLINES)
    table.set_cols_align(["l", "l", "l", "l", "l", "l"])
    table.set_cols_width([20, 20, 15, 10, 15, 10])
    
    # Add header
    table.add_row(["Node Name", "Machine Name", "IP Address", "OS Type", "OS Vendor", "OS Version"])
    
    # Add data
    nodes = os_details.get('os_details', [])
    for node in nodes:
        table.add_row([
            node.get('name', 'Unknown'),
            node.get('machine_name', 'Unknown'),
            node.get('ip_address', 'Unknown'),
            node.get('os_type', 'Unknown'),
            node.get('os_vendor', 'Unknown'),
            node.get('os_version', 'Unknown')
        ])
    
    print(table.draw())
    print()

def display_hardware_details(hw_details):
    """
    Display hardware details for nodes in a tabular format

    Args:
        hw_details: Hardware details information
    """
    if "error" in hw_details:
        print(f"{Colors.ERROR}Error: {hw_details['error']}{Colors.RESET}")
        return

    print(format_subheader("Jenkins Nodes Hardware Information"))

    # Create table
    table = Texttable()
    table.set_deco(Texttable.HEADER | Texttable.VLINES | Texttable.HLINES)
    table.set_cols_align(["l", "l", "l", "l", "l", "l", "l", "l", "l"])
    table.set_cols_width([15, 10, 15, 10, 15, 15, 8, 10, 8])
    
    # Add header
    table.add_row(["Node Name", "Vendor", "Model", "Type", "Serial", "CPU", "RAM", "Disk", "Swap"])
    
    # Add data
    nodes = hw_details.get('hardware_details', [])
    for node in nodes:
        table.add_row([
            node.get('name', 'Unknown'),
            node.get('vendor', 'Unknown'),
            node.get('model', 'Unknown'),
            node.get('type', 'Unknown'),
            node.get('serial', 'Unknown'),
            node.get('cpu', 'Unknown'),
            node.get('ram', 'Unknown'),
            node.get('disk', 'Unknown'),
            node.get('swap', 'Unknown')
        ])
    
    print(table.draw())
    print()

def display_software_details(sw_details):
    """
    Display software details for nodes in a tabular format

    Args:
        sw_details: Software details information
    """
    if "error" in sw_details:
        print(f"{Colors.ERROR}Error: {sw_details['error']}{Colors.RESET}")
        return

    print(format_subheader("Jenkins Nodes Software & System Information"))

    # Create table
    table = Texttable()
    table.set_deco(Texttable.HEADER | Texttable.VLINES | Texttable.HLINES)
    table.set_cols_align(["l", "l", "l", "l"])
    table.set_cols_width([20, 35, 15, 15])
    
    # Add header
    table.add_row(["Node Name", "JDK Version", "Agent Version", "Clock Difference"])
    
    # Add data
    nodes = sw_details.get('software_details', [])
    for node in nodes:
        table.add_row([
            node.get('name', 'Unknown'),
            node.get('jdk', 'Unknown'),
            node.get('agent_version', 'Unknown'),
            node.get('clock_difference', 'Unknown')
        ])
    
    print(table.draw())
    print()

def display_all_node_details(details):
    """
    Display all detailed information for nodes

    Args:
        details: All detailed node information
    """
    if "error" in details:
        print(f"{Colors.ERROR}Error: {details['error']}{Colors.RESET}")
        return

    print(format_header("JENKINS NODES DETAILED INFORMATION"))
    
    # Display OS details
    os_details = {'os_details': details.get('os_details', [])}
    display_os_details(os_details)
    
    # Display hardware details
    hw_details = {'hardware_details': details.get('hardware_details', [])}
    display_hardware_details(hw_details)
    
    # Display software details
    sw_details = {'software_details': details.get('software_details', [])}
    display_software_details(sw_details)
