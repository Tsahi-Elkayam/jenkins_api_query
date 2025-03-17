#!/usr/bin/env python3
"""
Jenkins Node Labels Collector
This module collects detailed information about Jenkins node labels.
"""

from collectors.base_collector import BaseCollector

class JenkinsLabelsCollector(BaseCollector):
    """Collects information about Jenkins node labels"""

    def get_labels_details(self):
        """
        Fetches detailed information about labels

        Returns:
            dict: Labels information
        """
        try:
            # Get nodes information with labels
            response = self.fetch_jenkins_data("computer/api/json", depth=2)
            if "error" in response:
                return response

            nodes = response.get('computer', [])

            # Initialize label tracking
            labels_data = {}
            nodes_by_label = {}
            labeled_nodes = {}

            # Process each node
            for node in nodes:
                node_name = node.get('displayName', 'Unknown')
                node_online = not node.get('offline', True)
                node_executors = node.get('numExecutors', 0)

                # Get assigned labels for this node
                assigned_labels = []

                # First try assignedLabels which is more reliable
                if 'assignedLabels' in node:
                    label_objects = node.get('assignedLabels', [])
                    for label in label_objects:
                        if isinstance(label, dict) and 'name' in label:
                            label_name = label.get('name')
                            if label_name and label_name.strip():
                                assigned_labels.append(label_name.strip())

                # Also try labelString as a backup
                elif 'labelString' in node:
                    label_string = node.get('labelString', '')
                    if label_string:
                        assigned_labels = [label.strip() for label in label_string.split() if label.strip()]

                # Store node's labels
                if assigned_labels:
                    labeled_nodes[node_name] = assigned_labels

                # Count labels and associate with nodes
                for label in assigned_labels:
                    # Initialize label data if needed
                    if label not in labels_data:
                        labels_data[label] = {
                            'count': 0,
                            'online_nodes': 0,
                            'offline_nodes': 0,
                            'total_executors': 0,
                            'online_executors': 0
                        }

                    # Add to label counts
                    labels_data[label]['count'] += 1
                    if node_online:
                        labels_data[label]['online_nodes'] += 1
                        labels_data[label]['online_executors'] += node_executors
                    else:
                        labels_data[label]['offline_nodes'] += 1

                    labels_data[label]['total_executors'] += node_executors

                    # Add to nodes by label
                    if label not in nodes_by_label:
                        nodes_by_label[label] = []

                    nodes_by_label[label].append({
                        'name': node_name,
                        'online': node_online,
                        'executors': node_executors
                    })

            # Convert to a list format and sort for display
            labels_list = []
            for label, data in labels_data.items():
                labels_list.append({
                    'name': label,
                    'node_count': data['count'],
                    'online_nodes': data['online_nodes'],
                    'offline_nodes': data['offline_nodes'],
                    'total_executors': data['total_executors'],
                    'online_executors': data['online_executors'],
                    'utilization': (data['online_executors'] / data['total_executors'] * 100)
                                 if data['total_executors'] > 0 else 0
                })

            # Sort by node count (descending)
            labels_list.sort(key=lambda x: x['node_count'], reverse=True)

            # Find nodes without labels
            unlabeled_nodes = []
            for node in nodes:
                node_name = node.get('displayName', 'Unknown')
                if node_name not in labeled_nodes:
                    unlabeled_nodes.append(node_name)

            return {
                'labels': labels_list,
                'nodes_by_label': nodes_by_label,
                'labeled_nodes': labeled_nodes,
                'unlabeled_nodes': unlabeled_nodes,
                'total_labels': len(labels_list)
            }

        except Exception as e:
            return {"error": f"Error retrieving labels information: {str(e)}"}

    def get_label_usage(self):
        """
        Fetches information about label usage in jobs

        Returns:
            dict: Label usage information
        """
        try:
            # Get labels first
            labels_info = self.get_labels_details()
            if "error" in labels_info:
                return labels_info

            label_names = [label['name'] for label in labels_info.get('labels', [])]

            # Get jobs information
            response = self.fetch_jenkins_data("api/json", params={"tree": "jobs[name,url]"})
            if "error" in response:
                return {"error": "Failed to fetch jobs information"}

            jobs = response.get('jobs', [])

            # Track label usage in jobs
            label_usage = {}
            for label in label_names:
                label_usage[label] = {
                    'jobs': [],
                    'count': 0
                }

            # Check first 50 jobs for performance
            for job in jobs[:50]:
                job_name = job.get('name', 'Unknown')
                job_url = job.get('url', '')

                if not job_url:
                    continue

                # Check job config for label references
                try:
                    response = self.fetch_jenkins_data(f"{job_url}config.xml")
                    if "error" not in response and "html" in response:
                        config = response["content"]

                        # Check each label
                        for label in label_names:
                            # Look for label in assignedNode or label elements
                            label_pattern = f"<assignedNode>{label}</assignedNode>|<label>{label}</label>"
                            if re.search(label_pattern, config) or f"'{label}'" in config or f"\"{label}\"" in config:
                                label_usage[label]['jobs'].append(job_name)
                                label_usage[label]['count'] += 1
                except Exception:
                    # Skip on error and continue with other jobs
                    continue

            # Add usage info to labels
            labels_with_usage = []
            for label in labels_info.get('labels', []):
                label_name = label['name']
                label['jobs_count'] = label_usage.get(label_name, {}).get('count', 0)
                label['jobs'] = label_usage.get(label_name, {}).get('jobs', [])
                labels_with_usage.append(label)

            return {
                'labels': labels_with_usage,
                'nodes_by_label': labels_info.get('nodes_by_label', {}),
                'labeled_nodes': labels_info.get('labeled_nodes', {}),
                'unlabeled_nodes': labels_info.get('unlabeled_nodes', []),
                'total_labels': labels_info.get('total_labels', 0)
            }

        except Exception as e:
            return {"error": f"Error retrieving label usage: {str(e)}"}
