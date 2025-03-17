#!/usr/bin/env python3
"""
Jenkins Jobs Information Collector
This module collects information about Jenkins jobs.
"""

from datetime import datetime
from collectors.base_collector import BaseCollector

class JenkinsJobsCollector(BaseCollector):
    """Collects detailed information about Jenkins jobs"""

    def get_jobs_overview(self):
        """
        Fetches overview information about all jobs

        Returns:
            dict: Jobs overview information
        """
        try:
            # Get the list of all jobs with detailed information
            tree_param = "jobs[name,url,color,buildable,inQueue,firstBuild[number],lastBuild[number,timestamp,result,duration]]"
            response = self.fetch_jenkins_data("api/json", params={"tree": tree_param})

            if "error" in response:
                return response

            jobs = response.get('jobs', [])

            # Process the jobs information
            processed_jobs = []
            for job in jobs:
                if not isinstance(job, dict):
                    continue

                job_info = {
                    'name': job.get('name', 'Unknown'),
                    'url': job.get('url', ''),
                    'color': self._parse_job_color(job.get('color', '')),
                    'buildable': job.get('buildable', False),
                    'inQueue': job.get('inQueue', False),
                    'firstBuildNumber': 'N/A',
                }

                # Get first build info if available
                first_build = job.get('firstBuild')
                if isinstance(first_build, dict):
                    job_info['firstBuildNumber'] = first_build.get('number', 'N/A')

                # Get last build information if available
                last_build = job.get('lastBuild')
                if isinstance(last_build, dict):
                    job_info['lastBuildNumber'] = last_build.get('number', 'N/A')

                    # Format timestamp to human-readable date
                    timestamp = last_build.get('timestamp')
                    if timestamp:
                        job_info['lastBuildTime'] = self.format_timestamp(timestamp)
                    else:
                        job_info['lastBuildTime'] = 'N/A'

                    # Get build result
                    job_info['lastBuildResult'] = last_build.get('result', 'N/A')

                    # Format duration to human-readable time
                    duration = last_build.get('duration')
                    if duration:
                        job_info['lastBuildDuration'] = self.format_duration(duration)
                    else:
                        job_info['lastBuildDuration'] = 'N/A'
                else:
                    job_info['lastBuildNumber'] = 'N/A'
                    job_info['lastBuildTime'] = 'N/A'
                    job_info['lastBuildResult'] = 'N/A'
                    job_info['lastBuildDuration'] = 'N/A'

                # Add to processed jobs list
                processed_jobs.append(job_info)

            # Calculate statistics
            total_jobs = len(processed_jobs)
            status_counts = {'Success': 0, 'Failed': 0, 'Unstable': 0, 'Disabled': 0, 'In progress': 0, 'Not built': 0}

            for job in processed_jobs:
                status = job['color'].split()[0] if job['color'] else "Not built"  # Get the status part without the details
                if status == 'Success':
                    status_counts['Success'] += 1
                elif status == 'Failed':
                    status_counts['Failed'] += 1
                elif status == 'Unstable':
                    status_counts['Unstable'] += 1
                elif status == 'Disabled':
                    status_counts['Disabled'] += 1
                elif status == 'In' and 'progress' in job['color']:
                    status_counts['In progress'] += 1
                else:
                    status_counts['Not built'] += 1

            # Get success rate
            built_jobs = total_jobs - status_counts['Disabled'] - status_counts['Not built']
            success_rate = (status_counts['Success'] / built_jobs * 100) if built_jobs > 0 else 0

            return {
                'total_jobs': total_jobs,
                'status_counts': status_counts,
                'success_rate': success_rate,
                'jobs': processed_jobs
            }

        except Exception as e:
            return {"error": f"Error retrieving jobs overview: {str(e)}"}

    def get_job_types(self):
        """
        Fetches information about job types

        Returns:
            dict: Job types information
        """
        try:
            # To get job types, we need to make additional API calls to each job
            overview = self.get_jobs_overview()
            if "error" in overview:
                return overview

            jobs = overview.get('jobs', [])
            if not jobs:
                return {"error": "No jobs found or unable to retrieve jobs"}

            # Process a sample of jobs (limit to 50 for performance)
            job_types = {}
            sample_size = min(50, len(jobs))
            sample_jobs = jobs[:sample_size]

            for job in sample_jobs:
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

                    # Extract the simple class name (last part after the dot)
                    simple_class = job_class.split('.')[-1]

                    # Map to common name
                    job_type = self._map_job_class_to_type(simple_class)

                    # Count job types
                    if job_type in job_types:
                        job_types[job_type] += 1
                    else:
                        job_types[job_type] = 1
                except Exception:
                    # If we can't determine the type, skip this job
                    continue

            # Calculate percentages
            total = sum(job_types.values())
            job_types_with_percent = []

            for job_type, count in job_types.items():
                percentage = (count / total * 100) if total > 0 else 0
                job_types_with_percent.append({
                    'type': job_type,
                    'count': count,
                    'percentage': percentage
                })

            # Sort by count (descending)
            job_types_with_percent.sort(key=lambda x: x['count'], reverse=True)

            return {
                'total_analyzed': total,
                'job_types': job_types_with_percent
            }
        except Exception as e:
            return {"error": f"Error analyzing job types: {str(e)}"}

    def get_recent_builds(self, limit=20):
        """
        Fetches information about recent builds across all jobs

        Args:
            limit: Maximum number of recent builds to return

        Returns:
            dict: Recent builds information
        """
        try:
            # Get all jobs first
            overview = self.get_jobs_overview()
            if "error" in overview:
                return overview

            jobs = overview.get('jobs', [])
            if not jobs:
                return {"error": "No jobs found or unable to retrieve jobs"}

            # Collect the most recent build from each job
            recent_builds = []

            for job in jobs:
                if job.get('lastBuildNumber', 'N/A') != 'N/A':
                    # Only include jobs that have actual builds
                    build_info = {
                        'job_name': job.get('name', 'Unknown'),
                        'build_number': job.get('lastBuildNumber', 'N/A'),
                        'timestamp': job.get('lastBuildTime', 'N/A'),
                        'result': job.get('lastBuildResult', 'N/A'),
                        'duration': job.get('lastBuildDuration', 'N/A')
                    }
                    recent_builds.append(build_info)

            # Sort by timestamp (most recent first)
            def get_sort_key(build):
                timestamp = build.get('timestamp', 'N/A')
                if timestamp == 'N/A':
                    return ''  # This will sort to the end
                return timestamp

            recent_builds.sort(key=get_sort_key, reverse=True)

            # Limit the number of builds
            recent_builds = recent_builds[:limit]

            return {
                'total_builds': len(recent_builds),
                'builds': recent_builds
            }
        except Exception as e:
            return {"error": f"Error retrieving recent builds: {str(e)}"}

    def _parse_job_color(self, color):
        """
        Parse Jenkins job color and return human-readable status

        Args:
            color: Jenkins job color string

        Returns:
            str: Human-readable job status
        """
        if not color:
            return "Not built"

        # Remove _anime suffix (indicates job is in progress)
        in_progress = color.endswith('_anime')
        base_color = color.replace('_anime', '')

        # Map colors to statuses
        status_map = {
            'blue': "Success",
            'green': "Success",
            'yellow': "Unstable",
            'red': "Failed",
            'aborted': "Aborted",
            'disabled': "Disabled",
            'notbuilt': "Not built"
        }

        status = status_map.get(base_color, "Unknown")

        # Add in progress indicator if needed
        if in_progress:
            return f"{status} (in progress)"

        return status

    def format_timestamp(self, timestamp):
        """Format timestamp to readable date/time"""
        if timestamp is None:
            return "N/A"
        try:
            # Convert milliseconds to seconds
            seconds = timestamp / 1000
            from datetime import datetime
            dt = datetime.fromtimestamp(seconds)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return str(timestamp)

    def _map_job_class_to_type(self, class_name):
        """
        Map Jenkins job class to human-readable type

        Args:
            class_name: Jenkins job class name

        Returns:
            str: Human-readable job type
        """
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

        # Check for partial matches
        for key, value in type_map.items():
            if key in class_name:
                return value

        return class_name  # Return the original class name if no mapping found
