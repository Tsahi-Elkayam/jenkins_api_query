#!/usr/bin/env python3
"""
Jenkins Build Statistics Collector
This module collects information about Jenkins build durations and frequencies.
"""

from datetime import datetime, timedelta
from collectors.base_collector import BaseCollector

class JenkinsBuildStatsCollector(BaseCollector):
    """Collects statistics about Jenkins builds"""

    def get_build_durations(self, limit=10):
        """
        Fetches information about jobs with longest build durations

        Args:
            limit: Maximum number of jobs to return

        Returns:
            dict: Build duration information
        """
        try:
            # Get jobs with basic info
            response = self.fetch_jenkins_data("api/json", params={"tree": "jobs[name,url,lastBuild[number]]"})
            if "error" in response:
                return response

            jobs = response.get('jobs', [])

            # Process job build durations
            job_durations = []

            for job in jobs:
                job_name = job.get('name', 'Unknown')
                job_url = job.get('url', '')

                # Skip jobs with no builds
                if not job.get('lastBuild'):
                    continue

                try:
                    # Get build history
                    response = self.fetch_jenkins_data(f"{job_url}api/json",
                                                     params={"tree": "builds[number,duration,result,timestamp]{0,10}"})

                    if "error" in response:
                        continue

                    builds = response.get('builds', [])

                    if not builds:
                        continue

                    # Calculate build statistics
                    durations = [build.get('duration', 0) for build in builds if build.get('duration', 0) > 0]

                    if not durations:
                        continue

                    avg_duration = sum(durations) / len(durations)
                    min_duration = min(durations)
                    max_duration = max(durations)

                    # Get latest build duration
                    last_duration = builds[0].get('duration', 0) if builds else 0

                    # Calculate trend (positive means getting longer)
                    trend = 0
                    if len(durations) > 1:
                        # Use simple trend calculation - compare first half with second half
                        half = len(durations) // 2
                        first_half = durations[:half]
                        second_half = durations[half:]

                        if first_half and second_half:
                            first_avg = sum(first_half) / len(first_half)
                            second_avg = sum(second_half) / len(second_half)

                            trend = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0

                    job_durations.append({
                        'job_name': job_name,
                        'avg_duration': avg_duration,
                        'min_duration': min_duration,
                        'max_duration': max_duration,
                        'last_duration': last_duration,
                        'trend': trend,
                        'trend_direction': "up" if trend > 5 else "down" if trend < -5 else "stable"
                    })
                except Exception:
                    # Skip on error and continue with other jobs
                    continue

            # Sort by average duration (descending)
            job_durations.sort(key=lambda x: x['avg_duration'], reverse=True)

            # Limit to requested number
            job_durations = job_durations[:limit]

            return {
                'job_durations': job_durations,
                'total_jobs_analyzed': len(job_durations)
            }

        except Exception as e:
            return {"error": f"Error retrieving build durations: {str(e)}"}

    def get_build_frequencies(self, limit=10):
        """
        Fetches information about most frequently built jobs

        Args:
            limit: Maximum number of jobs to return

        Returns:
            dict: Build frequency information
        """
        try:
            # Get jobs with basic info
            response = self.fetch_jenkins_data("api/json", params={"tree": "jobs[name,url,lastBuild[number]]"})
            if "error" in response:
                return response

            jobs = response.get('jobs', [])

            # Get current time for period calculations
            now = datetime.now().timestamp() * 1000  # milliseconds
            today = now - (24 * 60 * 60 * 1000)  # 24 hours ago
            week_ago = now - (7 * 24 * 60 * 60 * 1000)  # 7 days ago
            month_ago = now - (30 * 24 * 60 * 60 * 1000)  # 30 days ago

            # Process job build frequencies
            job_frequencies = []

            for job in jobs:
                job_name = job.get('name', 'Unknown')
                job_url = job.get('url', '')

                # Skip jobs with no builds
                if not job.get('lastBuild'):
                    continue

                try:
                    # Get build history with timestamps
                    response = self.fetch_jenkins_data(f"{job_url}api/json",
                                                    params={"tree": "builds[number,timestamp]{0,100}"})

                    if "error" in response:
                        continue

                    builds = response.get('builds', [])

                    if not builds:
                        continue

                    # Count builds by period
                    total_builds = len(builds)
                    builds_today = sum(1 for build in builds if build.get('timestamp', 0) >= today)
                    builds_this_week = sum(1 for build in builds if build.get('timestamp', 0) >= week_ago)
                    builds_this_month = sum(1 for build in builds if build.get('timestamp', 0) >= month_ago)

                    # Calculate average builds per day
                    if builds_this_month > 0:
                        avg_builds_per_day = builds_this_month / 30
                    else:
                        # If no builds in the last month, use all-time average if available
                        first_build_time = builds[-1].get('timestamp', now) if builds else now
                        days_since_first_build = (now - first_build_time) / (24 * 60 * 60 * 1000)

                        if days_since_first_build > 0:
                            avg_builds_per_day = total_builds / days_since_first_build
                        else:
                            avg_builds_per_day = 0

                    job_frequencies.append({
                        'job_name': job_name,
                        'total_builds': total_builds,
                        'builds_today': builds_today,
                        'builds_this_week': builds_this_week,
                        'builds_this_month': builds_this_month,
                        'avg_builds_per_day': avg_builds_per_day
                    })
                except Exception:
                    # Skip on error and continue with other jobs
                    continue

            # Sort by builds today (descending)
            job_frequencies.sort(key=lambda x: x['builds_today'], reverse=True)

            # Limit to requested number
            job_frequencies = job_frequencies[:limit]

            return {
                'job_frequencies': job_frequencies,
                'total_jobs_analyzed': len(job_frequencies)
            }

        except Exception as e:
            return {"error": f"Error retrieving build frequencies: {str(e)}"}
