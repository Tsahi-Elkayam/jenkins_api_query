#!/usr/bin/env python3
"""
Jenkins Nodes Information Collector
This module collects information about Jenkins nodes/agents.
"""

import re
from datetime import datetime
from collectors.base_collector import BaseCollector

class JenkinsNodesCollector(BaseCollector):
    """Collects information about Jenkins nodes/agents"""

    def _extract_labels(self, node):
        """
        Extract labels from node information

        Args:
            node: Node information dictionary

        Returns:
            str: Space-separated list of labels
        """
        # Try different ways to get labels
        labels = []

        # First check if assignedLabels are directly available
        if 'assignedLabels' in node:
            assigned_labels = node.get('assignedLabels', [])
            if isinstance(assigned_labels, list):
                # Extract label names from objects
                for label in assigned_labels:
                    if isinstance(label, dict) and 'name' in label:
                        label_name = label.get('name')
                        if label_name and label_name.strip():  # Skip empty labels
                            labels.append(label_name.strip())

        # If that fails, check for labelString
        if not labels and 'labelString' in node:
            label_string = node.get('labelString', '')
            if label_string:
                # Split by spaces or commas
                for part in re.split(r'[\s,]+', label_string):
                    if part.strip():
                        labels.append(part.strip())

        # Remove duplicates and join with spaces
        return ' '.join(sorted(set(labels)))

    def _extract_connection_type(self, class_name):
        """
        Extract connection type from class name

        Args:
            class_name: Node class name

        Returns:
            str: Connection type
        """
        # Map class names to connection types
        if 'hudson.slaves.DumbSlave' in class_name:
            return 'Agent'
        elif 'hudson.model.Hudson$MasterComputer' in class_name:
            return 'Built-in Node'
        elif 'hudson.slaves.SlaveComputer' in class_name:
            return 'Agent'
        elif 'jenkins.slaves.JnlpSlaveAgentProtocol' in class_name or 'JNLPLauncher' in class_name:
            return 'JNLP Agent'
        elif 'SSHLauncher' in class_name:
            return 'SSH Agent'
        elif 'ComputerLauncher' in class_name:
            return 'Custom Launcher'
        elif 'DockerComputer' in class_name:
            return 'Docker Agent'
        elif 'KubernetesComputer' in class_name:
            return 'Kubernetes Agent'
        elif 'EC2Computer' in class_name:
            return 'EC2 Agent'
        else:
            return 'Unknown Agent Type'

    def _extract_os_info_from_labels(self, labels):
        """
        Extract OS information from node labels

        Args:
            labels: Space-separated list of node labels

        Returns:
            dict or None: OS information if found, None otherwise
        """
        if not labels:
            return None

        # Patterns for common OS distributions and versions in labels
        patterns = [
            # Ubuntu patterns
            (r'ubuntu[\-_]?(\d+[\.\-_]?\d+)', 'Ubuntu', lambda v: f"Ubuntu {v.replace('_', '.').replace('-', '.')}"),
            # CentOS patterns
            (r'centos[\-_]?(\d+(\.\d+)*)', 'CentOS', lambda v: f"CentOS {v.replace('_', '.').replace('-', '.')}"),
            # RHEL patterns
            (r'rhel[\-_]?(\d+(\.\d+)*)', 'RHEL', lambda v: f"RHEL {v.replace('_', '.').replace('-', '.')}"),
            # Debian patterns
            (r'debian[\-_]?(\d+(\.\d+)*)', 'Debian', lambda v: f"Debian {v.replace('_', '.').replace('-', '.')}"),
            # Fedora patterns
            (r'fedora[\-_]?(\d+)', 'Fedora', lambda v: f"Fedora {v}"),
            # Windows patterns
            (r'win[\-_]?(\d+)', 'Windows', lambda v: f"Windows {v}"),
            (r'windows[\-_]?(\d+)', 'Windows', lambda v: f"Windows {v}"),
            (r'win[\-_]?server[\-_]?(\d+)', 'Windows', lambda v: f"Windows Server {v}"),
            # More specific Ubuntu patterns
            (r'bionic', 'Ubuntu', lambda v: "Ubuntu 18.04"),
            (r'focal', 'Ubuntu', lambda v: "Ubuntu 20.04"),
            (r'jammy', 'Ubuntu', lambda v: "Ubuntu 22.04"),
            (r'noble', 'Ubuntu', lambda v: "Ubuntu 24.04"),
            # More specific Debian patterns
            (r'buster', 'Debian', lambda v: "Debian 10"),
            (r'bullseye', 'Debian', lambda v: "Debian 11"),
            (r'bookworm', 'Debian', lambda v: "Debian 12"),
        ]

        for pattern, os_name, full_name_func in patterns:
            match = re.search(pattern, labels.lower())
            if match:
                return {
                    'name': os_name,
                    'full_name': full_name_func(match.group(1)) if callable(full_name_func) else full_name_func
                }

        return None

    def _extract_os_info_from_name(self, node_name):
        """
        Try to guess OS information from node name

        Args:
            node_name: Name of the node

        Returns:
            dict or None: OS information if found, None otherwise
        """
        if not node_name:
            return None

        # Patterns to match in node names
        patterns = [
            # Ubuntu patterns in node names
            (r'ubuntu[\-_]?(\d+[\.\-_]?\d+)', 'Ubuntu', lambda v: f"Ubuntu {v.replace('_', '.').replace('-', '.')}"),
            # Common Ubuntu version codenames in node names
            (r'bionic', 'Ubuntu', lambda v: "Ubuntu 18.04"),
            (r'focal', 'Ubuntu', lambda v: "Ubuntu 20.04"),
            (r'jammy', 'Ubuntu', lambda v: "Ubuntu 22.04"),
            # CentOS patterns in node names
            (r'centos[\-_]?(\d+)', 'CentOS', lambda v: f"CentOS {v}"),
            # RHEL patterns in node names
            (r'rhel[\-_]?(\d+)', 'RHEL', lambda v: f"RHEL {v}"),
            # Debian patterns in node names
            (r'debian[\-_]?(\d+)', 'Debian', lambda v: f"Debian {v}"),
            # Windows patterns in node names
            (r'win[\-_]?(\d+)', 'Windows', lambda v: f"Windows {v}"),
            (r'win[\-_]?server[\-_]?(\d+)', 'Windows', lambda v: f"Windows Server {v}"),
        ]

        lower_name = node_name.lower()

        for pattern, os_name, full_name_func in patterns:
            match = re.search(pattern, lower_name)
            if match:
                return {
                    'name': os_name,
                    'full_name': full_name_func(match.group(1)) if callable(full_name_func) else full_name_func
                }

        # Check for certain node naming patterns that indicate OS
        if 'ubuntu' in lower_name:
            return {'name': 'Ubuntu', 'full_name': 'Ubuntu'}
        elif 'centos' in lower_name:
            return {'name': 'CentOS', 'full_name': 'CentOS'}
        elif 'rhel' in lower_name or 'redhat' in lower_name:
            return {'name': 'RHEL', 'full_name': 'RHEL'}
        elif 'debian' in lower_name:
            return {'name': 'Debian', 'full_name': 'Debian'}
        elif 'fedora' in lower_name:
            return {'name': 'Fedora', 'full_name': 'Fedora'}
        elif 'win' in lower_name:
            return {'name': 'Windows', 'full_name': 'Windows'}

        return None

    def _extract_detailed_os_info(self, node_info, architecture):
        """
        Extract detailed OS information including specific versions

        Args:
            node_info: Node information dictionary to update
            architecture: Architecture string containing OS information

        Returns:
            dict: Updated node_info dictionary with detailed OS information
        """
        # Default values
        node_info['os_name'] = 'Unknown'
        node_info['os_full_name'] = 'Unknown'

        # Extract OS info from labels first (most reliable for Linux distributions)
        label_os_info = self._extract_os_info_from_labels(node_info.get('labels', ''))
        if label_os_info:
            node_info['os_name'] = label_os_info['name']
            node_info['os_full_name'] = label_os_info['full_name']
            return node_info

        # Try to extract from architecture string
        if architecture and isinstance(architecture, str):
            # First try to identify OS family
            os_family_match = re.match(r'^(Windows|Linux|Mac|macOS|Ubuntu|CentOS|RHEL|Debian|Fedora)', architecture)
            if os_family_match:
                os_family = os_family_match.group(1)
                node_info['os_name'] = os_family

                # Extract detailed version information
                if os_family == 'Windows':
                    # Handle Windows versions (Windows 10, Windows Server 2019, etc.)
                    win_version_match = re.match(r'^Windows\s+(Server\s+\d+|\d+|XP|Vista|7|8|8.1|10|11)', architecture)
                    if win_version_match:
                        node_info['os_full_name'] = f"Windows {win_version_match.group(1)}"
                    else:
                        node_info['os_full_name'] = "Windows"

                elif os_family == 'Linux':
                    # Try to extract Linux distribution and version
                    ubuntu_match = re.search(r'Ubuntu\s+(\d+\.\d+)', architecture)
                    centos_match = re.search(r'CentOS\s+(\d+(\.\d+)*)', architecture)
                    rhel_match = re.search(r'RHEL\s+(\d+(\.\d+)*)', architecture)
                    debian_match = re.search(r'Debian\s+(\d+(\.\d+)*)', architecture)
                    fedora_match = re.search(r'Fedora\s+(\d+)', architecture)

                    if ubuntu_match:
                        node_info['os_name'] = 'Ubuntu'
                        node_info['os_full_name'] = f"Ubuntu {ubuntu_match.group(1)}"
                    elif centos_match:
                        node_info['os_name'] = 'CentOS'
                        node_info['os_full_name'] = f"CentOS {centos_match.group(1)}"
                    elif rhel_match:
                        node_info['os_name'] = 'RHEL'
                        node_info['os_full_name'] = f"RHEL {rhel_match.group(1)}"
                    elif debian_match:
                        node_info['os_name'] = 'Debian'
                        node_info['os_full_name'] = f"Debian {debian_match.group(1)}"
                    elif fedora_match:
                        node_info['os_name'] = 'Fedora'
                        node_info['os_full_name'] = f"Fedora {fedora_match.group(1)}"
                    else:
                        # Try to guess distribution from node name
                        name_os_info = self._extract_os_info_from_name(node_info.get('name', ''))
                        if name_os_info:
                            node_info['os_name'] = name_os_info['name']
                            node_info['os_full_name'] = name_os_info['full_name']
                        else:
                            node_info['os_full_name'] = "Linux"

                elif os_family in ['Mac', 'macOS']:
                    # Handle macOS versions
                    mac_version_match = re.search(r'(Mac|macOS)\s+((\d+(\.\d+)*)|Catalina|Big Sur|Monterey|Ventura|Sonoma)', architecture)
                    if mac_version_match:
                        node_info['os_name'] = 'macOS'
                        node_info['os_full_name'] = f"macOS {mac_version_match.group(2)}"
                    else:
                        node_info['os_full_name'] = "macOS"
                else:
                    # For other OS types, just use what we found
                    node_info['os_full_name'] = os_family
        else:
            # If no architecture string, try to extract from node name
            name_os_info = self._extract_os_info_from_name(node_info.get('name', ''))
            if name_os_info:
                node_info['os_name'] = name_os_info['name']
                node_info['os_full_name'] = name_os_info['full_name']
            else:
                # Default to generic OS family if we couldn't determine version
                if node_info['os_name'] == 'Linux':
                    node_info['os_full_name'] = 'Linux'
                elif node_info['os_name'] == 'Windows':
                    node_info['os_full_name'] = 'Windows'
                else:
                    node_info['os_name'] = 'Unknown'
                    node_info['os_full_name'] = 'Unknown'

        return node_info

    def debug_nodes_labels(self, processed_nodes):
        """Log node labels for debugging OS detection"""
        print("=== DEBUG: NODE LABELS DEBUGGING ===")
        for node in processed_nodes[:20]:  # First 20 nodes
            print(f"Node: {node.get('name')}")
            print(f"  Architecture: {node.get('architecture', 'None')}")
            print(f"  Labels: {node.get('labels', 'None')}")
        print("======================================")

    def get_nodes_overview(self):
        """
        Fetches overview information about all nodes

        Returns:
            dict: Nodes overview information
        """
        try:
            # Get the list of all nodes/computers with detailed information
            response = self.fetch_jenkins_data("computer/api/json", depth=2)
            if "error" in response:
                return response

            # Extract total executor count
            total_executors = response.get('totalExecutors', 0)
            busy_executors = response.get('busyExecutors', 0)

            # Process the nodes information
            nodes = response.get('computer', [])
            processed_nodes = []

            # Track node statuses
            status_counts = {
                'online': 0,
                'offline': 0,
                'temp_offline': 0
            }

            # Track unique labels
            all_labels = set()

            # Track OS distributions with detailed versions
            os_distribution = {}

            for node in nodes:
                if not isinstance(node, dict):
                    continue

                # Basic node info
                node_info = {
                    'name': node.get('displayName', 'Unknown'),
                    'description': node.get('description', ''),
                    'url': f"{self.url}computer/{node.get('displayName', '')}/"
                }

                # Get status information
                node_info['offline'] = node.get('offline', True)
                node_info['temporarily_offline'] = node.get('temporarilyOffline', False)

                if node_info['offline']:
                    if node_info['temporarily_offline']:
                        node_info['status'] = 'Temporarily Offline'
                        status_counts['temp_offline'] += 1
                    else:
                        node_info['status'] = 'Offline'
                        status_counts['offline'] += 1
                else:
                    node_info['status'] = 'Online'
                    status_counts['online'] += 1

                # Store JVM version for later analysis
                if 'hudson.node_monitors.JavaInfo' in node.get('monitorData', {}):
                    java_info = node.get('monitorData', {}).get('hudson.node_monitors.JavaInfo', {})
                    if isinstance(java_info, dict):
                        node_info['jvm_version'] = java_info.get('version', 'Unknown')
                    else:
                        node_info['jvm_version'] = str(java_info) if java_info else 'Unknown'
                else:
                    node_info['jvm_version'] = 'Unknown'

                # Get labels
                labels_string = self._extract_labels(node)
                node_info['labels'] = labels_string.strip() if labels_string else ""

                # Add to all labels set
                if labels_string:
                    all_labels.update([label.strip() for label in labels_string.split() if label.strip()])

                # Get monitoring data if available
                monitoring = node.get('monitorData', {})

                # Get executor information
                node_info['num_executors'] = node.get('numExecutors', 0)

                # Get idle executors
                executors = node.get('executors', [])
                idle_executors = sum(1 for executor in executors if executor.get('idle', True))
                node_info['idle_executors'] = idle_executors
                node_info['busy_executors'] = node_info['num_executors'] - idle_executors

                # Get disk space
                if 'hudson.node_monitors.DiskSpaceMonitor' in monitoring:
                    disk_space = monitoring.get('hudson.node_monitors.DiskSpaceMonitor', {})
                    if isinstance(disk_space, dict) and 'size' in disk_space and 'path' in disk_space:
                        try:
                            # Convert to GB and format
                            size_gb = disk_space.get('size', 0) / (1024 ** 3)
                            node_info['disk_space'] = f"{size_gb:.2f} GB"
                            node_info['disk_path'] = disk_space.get('path', '')
                        except (TypeError, ValueError):
                            node_info['disk_space'] = 'Unknown'
                            node_info['disk_path'] = ''
                    else:
                        node_info['disk_space'] = 'Unknown'
                        node_info['disk_path'] = ''
                else:
                    node_info['disk_space'] = 'Unknown'
                    node_info['disk_path'] = ''

                # Get response time
                if 'hudson.node_monitors.ResponseTimeMonitor' in monitoring:
                    response_time = monitoring.get('hudson.node_monitors.ResponseTimeMonitor', {})
                    if isinstance(response_time, dict) and 'average' in response_time:
                        try:
                            avg_ms = response_time.get('average', 0)
                            node_info['response_time'] = f"{avg_ms:.2f} ms"
                        except (TypeError, ValueError):
                            node_info['response_time'] = 'Unknown'
                    else:
                        node_info['response_time'] = 'Unknown'
                else:
                    node_info['response_time'] = 'Unknown'

                # Get architecture and OS info if available
                if 'hudson.node_monitors.ArchitectureMonitor' in monitoring:
                    architecture = monitoring.get('hudson.node_monitors.ArchitectureMonitor', '')
                    node_info['architecture'] = architecture if architecture else 'Unknown'

                    # Extract OS info from architecture if available
                    if architecture and isinstance(architecture, str):
                        # Enhanced OS detection with detailed version information
                        node_info = self._extract_detailed_os_info(node_info, architecture)

                        # Update OS distribution counts
                        os_key = node_info['os_full_name']
                        if os_key in os_distribution:
                            os_distribution[os_key] += 1
                        else:
                            os_distribution[os_key] = 1
                    else:
                        node_info['os_name'] = 'Unknown'
                        node_info['os_full_name'] = 'Unknown'
                else:
                    node_info['architecture'] = 'Unknown'
                    node_info['os_name'] = 'Unknown'
                    node_info['os_full_name'] = 'Unknown'

                # Get connection details
                if node.get('_class', ''):
                    node_info['connection_type'] = self._extract_connection_type(node.get('_class', ''))
                else:
                    node_info['connection_type'] = 'Unknown'

                # Get last connection time for agents that have been connected before
                if not node_info['offline'] or node_info['temporarily_offline']:
                    node_info['last_connection'] = 'Currently Connected'
                elif 'connectTime' in node:
                    try:
                        connect_time = node.get('connectTime', 0)
                        if connect_time > 0:
                            dt = datetime.fromtimestamp(connect_time / 1000)  # Convert from ms to seconds
                            node_info['last_connection'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            node_info['last_connection'] = 'Never'
                    except (ValueError, TypeError):
                        node_info['last_connection'] = 'Unknown'
                else:
                    node_info['last_connection'] = 'Unknown'

                processed_nodes.append(node_info)

            # Debug node architecture strings - uncomment if needed for troubleshooting
            # self.debug_nodes_labels(processed_nodes)

            return {
                'total_nodes': len(processed_nodes),
                'total_executors': total_executors,
                'busy_executors': busy_executors,
                'idle_executors': total_executors - busy_executors,
                'status_counts': status_counts,
                'nodes': processed_nodes,
                'all_labels': list(all_labels),
                'os_distribution': os_distribution
            }

        except Exception as e:
            return {"error": f"Error retrieving nodes overview: {str(e)}"}

    def get_os_distribution_summary(self):
        """
        Get a summary of OS distribution with detailed versions

        Returns:
            dict: OS distribution summary
        """
        try:
            overview = self.get_nodes_overview()
            if "error" in overview:
                return overview

            return {
                'os_distribution': overview.get('os_distribution', {})
            }
        except Exception as e:
            return {"error": f"Error retrieving OS distribution summary: {str(e)}"}

    def get_nodes_summary(self):
        """
        Fetches summarized information about Jenkins nodes/agents

        Returns:
            dict: Nodes summary information
        """
        try:
            # Get overview data first
            overview = self.get_nodes_overview()
            if "error" in overview:
                return overview

            # Extract key metrics for the summary
            return {
                'total_nodes': overview.get('total_nodes', 0),
                'node_status': overview.get('status_counts', {}),
                'total_executors': overview.get('total_executors', 0),
                'busy_executors': overview.get('busy_executors', 0),
                'idle_executors': overview.get('idle_executors', 0),
                'executor_utilization': (overview.get('busy_executors', 0) / overview.get('total_executors', 1) * 100)
                                        if overview.get('total_executors', 0) > 0 else 0,
                'all_labels': overview.get('all_labels', []),
                'os_distribution': overview.get('os_distribution', {})  # Add OS distribution to summary
            }

        except Exception as e:
            return {"error": f"Error retrieving nodes summary: {str(e)}"}
