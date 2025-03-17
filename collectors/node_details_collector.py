#!/usr/bin/env python3
"""
Jenkins Node Details Collector
This module collects detailed information about Jenkins nodes including OS, hardware, and software details.
Uses the Jenkins Script Console for advanced data collection.
"""

import concurrent.futures
import json
import re
from datetime import datetime
from collectors.base_collector import BaseCollector
from collectors.nodes_collector import JenkinsNodesCollector

class JenkinsNodeDetailsCollector(BaseCollector):
    """Collects detailed information about Jenkins nodes/agents including OS, hardware, and software details"""

    def __init__(self, client):
        """Initialize with client and nodes collector"""
        super().__init__(client)
        self.nodes_collector = JenkinsNodesCollector(client)

        # Cache for node details to avoid repeated API calls
        self._node_details_cache = None

    def get_os_details_table(self):
        """
        Get detailed OS information for all nodes

        Returns:
            dict: OS information for all nodes
        """
        try:
            # Use the native API approach to get data instead of Script Console
            nodes_overview = self.nodes_collector.get_nodes_overview()
            if "error" in nodes_overview:
                return nodes_overview

            os_details = []

            # Extract just the OS-related information
            for node in nodes_overview.get('nodes', []):
                os_details.append({
                    'name': node.get('name', 'Unknown'),
                    'machine_name': node.get('name', 'Unknown'),
                    'ip_address': 'Unknown',
                    'os_type': node.get('os_name', 'Unknown'),
                    'os_vendor': node.get('os_name', 'Unknown'),
                    'os_version': node.get('os_version', 'Unknown')
                })

            return {
                'os_details': os_details
            }

        except Exception as e:
            return {"error": f"Error retrieving OS details: {str(e)}"}

    def get_hardware_details_table(self):
        """
        Get detailed hardware information for all nodes

        Returns:
            dict: Hardware information for all nodes
        """
        try:
            # Use the native API approach to get data instead of Script Console
            nodes_overview = self.nodes_collector.get_nodes_overview()
            if "error" in nodes_overview:
                return nodes_overview

            hw_details = []

            # Extract just the hardware-related information
            for node in nodes_overview.get('nodes', []):
                hw_details.append({
                    'name': node.get('name', 'Unknown'),
                    'vendor': node.get('os_name', 'Unknown'),
                    'model': 'Unknown',
                    'type': 'Physical (assumed)',
                    'serial': 'Unknown',
                    'cpu': f"Estimated ~{node.get('num_executors', 1)} cores",
                    'ram': 'Unknown',
                    'disk': node.get('disk_space', 'Unknown'),
                    'swap': 'Unknown'
                })

            return {
                'hardware_details': hw_details
            }

        except Exception as e:
            return {"error": f"Error retrieving hardware details: {str(e)}"}

    def get_software_details_table(self):
        """
        Get detailed software and system information for all nodes

        Returns:
            dict: Software information for all nodes
        """
        try:
            # Use the native API approach to get data instead of Script Console
            nodes_overview = self.nodes_collector.get_nodes_overview()
            if "error" in nodes_overview:
                return nodes_overview

            sw_details = []

            # Extract just the software-related information
            for node in nodes_overview.get('nodes', []):
                sw_details.append({
                    'name': node.get('name', 'Unknown'),
                    'jdk': node.get('jvm_version', 'Unknown'),
                    'agent_version': 'Unknown',
                    'clock_difference': 'Unknown'
                })

            return {
                'software_details': sw_details
            }

        except Exception as e:
            return {"error": f"Error retrieving software details: {str(e)}"}

    def get_all_node_details(self):
        """
        Get all detailed information for all nodes

        Returns:
            dict: All detailed information for all nodes
        """
        try:
            # Get node details (cached)
            nodes_overview = self.nodes_collector.get_nodes_overview()
            if "error" in nodes_overview:
                return nodes_overview

            # Process this data for the three tables
            os_details = []
            hardware_details = []
            software_details = []

            for node in nodes_overview.get('nodes', []):
                # OS details
                os_details.append({
                    'name': node.get('name', 'Unknown'),
                    'machine_name': node.get('name', 'Unknown'),
                    'ip_address': 'Unknown',
                    'os_type': node.get('os_name', 'Unknown'),
                    'os_vendor': node.get('os_name', 'Unknown'),
                    'os_version': node.get('os_version', 'Unknown')
                })

                # Hardware details
                hardware_details.append({
                    'name': node.get('name', 'Unknown'),
                    'vendor': node.get('os_name', 'Unknown'),
                    'model': 'Unknown',
                    'type': 'Physical (assumed)',
                    'serial': 'Unknown',
                    'cpu': f"Estimated ~{node.get('num_executors', 1)} cores",
                    'ram': 'Unknown',
                    'disk': node.get('disk_space', 'Unknown'),
                    'swap': 'Unknown'
                })

                # Software details
                software_details.append({
                    'name': node.get('name', 'Unknown'),
                    'jdk': node.get('jvm_version', 'Unknown'),
                    'agent_version': 'Unknown',
                    'clock_difference': 'Unknown'
                })

            return {
                'os_details': os_details,
                'hardware_details': hardware_details,
                'software_details': software_details
            }

        except Exception as e:
            return {"error": f"Error retrieving all node details: {str(e)}"}

    def get_node_details_with_script_console(self):
        """
        Get node details using Jenkins API (fallback from Script Console)

        Returns:
            dict: Node details collected from all nodes
        """
        # If we already have the data, return it
        if self._node_details_cache is not None:
            return self._node_details_cache

        try:
            # Use the nodes_collector to get data instead of the Script Console
            nodes_overview = self.nodes_collector.get_nodes_overview()
            if "error" in nodes_overview:
                return nodes_overview

            all_node_details = []

            for node in nodes_overview.get('nodes', []):
                # Extract and format the data from the regular API
                node_info = {
                    "name": node.get('name', 'Unknown'),
                    "machine_name": node.get('name', 'Unknown'),
                    "description": node.get('description', 'Unknown'),
                    "status": node.get('status', 'Unknown'),
                    "architecture": node.get('architecture', 'Unknown'),
                    "disk_space": node.get('disk_space', 'Unknown'),
                    "jdk_version": node.get('jvm_version', 'Unknown'),
                    "os_type": node.get('os_name', 'Unknown'),
                    "os_vendor": node.get('os_name', 'Unknown'),
                    "os_version": node.get('os_version', 'Unknown'),
                    "vendor": node.get('os_name', 'Unknown'),
                    "model": "Unknown",
                    "hardware_type": "Physical (assumed)",
                    "serial": "Unknown",
                    "cpu": f"Estimated ~{node.get('num_executors', 1)} cores",
                    "ram": "Unknown",
                    "swap": "Unknown",
                    "agent_version": "Unknown",
                    "clock_difference": "Unknown",
                    "ip_address": "Unknown"
                }

                all_node_details.append(node_info)

            # Cache the results
            self._node_details_cache = {'all_node_details': all_node_details}
            return self._node_details_cache

        except Exception as e:
            print(f"Debug - Overall exception: {str(e)}")
            return {"error": f"Error retrieving node details: {str(e)}"}
