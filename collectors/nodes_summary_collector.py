#!/usr/bin/env python3
"""
Jenkins Nodes Summary Collector
This module collects summarized information about Jenkins nodes/agents.
"""

from collectors.base_collector import BaseCollector

class JenkinsNodesStatCollector(BaseCollector):
    """Collects summarized information about Jenkins nodes/agents"""

    def get_nodes_summary(self):
        """
        Fetches summary information about Jenkins nodes/agents

        Returns:
            dict: Nodes summary information
        """
        try:
            # Get the list of all nodes/computers
            response = self.fetch_jenkins_data("computer/api/json", depth=1)
            if "error" in response:
                return response

            # Extract executor count
            total_executors = response.get('totalExecutors', 0)
            busy_executors = response.get('busyExecutors', 0)
            idle_executors = total_executors - busy_executors

            # Process nodes information
            nodes = response.get('computer', [])
            total_nodes = len(nodes)

            # Track node statuses
            node_status = {
                'online': 0,
                'offline': 0,
                'temp_offline': 0
            }

            # Track OS types
            os_types = {}

            # Track connection types
            connection_types = {}

            # Track labels
            all_labels = set()

            for node in nodes:
                # Check online status
                offline = node.get('offline', True)
                temp_offline = node.get('temporarilyOffline', False)

                if offline:
                    if temp_offline:
                        node_status['temp_offline'] += 1
                    else:
                        node_status['offline'] += 1
                else:
                    node_status['online'] += 1

                # Try to get OS information
                monitor_data = node.get('monitorData', {})
                if 'hudson.node_monitors.ArchitectureMonitor' in monitor_data:
                    architecture = monitor_data.get('hudson.node_monitors.ArchitectureMonitor', '')

                    if isinstance(architecture, str):
                        # Determine OS type from architecture string
                        if 'Windows' in architecture:
                            os_type = 'Windows'
                        elif 'Linux' in architecture:
                            os_type = 'Linux'
                        elif 'Mac' in architecture:
                            os_type = 'Mac'
                        else:
                            os_type = 'Other'

                        # Count OS types
                        if os_type in os_types:
                            os_types[os_type] += 1
                        else:
                            os_types[os_type] = 1

                # Get connection type from class name
                class_name = node.get('_class', '')
                conn_type = self._extract_connection_type(class_name)

                if conn_type in connection_types:
                    connection_types[conn_type] += 1
                else:
                    connection_types[conn_type] = 1

                # Extract labels if available
                if 'assignedLabels' in node:
                    assigned_labels = node.get('assignedLabels', [])
                    if isinstance(assigned_labels, list):
                        for label in assigned_labels:
                            if isinstance(label, dict) and 'name' in label:
                                label_name = label.get('name')
                                if label_name and label_name.strip():
                                    all_labels.add(label_name.strip())

            # Calculate executor utilization
            utilization = (busy_executors / total_executors * 100) if total_executors > 0 else 0

            return {
                'total_nodes': total_nodes,
                'node_status': node_status,
                'total_executors': total_executors,
                'busy_executors': busy_executors,
                'idle_executors': idle_executors,
                'executor_utilization': utilization,
                'os_distribution': os_types,
                'connection_types': connection_types,
                'total_labels': len(all_labels)
            }

        except Exception as e:
            return {"error": f"Error retrieving nodes summary: {str(e)}"}

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
