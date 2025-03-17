#!/usr/bin/env python3
"""
Jenkins Alerts Collector
This module analyzes Jenkins data and generates alerts and warnings.
"""

from collectors.base_collector import BaseCollector

class JenkinsAlertsCollector(BaseCollector):
    """Analyzes Jenkins data and identifies alerts and warnings"""

    def __init__(self, client):
        """
        Initialize with a JenkinsClient instance

        Args:
            client: Authenticated JenkinsClient instance
        """
        super().__init__(client)
        self.warnings = []
        self.critical_alerts = []

    def analyze_disk_usage(self, disk_info):
        """
        Analyze disk usage and add warnings if needed

        Args:
            disk_info: Disk usage information from JenkinsDiskCollector
        """
        if not disk_info or "error" in disk_info:
            return

        # Check for high disk usage
        usage_percent = disk_info.get('usage_percent', 0)
        if usage_percent >= 95:
            self.critical_alerts.append({
                'category': 'Disk Space',
                'message': f"CRITICAL: Disk usage at {usage_percent:.1f}% - Immediate cleanup required",
                'details': f"Free space: {disk_info.get('free_disk_gb', 0):.2f} GB",
                'impact': 'HIGH',
                'icon': '💾'
            })
        elif usage_percent >= 85:
            self.warnings.append({
                'category': 'Disk Space',
                'message': f"WARNING: Disk usage high at {usage_percent:.1f}%",
                'details': f"Free space: {disk_info.get('free_disk_gb', 0):.2f} GB",
                'impact': 'MEDIUM',
                'icon': '💾'
            })

    def analyze_nodes(self, nodes_info):
        """
        Analyze nodes information and add warnings if needed

        Args:
            nodes_info: Nodes information from JenkinsNodesCollector
        """
        if not nodes_info or "error" in nodes_info:
            return

        # Check for offline nodes
        offline_count = nodes_info.get('status_counts', {}).get('offline', 0)
        temp_offline_count = nodes_info.get('status_counts', {}).get('temp_offline', 0)
        total_nodes = nodes_info.get('total_nodes', 0)

        if offline_count > 0:
            offline_percentage = (offline_count / total_nodes * 100) if total_nodes > 0 else 0
            if offline_percentage >= 20:
                self.critical_alerts.append({
                    'category': 'Node Status',
                    'message': f"CRITICAL: {offline_count} nodes offline ({offline_percentage:.1f}% of total)",
                    'details': "Check node connectivity issues",
                    'impact': 'HIGH',
                    'icon': '🖥️'
                })
            else:
                self.warnings.append({
                    'category': 'Node Status',
                    'message': f"WARNING: {offline_count} nodes offline",
                    'details': "Check node connectivity issues",
                    'impact': 'MEDIUM',
                    'icon': '🖥️'
                })

        if temp_offline_count > 0:
            self.warnings.append({
                'category': 'Node Status',
                'message': f"WARNING: {temp_offline_count} nodes temporarily offline",
                'details': "Check if maintenance is in progress",
                'impact': 'LOW',
                'icon': '🖥️'
            })

        # Check for high executor utilization
        utilization = (nodes_info.get('busy_executors', 0) / nodes_info.get('total_executors', 1) * 100) if nodes_info.get('total_executors', 0) > 0 else 0
        if utilization >= 90:
            self.warnings.append({
                'category': 'Executor Usage',
                'message': f"WARNING: High executor utilization ({utilization:.1f}%)",
                'details': f"Consider adding more executors or optimizing builds",
                'impact': 'MEDIUM',
                'icon': '⚙️'
            })

    def analyze_jobs(self, jobs_info):
        """
        Analyze jobs information and add warnings if needed

        Args:
            jobs_info: Jobs information from JenkinsJobsCollector
        """
        if not jobs_info or "error" in jobs_info:
            return

        # Check for failed jobs
        failed_count = jobs_info.get('status_counts', {}).get('Failed', 0)
        unstable_count = jobs_info.get('status_counts', {}).get('Unstable', 0)
        total_jobs = jobs_info.get('total_jobs', 0)

        if failed_count > 0:
            failed_percentage = (failed_count / total_jobs * 100) if total_jobs > 0 else 0
            if failed_percentage >= 25:
                self.critical_alerts.append({
                    'category': 'Job Status',
                    'message': f"CRITICAL: {failed_count} failed jobs ({failed_percentage:.1f}% of total)",
                    'details': "Check console logs for error patterns",
                    'impact': 'HIGH',
                    'icon': '❌'
                })
            elif failed_count >= 10:
                self.warnings.append({
                    'category': 'Job Status',
                    'message': f"WARNING: {failed_count} failed jobs",
                    'details': "Review build logs for common issues",
                    'impact': 'MEDIUM',
                    'icon': '❌'
                })

        if unstable_count > 0:
            unstable_percentage = (unstable_count / total_jobs * 100) if total_jobs > 0 else 0
            if unstable_percentage >= 20:
                self.warnings.append({
                    'category': 'Job Status',
                    'message': f"WARNING: {unstable_count} unstable jobs ({unstable_percentage:.1f}% of total)",
                    'details': "Check tests for flakiness",
                    'impact': 'MEDIUM',
                    'icon': '⚠️'
                })

        # Check for low success rate
        success_rate = jobs_info.get('success_rate', 0)
        if success_rate <= 50:
            self.critical_alerts.append({
                'category': 'Build Success',
                'message': f"CRITICAL: Low build success rate ({success_rate:.1f}%)",
                'details': "Major build reliability issues",
                'impact': 'HIGH',
                'icon': '📊'
            })
        elif success_rate <= 75:
            self.warnings.append({
                'category': 'Build Success',
                'message': f"WARNING: Moderate build success rate ({success_rate:.1f}%)",
                'details': "Build reliability issues",
                'impact': 'MEDIUM',
                'icon': '📊'
            })

    def analyze_queue(self, queue_info):
        """
        Analyze queue information and add warnings if needed

        Args:
            queue_info: Queue information from JenkinsQueueCollector
        """
        if not queue_info or "error" in queue_info:
            return

        # Check for large queue
        items_in_queue = queue_info.get('items_in_queue', 0)
        if items_in_queue >= 20:
            self.critical_alerts.append({
                'category': 'Build Queue',
                'message': f"CRITICAL: {items_in_queue} items in queue",
                'details': "Severe build backlog, check executor availability",
                'impact': 'HIGH',
                'icon': '⏱️'
            })
        elif items_in_queue >= 10:
            self.warnings.append({
                'category': 'Build Queue',
                'message': f"WARNING: {items_in_queue} items in queue",
                'details': "Build backlog forming, check executor availability",
                'impact': 'MEDIUM',
                'icon': '⏱️'
            })

    def analyze_plugins(self, plugins_info):
        """
        Analyze plugins information and add warnings if needed

        Args:
            plugins_info: Plugins information from JenkinsPluginsCollector
        """
        if not plugins_info or "error" in plugins_info:
            return

        # Check for large number of updates
        updates_available = plugins_info.get('updates_available', 0)
        total_plugins = plugins_info.get('total_plugins', 0)

        if updates_available > 0:
            updates_percentage = (updates_available / total_plugins * 100) if total_plugins > 0 else 0
            if updates_percentage >= 40:
                self.warnings.append({
                    'category': 'Plugin Updates',
                    'message': f"WARNING: {updates_available} plugins need updates ({updates_percentage:.1f}% of total)",
                    'details': "Schedule a maintenance window to update plugins",
                    'impact': 'LOW',
                    'icon': '🔌'
                })

        # Check for security updates specifically
        security_updates = 0
        for plugin in plugins_info.get('update_list', []):
            if 'security' in plugin.get('name', '').lower():
                security_updates += 1

        if security_updates > 0:
            self.critical_alerts.append({
                'category': 'Security Updates',
                'message': f"CRITICAL: {security_updates} security-related plugins need updates",
                'details': "Security vulnerabilities may exist, update immediately",
                'impact': 'HIGH',
                'icon': '🔒'
            })

    def analyze_system(self, system_info):
        """
        Analyze system information and add warnings if needed

        Args:
            system_info: System information from JenkinsInfoCollector
        """
        if not system_info or "error" in system_info:
            return

        # Check for old Java version
        java_version = system_info.get('javaVersion', '')

        # Simplified Java version check
        if java_version and '1.8' in java_version:
            self.warnings.append({
                'category': 'Java Version',
                'message': f"WARNING: Using Java 8 ({java_version})",
                'details': "Consider upgrading to Java 11 or newer for better security and performance",
                'impact': 'LOW',
                'icon': '☕'
            })
        elif java_version and ('1.7' in java_version or '1.6' in java_version):
            self.critical_alerts.append({
                'category': 'Java Version',
                'message': f"CRITICAL: Using outdated Java version ({java_version})",
                'details': "Upgrade to at least Java 11 immediately for security and compatibility",
                'impact': 'HIGH',
                'icon': '☕'
            })

    def get_alerts_summary(self):
        """
        Return a summary of current alerts and warnings

        Returns:
            dict: Summary of alerts and warnings
        """
        return {
            'critical_count': len(self.critical_alerts),
            'warning_count': len(self.warnings),
            'critical_alerts': self.critical_alerts,
            'warnings': self.warnings,
            'total_count': len(self.critical_alerts) + len(self.warnings)
        }
