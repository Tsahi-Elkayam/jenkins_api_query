#!/usr/bin/env python3
"""
Jenkins Queue Information Collector
This module collects information about the Jenkins build queue.
"""

from datetime import datetime
from collectors.base_collector import BaseCollector

class JenkinsQueueCollector(BaseCollector):
    """Collects information about the Jenkins build queue"""

    def get_queue_summary(self):
        """
        Fetches summary information about the Jenkins build queue

        Returns:
            dict: Queue information summary
        """
        try:
            # Get the build queue
            response = self.fetch_jenkins_data("queue/api/json")
            if "error" in response:
                return response

            queue_items = response.get('items', [])

            # Count items in queue
            total_items = len(queue_items)

            # Group by blocking reason
            blocked_reasons = {}
            wait_times = []

            now = datetime.now().timestamp() * 1000  # Current time in milliseconds

            for item in queue_items:
                # Get wait time
                in_queue_since = item.get('inQueueSince', 0)
                wait_time_ms = now - in_queue_since
                wait_times.append(wait_time_ms)

                # Count blocking reasons
                why = item.get('why', '')
                if why:
                    if why in blocked_reasons:
                        blocked_reasons[why] += 1
                    else:
                        blocked_reasons[why] = 1

            # Calculate average wait time
            avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0
            # Convert to seconds
            avg_wait_time = avg_wait_time / 1000

            # Format the wait time into a readable string
            if avg_wait_time < 60:
                avg_wait = f"{avg_wait_time:.1f} seconds"
            elif avg_wait_time < 3600:
                avg_wait = f"{(avg_wait_time / 60):.1f} minutes"
            else:
                avg_wait = f"{(avg_wait_time / 3600):.1f} hours"

            # Get more detailed queue items information
            queue_items_info = []

            for item in queue_items[:10]:  # Limit to the first 10 for the summary
                task = item.get('task', {})
                job_name = task.get('name', 'Unknown') if isinstance(task, dict) else 'Unknown'

                queue_time = item.get('inQueueSince', 0)
                wait_time = now - queue_time

                # Format wait time
                if wait_time < 60000:  # Less than a minute
                    wait_time_str = f"{(wait_time / 1000):.1f} seconds"
                elif wait_time < 3600000:  # Less than an hour
                    wait_time_str = f"{(wait_time / 60000):.1f} minutes"
                else:  # Hours or more
                    wait_time_str = f"{(wait_time / 3600000):.1f} hours"

                # Get why it's blocked
                why_blocked = item.get('why', 'Not blocked')

                # Get cause information
                cause = "Unknown"
                actions = item.get('actions', [])
                for action in actions:
                    if isinstance(action, dict) and 'causes' in action:
                        causes = action.get('causes', [])
                        if causes and isinstance(causes[0], dict):
                            cause = causes[0].get('shortDescription', 'Unknown')

                # Add to queue items info
                queue_items_info.append({
                    'job_name': job_name,
                    'wait_time': wait_time_str,
                    'why_blocked': why_blocked,
                    'cause': cause
                })

            return {
                'items_in_queue': total_items,
                'avg_wait_time': avg_wait,
                'blocking_reasons': blocked_reasons,
                'queue_items': queue_items_info
            }

        except Exception as e:
            return {"error": f"Error retrieving queue summary: {str(e)}"}
