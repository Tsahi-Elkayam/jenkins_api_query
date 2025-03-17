#!/usr/bin/env python3
"""
Jenkins Plugins Information Collector
This module collects information about Jenkins plugins.
"""

from collectors.base_collector import BaseCollector

class JenkinsPluginsCollector(BaseCollector):
    """Collects information about Jenkins plugins"""

    def get_plugins_summary(self):
        """
        Fetches summary information about Jenkins plugins

        Returns:
            dict: Plugins information summary
        """
        try:
            # Get list of plugins with deeper information
            response = self.fetch_jenkins_data("pluginManager/api/json", depth=2)
            if "error" in response:
                return response

            plugins = response.get('plugins', [])

            # Count plugins
            total_plugins = len(plugins)
            active_plugins = 0
            has_updates = 0

            # Group by category
            categories = {}

            # Track plugins with updates
            updates_available = []

            # Get update center data which contains the latest versions
            update_center_response = self.fetch_jenkins_data("updateCenter/api/json", depth=2)
            latest_versions = {}

            if "error" not in update_center_response:
                # Extract latest versions from update sites
                for site in update_center_response.get('sites', []):
                    for plugin_name, plugin_info in site.get('plugins', {}).items():
                        latest_versions[plugin_name] = plugin_info.get('version', 'Unknown')

            # Process each plugin
            for plugin in plugins:
                # Check if active
                if plugin.get('active', False):
                    active_plugins += 1

                # Check if has update
                if plugin.get('hasUpdate', False):
                    has_updates += 1

                    # Get the plugin short name for lookup
                    plugin_name = plugin.get('shortName', '')
                    current_version = plugin.get('version', 'Unknown')

                    # Try different approaches to find the new version
                    new_version = 'Unknown'

                    # Method 1: Check updateInfo
                    update_info = plugin.get('updateInfo', {})
                    if isinstance(update_info, dict) and 'version' in update_info:
                        new_version = update_info.get('version')

                    # Method 2: Check in the update center data
                    if new_version == 'Unknown' and plugin_name in latest_versions:
                        new_version = latest_versions[plugin_name]

                    # Method 3: If available updates were detected but we don't have a version,
                    # use a placeholder that's more informative than "Unknown"
                    if new_version == 'Unknown':
                        new_version = f"Newer than {current_version}"

                    # Add to updates list
                    updates_available.append({
                        'name': plugin.get('longName', plugin.get('shortName', 'Unknown')),
                        'current_version': current_version,
                        'new_version': new_version
                    })

                # Count by category
                categories_list = plugin.get('categories', [])
                if categories_list:
                    # Use the first category
                    cat_name = categories_list[0] if isinstance(categories_list[0], str) else categories_list[0].get('name', 'Other')

                    if cat_name in categories:
                        categories[cat_name] += 1
                    else:
                        categories[cat_name] = 1
                else:
                    # If no category, count as Other
                    if 'Other' in categories:
                        categories['Other'] += 1
                    else:
                        categories['Other'] = 1

            # Get the most recently installed plugins
            recent_plugins = []

            # Sort plugins by release date if available
            plugins_with_dates = []
            for plugin in plugins:
                if isinstance(plugin.get('releaseTimestamp'), (int, float)):
                    plugins_with_dates.append(plugin)

            # Sort by release timestamp (descending)
            if plugins_with_dates:
                plugins_with_dates.sort(key=lambda x: x.get('releaseTimestamp', 0), reverse=True)

                # Take the 5 most recent
                for plugin in plugins_with_dates[:5]:
                    recent_plugins.append({
                        'name': plugin.get('longName', plugin.get('shortName', 'Unknown')),
                        'version': plugin.get('version', 'Unknown')
                    })

            # Return plugins summary
            return {
                'total_plugins': total_plugins,
                'active_plugins': active_plugins,
                'updates_available': has_updates,
                'update_list': updates_available,
                'categories': categories,
                'recent_plugins': recent_plugins
            }

        except Exception as e:
            return {"error": f"Error retrieving plugins summary: {str(e)}"}
