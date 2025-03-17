#!/usr/bin/env python3
"""
Jenkins Disk Usage Information Collector
This module collects information about Jenkins disk usage.
"""

from collectors.base_collector import BaseCollector

class JenkinsDiskCollector(BaseCollector):
    """Collects information about Jenkins disk usage"""

    def get_disk_summary(self):
        """
        Fetches summary information about Jenkins disk usage

        Returns:
            dict: Disk usage information summary
        """
        try:
            # Get disk space monitor data from nodes to estimate total disk usage
            response = self.fetch_jenkins_data("computer/api/json", depth=2)
            if "error" in response:
                return response

            nodes = response.get('computer', [])

            # Initialize disk space tracking
            total_disk = 0
            free_disk = 0

            for node in nodes:
                monitor_data = node.get('monitorData', {})

                # Check for disk space monitor
                if 'hudson.node_monitors.DiskSpaceMonitor' in monitor_data:
                    disk_space = monitor_data.get('hudson.node_monitors.DiskSpaceMonitor', {})

                    if isinstance(disk_space, dict):
                        # Add to total disk space (assumes in bytes)
                        if 'size' in disk_space:
                            total_disk = disk_space.get('size', 0)

                        # Calculate free space if available
                        if 'freeSpace' in disk_space:
                            free_disk = disk_space.get('freeSpace', 0)

            # Try to get job disk usage if the plugin is available
            job_disk_usage = "Unknown"
            build_disk_usage = "Unknown"

            # First check if disk-usage plugin is available
            response = self.fetch_jenkins_data("disk-usage/api/json")
            if "error" not in response:
                # Extract job and build disk usage
                if 'jobsDiskUsage' in response:
                    job_disk_usage = response.get('jobsDiskUsage', 0)

                if 'buildsDiskUsage' in response:
                    build_disk_usage = response.get('buildsDiskUsage', 0)

            # Try to get disk usage by job from the disk-usage plugin
            top_jobs_by_size = []
            try:
                response = self.fetch_jenkins_data("job/*/disk-usage/")
                # This would need HTML parsing to extract detailed job data
            except:
                # Best effort attempt
                pass

            # Calculate used disk space and usage percentage
            used_disk = total_disk - free_disk
            usage_percent = (used_disk / total_disk * 100) if total_disk > 0 else 0

            # Convert to GB for display
            total_disk_gb = total_disk / (1024**3)
            free_disk_gb = free_disk / (1024**3)
            used_disk_gb = used_disk / (1024**3)

            # Get job workspace sizes if available
            workspace_sizes = {}

            # Try to get JENKINS_HOME size from disk usage plugin
            jenkins_home_size = "Unknown"
            try:
                response = self.fetch_jenkins_data("disk-usage/jenkinsHomeUsage/api/json")
                if "error" not in response and 'size' in response:
                    jenkins_home_size = response.get('size', 0)
            except:
                pass

            return {
                'total_disk_gb': total_disk_gb,
                'free_disk_gb': free_disk_gb,
                'used_disk_gb': used_disk_gb,
                'usage_percent': usage_percent,
                'job_disk_usage': job_disk_usage,
                'build_disk_usage': build_disk_usage,
                'jenkins_home_size': jenkins_home_size,
                'top_jobs_by_size': top_jobs_by_size
            }

        except Exception as e:
            return {"error": f"Error retrieving disk summary: {str(e)}"}
