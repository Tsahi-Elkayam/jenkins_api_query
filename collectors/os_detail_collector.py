#!/usr/bin/env python3
"""
Jenkins OS Details Collector
This module collects detailed information about operating systems used by Jenkins nodes.
"""

import re
from collectors.base_collector import BaseCollector

class JenkinsOSDetailCollector(BaseCollector):
    """Collects detailed OS information from Jenkins nodes"""

    def get_os_details(self):
        """
        Fetches detailed OS information from all Jenkins nodes

        Returns:
            dict: Detailed OS information
        """
        try:
            # Get the nodes with detailed information
            response = self.fetch_jenkins_data("computer/api/json", depth=2)
            if "error" in response:
                return response

            nodes = response.get('computer', [])
            os_details = []

            # Collect OS distribution by category
            os_distribution = {
                'Windows': {},
                'Linux': {},
                'Mac': {},
                'Other': {}
            }

            linux_distributions = {}

            for node in nodes:
                node_name = node.get('displayName', 'Unknown')

                # Get monitor data
                monitor_data = node.get('monitorData', {})

                # Extract architecture info
                arch_info = monitor_data.get('hudson.node_monitors.ArchitectureMonitor', '')

                # Extract system info
                system_info = monitor_data.get('hudson.node_monitors.SystemInfo', {})
                if isinstance(system_info, str):
                    system_info = {'name': system_info}

                # Get OS name and version
                os_name = system_info.get('name', 'Unknown') if isinstance(system_info, dict) else 'Unknown'
                os_version = system_info.get('version', '') if isinstance(system_info, dict) else ''
                os_arch = system_info.get('arch', '') if isinstance(system_info, dict) else ''

                # If OS name is unknown, try to extract from architecture
                if os_name == 'Unknown' and isinstance(arch_info, str):
                    # Match common OS patterns
                    if 'Windows' in arch_info:
                        os_name = 'Windows'
                        # Try to extract Windows version
                        win_version = re.search(r'Windows\s+(\d+(?:\.\d+)?|Server\s+\d+|\w+)', arch_info)
                        if win_version:
                            os_version = win_version.group(1)
                    elif 'Linux' in arch_info:
                        os_name = 'Linux'
                        # Try to extract Linux distribution
                        linux_distro = re.search(r'(Ubuntu|CentOS|Debian|Red\s*Hat|RHEL|Fedora|SUSE)[^\d]*(\d+(?:\.\d+)?)?', arch_info, re.IGNORECASE)
                        if linux_distro:
                            os_name = linux_distro.group(1)
                            if linux_distro.group(2):
                                os_version = linux_distro.group(2)
                    elif 'Mac' in arch_info or 'Darwin' in arch_info:
                        os_name = 'Mac'
                        # Try to extract macOS version
                        mac_version = re.search(r'(\d+\.\d+(?:\.\d+)?)', arch_info)
                        if mac_version:
                            os_version = mac_version.group(1)

                # Get architecture
                if not os_arch and isinstance(arch_info, str):
                    arch_match = re.search(r'\((.*?)\)', arch_info)
                    if arch_match:
                        os_arch = arch_match.group(1)

                # Get kernel version for Linux
                kernel_version = ''
                if os_name in ['Linux', 'Ubuntu', 'CentOS', 'Debian', 'Red Hat', 'RHEL', 'Fedora', 'SUSE']:
                    if isinstance(arch_info, str):
                        kernel_match = re.search(r'Linux\s+(\d+\.\d+\.\d+[^\s\)]*)', arch_info)
                        if kernel_match:
                            kernel_version = kernel_match.group(1)

                    # Track Linux distributions
                    if os_name in linux_distributions:
                        linux_distributions[os_name] += 1
                    else:
                        linux_distributions[os_name] = 1

                # Categorize this OS
                category = 'Other'
                if 'Windows' in os_name:
                    category = 'Windows'
                elif os_name in ['Linux', 'Ubuntu', 'CentOS', 'Debian', 'Red Hat', 'RHEL', 'Fedora', 'SUSE']:
                    category = 'Linux'
                elif 'Mac' in os_name or 'Darwin' in os_name:
                    category = 'Mac'

                # Add version to distribution count
                os_key = f"{os_name} {os_version}".strip()
                if os_key in os_distribution[category]:
                    os_distribution[category][os_key] += 1
                else:
                    os_distribution[category][os_key] = 1

                # Create a detailed OS entry
                os_details.append({
                    'node_name': node_name,
                    'os_name': os_name,
                    'os_version': os_version,
                    'os_arch': os_arch,
                    'kernel_version': kernel_version,
                    'full_description': arch_info if isinstance(arch_info, str) else 'Unknown',
                    'category': category
                })

            # Calculate overall totals
            os_totals = {
                'Windows': sum(os_distribution['Windows'].values()),
                'Linux': sum(os_distribution['Linux'].values()),
                'Mac': sum(os_distribution['Mac'].values()),
                'Other': sum(os_distribution['Other'].values())
            }

            return {
                'os_details': os_details,
                'os_distribution': os_distribution,
                'os_totals': os_totals,
                'linux_distributions': linux_distributions
            }

        except Exception as e:
            return {"error": f"Error retrieving OS details: {str(e)}"}

    def get_linux_details(self):
        """
        Fetches detailed information about Linux nodes

        Returns:
            dict: Linux-specific details
        """
        try:
            # Get OS details first
            os_info = self.get_os_details()
            if "error" in os_info:
                return os_info

            # Filter Linux nodes
            linux_nodes = [node for node in os_info.get('os_details', [])
                          if node.get('category') == 'Linux']

            # Get distribution breakdown
            linux_distributions = os_info.get('linux_distributions', {})

            # Check for specific Linux properties
            for node in linux_nodes:
                # Try to extract additional Linux info from JVM version
                response = self.fetch_jenkins_data(f"computer/{node['node_name']}/systemInfo")
                if "error" not in response and "html" in response:
                    html = response["content"]

                    # Check for specific Linux properties
                    for key in ['lsb.release', 'lsb_release', 'DISTRIB_ID', 'DISTRIB_RELEASE']:
                        value = self.extract_property(html, key)
                        if value != "Unknown":
                            node[key] = value

            return {
                'linux_nodes': linux_nodes,
                'linux_distributions': linux_distributions,
                'total_linux_nodes': len(linux_nodes)
            }

        except Exception as e:
            return {"error": f"Error retrieving Linux details: {str(e)}"}
