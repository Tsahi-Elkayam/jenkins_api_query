#!/usr/bin/env python3
"""
Jenkins Jobs Summary Collector
This module collects summarized information about Jenkins jobs.
"""

from datetime import datetime
from collectors.base_collector import BaseCollector

class JenkinsJobsStatCollector(BaseCollector):
    """Collects summarized information about Jenkins jobs"""

    def get_jobs_summary(self):
        """
        Fetches summary information about Jenkins jobs without detailed info per job

        Returns:
            dict: Jobs summary information
        """
        try:
            # Get the list of all jobs with minimal information
            response = self.fetch_jenkins_data(
                "api/json",
                params={"tree": "jobs[name,color,buildable,inQueue]"}
            )

            if "error" in response:
                return response

            jobs = response.get('jobs', [])

            # Initialize counters
            total_jobs = len(jobs)
            job_status = {
                'successful': 0,
                'failed': 0,
                'unstable': 0,
                'disabled': 0,
                'building': 0,
                'not_built': 0
            }

            # Count jobs by status
            for job in jobs:
                color = job.get('color', '')

                # Check job status
                if not color:
                    job_status['not_built'] += 1
                elif color == 'disabled':
                    job_status['disabled'] += 1
                elif color == 'red' or color == 'red_anime':
                    job_status['failed'] += 1
                elif color == 'yellow' or color == 'yellow_anime':
                    job_status['unstable'] += 1
                elif color == 'blue' or color == 'blue_anime' or color == 'green' or color == 'green_anime':
                    job_status['successful'] += 1
                else:
                    # Any _anime suffix indicates building
                    if '_anime' in color:
                        job_status['building'] += 1
                    else:
                        job_status['not_built'] += 1

            # Get recent builds activity
            response = self.fetch_jenkins_data(
                "api/json",
                params={"tree": "builds[timestamp,result]{0,50}"}
            )

            # Initialize recent activity counters
            builds_last_24h = 0
            recent_build_results = {'SUCCESS': 0, 'FAILURE': 0, 'UNSTABLE': 0, 'ABORTED': 0}

            if "error" not in response and 'builds' in response:
                builds = response.get('builds', [])

                # Get current time in milliseconds
                now = datetime.now().timestamp() * 1000
                day_ago = now - (24 * 60 * 60 * 1000)  # 24 hours ago

                # Count builds in last 24 hours and by result
                for build in builds:
                    # Count by result
                    result = build.get('result')
                    if result in recent_build_results:
                        recent_build_results[result] += 1

                    # Check if in last 24 hours
                    timestamp = build.get('timestamp', 0)
                    if timestamp > day_ago:
                        builds_last_24h += 1

            # Calculate success rate
            built_jobs = total_jobs - job_status['disabled'] - job_status['not_built']
            success_rate = (job_status['successful'] / built_jobs * 100) if built_jobs > 0 else 0

            # Try to get job types information with minimal API calls
            job_types = self._get_job_types_sample(jobs[:min(20, len(jobs))])

            # Create summary object
            return {
                'total': total_jobs,
                'status': job_status,
                'success_rate': success_rate,
                'builds_last_24h': builds_last_24h,
                'recent_build_results': recent_build_results,
                'job_types': job_types
            }

        except Exception as e:
            return {"error": f"Error retrieving jobs summary: {str(e)}"}

    def _get_job_types_sample(self, jobs_sample):
        """Get job types from a small sample of jobs"""
        job_types = {}

        for job in jobs_sample:
            try:
                job_url = job.get('url')
                if not job_url:
                    continue

                response = self.fetch_jenkins_data(f"{job_url}api/json", params={"tree": "_class"})
                if "error" in response:
                    continue

                job_class = response.get('_class', 'Unknown')
                if not job_class:
                    continue

                # Extract the class name
                simple_class = job_class.split('.')[-1]

                # Map to common type
                job_type = self._map_job_class_to_type(simple_class)

                # Count job types
                if job_type in job_types:
                    job_types[job_type] += 1
                else:
                    job_types[job_type] = 1
            except Exception:
                continue

        return job_types

    def _map_job_class_to_type(self, class_name):
        """Map class name to human-readable job type"""
        type_map = {
            'FreeStyleProject': 'Freestyle',
            'WorkflowJob': 'Pipeline',
            'WorkflowMultiBranchProject': 'Multi-branch Pipeline',
            'ExternalJob': 'External',
            'MatrixProject': 'Matrix',
            'MavenModuleSet': 'Maven',
            'IvyModuleSet': 'Ivy',
            'MultiJobProject': 'Multi-job',
            'OrganizationFolder': 'Organization Folder'
        }

        for key, value in type_map.items():
            if key in class_name:
                return value

        return class_name
