#!/usr/bin/env python3
"""
Jenkins Failed Jobs Collector
This module collects information about failing Jenkins jobs.
"""

from datetime import datetime
from collectors.base_collector import BaseCollector

class JenkinsFailedJobsCollector(BaseCollector):
    """Collects information about failing Jenkins jobs"""

    def get_failed_jobs(self, limit=10):
        """
        Fetches information about failing jobs

        Args:
            limit: Maximum number of jobs to return

        Returns:
            dict: Failed jobs information
        """
        try:
            # Get jobs with basic info
            response = self.fetch_jenkins_data("api/json", params={"tree": "jobs[name,url,color,lastBuild[number,timestamp,result]]"})
            if "error" in response:
                return response

            jobs = response.get('jobs', [])

            # Filter for failed jobs
            failed_jobs = []

            for job in jobs:
                job_name = job.get('name', 'Unknown')
                job_url = job.get('url', '')
                color = job.get('color', '')

                # Check if job is failed or unstable
                if color not in ['red', 'red_anime', 'yellow', 'yellow_anime']:
                    continue

                # Skip jobs with no builds
                last_build = job.get('lastBuild', {})
                if not last_build:
                    continue

                try:
                    # Get build history
                    response = self.fetch_jenkins_data(f"{job_url}api/json",
                                                   params={"tree": "builds[number,result,timestamp,duration]{0,10}"})

                    if "error" in response:
                        continue

                    builds = response.get('builds', [])

                    if not builds:
                        continue

                    # Count successes and failures
                    total_builds = len(builds)
                    success_count = sum(1 for build in builds if build.get('result') == 'SUCCESS')
                    fail_count = sum(1 for build in builds if build.get('result') in ['FAILURE', 'UNSTABLE'])

                    # Calculate success rate
                    success_rate = (success_count / total_builds * 100) if total_builds > 0 else 0

                    # Find last failure and last success
                    last_failed = None
                    last_success = None

                    for build in builds:
                        if build.get('result') in ['FAILURE', 'UNSTABLE'] and not last_failed:
                            last_failed = build

                        if build.get('result') == 'SUCCESS' and not last_success:
                            last_success = build

                        if last_failed and last_success:
                            break

                    # Format timestamps
                    last_failed_time = "Never"
                    if last_failed and 'timestamp' in last_failed:
                        last_failed_time = self.format_timestamp(last_failed.get('timestamp', 0))

                    last_success_time = "Never"
                    if last_success and 'timestamp' in last_success:
                        last_success_time = self.format_timestamp(last_success.get('timestamp', 0))

                    # Try to get common failure reason
                    common_failure_reason = self._get_common_failure_reason(job_url, builds)

                    failed_jobs.append({
                        'job_name': job_name,
                        'last_failed': last_failed_time,
                        'fail_count': fail_count,
                        'success_rate': success_rate,
                        'last_success': last_success_time,
                        'common_failure_reason': common_failure_reason
                    })
                except Exception:
                    # Skip on error and continue with other jobs
                    continue

            # Sort by last failed time (most recent first)
            failed_jobs.sort(key=lambda x: x['last_failed'], reverse=True)

            # Limit to requested number
            failed_jobs = failed_jobs[:limit]

            return {
                'failed_jobs': failed_jobs,
                'total_failed_jobs': len(failed_jobs)
            }

        except Exception as e:
            return {"error": f"Error retrieving failed jobs: {str(e)}"}

    def _get_common_failure_reason(self, job_url, builds):
        """
        Try to determine common failure reason from build logs

        Args:
            job_url: URL of the job
            builds: List of build data

        Returns:
            str: Common failure reason or "Unknown"
        """
        try:
            # Find the most recent failed build
            failed_build = next((build for build in builds if build.get('result') in ['FAILURE', 'UNSTABLE']), None)

            if not failed_build:
                return "Unknown"

            build_number = failed_build.get('number')

            # Get build log (truncated)
            response = self.fetch_jenkins_data(f"{job_url}{build_number}/consoleText")
            if "error" in response or "html" not in response:
                return "Unknown"

            log = response["content"]

            # Look for common error patterns
            error_patterns = [
                "BUILD FAILURE",
                "Compilation failure",
                "Test failures",
                "Error:",
                "Exception:",
                "NullPointerException",
                "OutOfMemoryError",
                "Connection refused",
                "java.io.IOException",
                "Timeout"
            ]

            # Check for error patterns
            for pattern in error_patterns:
                if pattern in log:
                    # Get the line containing the error
                    lines = log.split('\n')
                    for line in lines:
                        if pattern in line:
                            # Truncate to reasonable length
                            if len(line) > 100:
                                return line[:97] + "..."
                            return line

            return "Unknown"

        except Exception:
            return "Unknown"
