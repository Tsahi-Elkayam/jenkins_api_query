#!/usr/bin/env python3
"""
Jenkins Build Artifacts Collector
This module collects information about artifacts produced by Jenkins builds.
"""

from collectors.base_collector import BaseCollector

class JenkinsBuildArtifactsCollector(BaseCollector):
    """Collects information about Jenkins build artifacts"""

    def get_build_artifacts(self, limit=10):
        """
        Fetches information about artifacts produced by builds

        Args:
            limit: Maximum number of artifacts to return

        Returns:
            dict: Build artifacts information
        """
        try:
            # Get jobs with basic info
            response = self.fetch_jenkins_data("api/json", params={"tree": "jobs[name,url,lastBuild[number]]"})
            if "error" in response:
                return response

            jobs = response.get('jobs', [])

            # Process artifacts
            artifacts_info = []

            for job in jobs:
                job_name = job.get('name', 'Unknown')
                job_url = job.get('url', '')

                # Skip jobs with no builds
                if not job.get('lastBuild'):
                    continue

                try:
                    # Get last build with artifacts
                    response = self.fetch_jenkins_data(f"{job_url}lastBuild/api/json",
                                                   params={"tree": "number,artifacts[*],timestamp"})

                    if "error" in response:
                        continue

                    build_number = response.get('number', 'Unknown')
                    build_time = response.get('timestamp', 0)
                    artifacts = response.get('artifacts', [])

                    if not artifacts:
                        continue

                    # Process each artifact
                    for artifact in artifacts:
                        artifact_name = artifact.get('fileName', 'Unknown')
                        artifact_path = artifact.get('relativePath', '')

                        # Get artifact size if available
                        size = artifact.get('size', 0)
                        if not size:
                            # Try to get from displayPath if available
                            display_path = artifact.get('displayPath', '')
                            if display_path and 'Size:' in display_path:
                                size_str = display_path.split('Size:')[1].strip()
                                try:
                                    size = int(size_str)
                                except ValueError:
                                    size = 0

                        # Try to estimate download count (not always available)
                        download_count = 0

                        # Format age
                        age = self.format_timestamp(build_time)

                        artifacts_info.append({
                            'job_name': job_name,
                            'artifact_name': artifact_name,
                            'size': size,
                            'build_number': build_number,
                            'age': age,
                            'download_count': download_count
                        })
                except Exception:
                    # Skip on error and continue with other jobs
                    continue

            # Sort by size (descending)
            artifacts_info.sort(key=lambda x: x['size'], reverse=True)

            # Limit to requested number
            artifacts_info = artifacts_info[:limit]

            return {
                'artifacts': artifacts_info,
                'total_artifacts': len(artifacts_info)
            }

        except Exception as e:
            return {"error": f"Error retrieving build artifacts: {str(e)}"}
