#!/usr/bin/env python3
"""
Jenkins Executor Usage Collector
This module collects information about Jenkins executor utilization.
"""

from collectors.base_collector import BaseCollector

class JenkinsExecutorUsageCollector(BaseCollector):
    """Collects information about Jenkins executor usage"""

    def get_executor_usage(self):
        """
        Fetches information about executor usage across all nodes

        Returns:
            dict: Executor usage information
        """
        try:
            # Get nodes with executor information
            response = self.fetch_jenkins_data("computer/api/json", depth=2)
            if "error" in response:
                return response

            nodes = response.get('computer', [])

            # Process executor usage by node
            executor_usage = []

            for node in nodes:
                node_name = node.get('displayName', 'Unknown')
                offline = node.get('offline', True)

                # Skip offline nodes
                if offline:
                    continue

                # Get executors information
                executors = node.get('executors', [])
                total_executors = len(executors)

                # Count busy and idle executors
                busy_executors = 0
                executor_info = []

                for executor in executors:
                    idle = executor.get('idle', True)

                    if not idle:
                        busy_executors += 1

                        # Get current build info
                        current_build = executor.get('currentExecutable', {})
                        if current_build:
                            build_number = current_build.get('number', 'Unknown')
                            build_url = current_build.get('url', '')

                            # Extract job name from URL or display name
                            job_name = 'Unknown'
                            if build_url:
                                url_parts = build_url.strip('/').split('/')
                                if 'job' in url_parts:
                                    job_idx = url_parts.index('job')
                                    if job_idx + 1 < len(url_parts):
                                        job_name = url_parts[job_idx + 1]

                            # Try display name if URL parsing failed
                            if job_name == 'Unknown' and 'displayName' in current_build:
                                display_name = current_build.get('displayName', '')
                                if '#' in display_name:
                                    job_name = display_name.split('#')[0].strip()

                            # Get progress if available
                            progress = executor.get('progress', -1)
                            progress_str = f"{progress}%" if progress >= 0 else "Unknown"

                            executor_info.append({
                                'job_name': job_name,
                                'build_number': build_number,
                                'progress': progress_str
                            })
                    else:
                        executor_info.append({
                            'idle': True
                        })

                # Calculate utilization
                utilization = (busy_executors / total_executors * 100) if total_executors > 0 else 0

                # Find most common job if any
                running_jobs = [e['job_name'] for e in executor_info if 'idle' not in e]
                most_running_job = ""
                if running_jobs:
                    job_counts = {}
                    for job in running_jobs:
                        if job in job_counts:
                            job_counts[job] += 1
                        else:
                            job_counts[job] = 1

                    # Find job with highest count
                    most_running_job = max(job_counts.items(), key=lambda x: x[1])[0]

                # Add node executor usage
                executor_usage.append({
                    'node_name': node_name,
                    'total_executors': total_executors,
                    'busy_executors': busy_executors,
                    'idle_executors': total_executors - busy_executors,
                    'utilization': utilization,
                    'most_running_job': most_running_job,
                    'executor_info': executor_info
                })

            # Sort by utilization (descending)
            executor_usage.sort(key=lambda x: x['utilization'], reverse=True)

            # Get overall stats
            total_executors = sum(node['total_executors'] for node in executor_usage)
            busy_executors = sum(node['busy_executors'] for node in executor_usage)
            idle_executors = total_executors - busy_executors
            overall_utilization = (busy_executors / total_executors * 100) if total_executors > 0 else 0

            return {
                'executor_usage': executor_usage,
                'total_executors': total_executors,
                'busy_executors': busy_executors,
                'idle_executors': idle_executors,
                'overall_utilization': overall_utilization
            }

        except Exception as e:
            return {"error": f"Error retrieving executor usage: {str(e)}"}
