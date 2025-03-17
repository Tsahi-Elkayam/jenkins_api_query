#!/usr/bin/env python3
"""
Jenkins Hardware Status Collector
This module collects hardware information about Jenkins nodes.
"""

import re
from collectors.base_collector import BaseCollector

class JenkinsHardwareCollector(BaseCollector):
    """Collects hardware information about Jenkins nodes"""

    def get_hardware_info(self):
        """
        Fetches hardware information about all nodes

        Returns:
            dict: Hardware information for all nodes
        """
        try:
            # Get detailed information about all nodes including monitoring data
            response = self.fetch_jenkins_data("computer/api/json", depth=3)
            if "error" in response:
                return response

            nodes = response.get('computer', [])
            hardware_info = []

            for node in nodes:
                node_info = {
                    'name': node.get('displayName', 'Unknown'),
                    'status': 'Online' if not node.get('offline', True) else 'Offline',
                    'connection_type': self._get_connection_type(node.get('_class', '')),
                }

                # Get monitor data if available
                monitor_data = node.get('monitorData', {})

                # Extract CPU information
                node_info['cpu_cores'] = self._extract_cpu_cores(node, monitor_data)
                node_info['cpu_load'] = self._extract_cpu_load(monitor_data)

                # Extract memory information
                node_info['memory_total'] = self._extract_memory_total(monitor_data)
                node_info['memory_used'] = self._extract_memory_used(monitor_data)
                node_info['memory_available'] = self._extract_memory_available(monitor_data)
                node_info['memory_usage_percent'] = self._calculate_memory_usage(
                    node_info['memory_used'],
                    node_info['memory_total']
                )

                # Extract disk information
                node_info['disk_space'] = self._extract_disk_space(monitor_data)
                node_info['disk_space_available'] = self._extract_disk_space_available(monitor_data)
                node_info['disk_usage_percent'] = self._calculate_disk_usage(
                    node_info['disk_space'],
                    node_info['disk_space_available']
                )

                # Extract OS information
                node_info['os_description'] = self._extract_os_description(monitor_data)

                # Extract response time
                node_info['response_time'] = self._extract_response_time(monitor_data)

                hardware_info.append(node_info)

            # Calculate summary statistics
            summary = self._calculate_hardware_summary(hardware_info)

            return {
                'nodes': hardware_info,
                'summary': summary
            }

        except Exception as e:
            return {"error": f"Error retrieving hardware information: {str(e)}"}

    def _extract_cpu_cores(self, node, monitor_data):
        """Extract CPU cores information"""
        try:
            # Try to get from hardware monitor
            if 'hudson.node_monitors.ArchitectureMonitor' in monitor_data:
                arch_info = monitor_data.get('hudson.node_monitors.ArchitectureMonitor', '')
                if isinstance(arch_info, str):
                    # Look for patterns like "4 cores" or "8 CPUs"
                    cores_match = re.search(r'(\d+)\s*(?:core|cpu|processor)', arch_info, re.IGNORECASE)
                    if cores_match:
                        return int(cores_match.group(1))

            # Try node executor count as a fallback
            executor_count = node.get('numExecutors', 0)
            if executor_count > 0:
                return executor_count  # This is a rough estimate

            return "Unknown"
        except Exception:
            return "Unknown"

    def _extract_cpu_load(self, monitor_data):
        """Extract CPU load information"""
        try:
            # Try to get from load monitor
            if 'hudson.node_monitors.SystemLoadMonitor' in monitor_data:
                load_info = monitor_data.get('hudson.node_monitors.SystemLoadMonitor', {})
                if isinstance(load_info, dict) and 'loadAverage' in load_info:
                    return f"{load_info.get('loadAverage', 0):.2f}"

            return "Unknown"
        except Exception:
            return "Unknown"

    def _extract_memory_total(self, monitor_data):
        """Extract total memory information"""
        try:
            # Try to get from memory monitor
            if 'hudson.node_monitors.SwapSpaceMonitor' in monitor_data:
                memory_info = monitor_data.get('hudson.node_monitors.SwapSpaceMonitor', {})
                if isinstance(memory_info, dict) and 'totalPhysicalMemory' in memory_info:
                    memory_bytes = memory_info.get('totalPhysicalMemory', 0)
                    return self.format_bytes(memory_bytes)

            return "Unknown"
        except Exception:
            return "Unknown"

    def _extract_memory_used(self, monitor_data):
        """Extract used memory information"""
        try:
            # Try to get from memory monitor
            if 'hudson.node_monitors.SwapSpaceMonitor' in monitor_data:
                memory_info = monitor_data.get('hudson.node_monitors.SwapSpaceMonitor', {})
                if isinstance(memory_info, dict):
                    total = memory_info.get('totalPhysicalMemory', 0)
                    available = memory_info.get('availablePhysicalMemory', 0)
                    used = total - available
                    return self.format_bytes(used)

            return "Unknown"
        except Exception:
            return "Unknown"

    def _extract_memory_available(self, monitor_data):
        """Extract available memory information"""
        try:
            # Try to get from memory monitor
            if 'hudson.node_monitors.SwapSpaceMonitor' in monitor_data:
                memory_info = monitor_data.get('hudson.node_monitors.SwapSpaceMonitor', {})
                if isinstance(memory_info, dict) and 'availablePhysicalMemory' in memory_info:
                    memory_bytes = memory_info.get('availablePhysicalMemory', 0)
                    return self.format_bytes(memory_bytes)

            return "Unknown"
        except Exception:
            return "Unknown"

    def _calculate_memory_usage(self, used, total):
        """Calculate memory usage percentage"""
        try:
            if used != "Unknown" and total != "Unknown":
                # Extract numeric values from formatted strings
                used_value = self._parse_size_to_bytes(used)
                total_value = self._parse_size_to_bytes(total)

                if total_value > 0:
                    usage_percent = (used_value / total_value) * 100
                    return f"{usage_percent:.1f}%"

            return "Unknown"
        except Exception:
            return "Unknown"

    def _extract_disk_space(self, monitor_data):
        """Extract total disk space information"""
        try:
            # Try to get from disk space monitor
            if 'hudson.node_monitors.DiskSpaceMonitor' in monitor_data:
                disk_info = monitor_data.get('hudson.node_monitors.DiskSpaceMonitor', {})
                if isinstance(disk_info, dict) and 'size' in disk_info:
                    disk_bytes = disk_info.get('size', 0)
                    return self.format_bytes(disk_bytes)

            return "Unknown"
        except Exception:
            return "Unknown"

    def _extract_disk_space_available(self, monitor_data):
        """Extract available disk space information"""
        try:
            # Try to get from disk space monitor
            if 'hudson.node_monitors.DiskSpaceMonitor' in monitor_data:
                disk_info = monitor_data.get('hudson.node_monitors.DiskSpaceMonitor', {})
                if isinstance(disk_info, dict) and 'freeSpace' in disk_info:
                    disk_bytes = disk_info.get('freeSpace', 0)
                    return self.format_bytes(disk_bytes)

            return "Unknown"
        except Exception:
            return "Unknown"

    def _calculate_disk_usage(self, total, available):
        """Calculate disk usage percentage"""
        try:
            if available != "Unknown" and total != "Unknown":
                # Extract numeric values from formatted strings
                available_value = self._parse_size_to_bytes(available)
                total_value = self._parse_size_to_bytes(total)

                if total_value > 0:
                    used_value = total_value - available_value
                    usage_percent = (used_value / total_value) * 100
                    return f"{usage_percent:.1f}%"

            return "Unknown"
        except Exception:
            return "Unknown"

    def _extract_os_description(self, monitor_data):
        """Extract OS description"""
        try:
            # Try to get from architecture monitor
            if 'hudson.node_monitors.ArchitectureMonitor' in monitor_data:
                arch_info = monitor_data.get('hudson.node_monitors.ArchitectureMonitor', '')
                if isinstance(arch_info, str):
                    return arch_info

            # Fallback to system info
            if 'hudson.node_monitors.SystemInfo' in monitor_data:
                sys_info = monitor_data.get('hudson.node_monitors.SystemInfo', {})
                if isinstance(sys_info, dict):
                    os_name = sys_info.get('name', '')
                    os_version = sys_info.get('version', '')
                    os_arch = sys_info.get('arch', '')
                    return f"{os_name} {os_version} ({os_arch})".strip()

            return "Unknown"
        except Exception:
            return "Unknown"

    def _extract_response_time(self, monitor_data):
        """Extract response time information"""
        try:
            # Try to get from response time monitor
            if 'hudson.node_monitors.ResponseTimeMonitor' in monitor_data:
                response_info = monitor_data.get('hudson.node_monitors.ResponseTimeMonitor', {})
                if isinstance(response_info, dict) and 'average' in response_info:
                    avg_ms = response_info.get('average', 0)
                    return f"{avg_ms:.2f} ms"

            return "Unknown"
        except Exception:
            return "Unknown"

    def _get_connection_type(self, class_name):
        """Get connection type from class name"""
        connection_types = {
            'hudson.slaves.DumbSlave': 'Agent',
            'hudson.model.Hudson$MasterComputer': 'Built-in Node',
            'hudson.slaves.SlaveComputer': 'Agent',
            'jenkins.slaves.JnlpSlaveAgentProtocol': 'JNLP Agent',
            'SSHLauncher': 'SSH Agent',
            'ComputerLauncher': 'Custom Launcher',
            'DockerComputer': 'Docker Agent',
            'KubernetesComputer': 'Kubernetes Agent',
            'EC2Computer': 'EC2 Agent'
        }

        for key, value in connection_types.items():
            if key in class_name:
                return value

        return "Unknown"

    def _parse_size_to_bytes(self, size_str):
        """Convert size string back to bytes for calculations"""
        try:
            if isinstance(size_str, (int, float)):
                return size_str

            if not isinstance(size_str, str) or size_str == "Unknown":
                return 0

            # Parse format like "123.45 GB"
            parts = size_str.split()
            if len(parts) != 2:
                return 0

            value = float(parts[0])
            unit = parts[1].upper()

            units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4, "PB": 1024**5}

            if unit in units:
                return value * units[unit]

            return 0
        except Exception:
            return 0

    def _calculate_hardware_summary(self, hardware_info):
        """Calculate summary statistics from hardware info"""
        summary = {
            'total_nodes': len(hardware_info),
            'online_nodes': sum(1 for node in hardware_info if node.get('status') == 'Online'),
            'offline_nodes': sum(1 for node in hardware_info if node.get('status') == 'Offline'),
            'total_cpu_cores': 0,
            'total_memory': 0,
            'total_disk_space': 0
        }

        # Count total cores, memory and disk space
        for node in hardware_info:
            # Add CPU cores if available
            if node.get('cpu_cores') not in (None, "Unknown"):
                try:
                    summary['total_cpu_cores'] += int(node.get('cpu_cores'))
                except (ValueError, TypeError):
                    pass

            # Add memory if available
            memory_total = node.get('memory_total')
            if memory_total not in (None, "Unknown"):
                try:
                    memory_bytes = self._parse_size_to_bytes(memory_total)
                    summary['total_memory'] += memory_bytes
                except (ValueError, TypeError):
                    pass

            # Add disk space if available
            disk_space = node.get('disk_space')
            if disk_space not in (None, "Unknown"):
                try:
                    disk_bytes = self._parse_size_to_bytes(disk_space)
                    summary['total_disk_space'] += disk_bytes
                except (ValueError, TypeError):
                    pass

        # Format memory and disk space
        summary['total_memory_formatted'] = self.format_bytes(summary['total_memory'])
        summary['total_disk_space_formatted'] = self.format_bytes(summary['total_disk_space'])

        return summary
