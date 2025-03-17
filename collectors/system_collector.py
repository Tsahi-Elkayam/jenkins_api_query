#!/usr/bin/env python3
"""
Jenkins System Information Collector
This module collects Jenkins system information.
"""

import re
from datetime import datetime, timedelta
from collectors.base_collector import BaseCollector

class JenkinsSystemCollector(BaseCollector):
    """Collects Jenkins system information"""

    def get_system_info(self):
        """
        Fetches basic system information about the Jenkins instance

        Returns:
            dict: System information
        """
        try:
            # Get basic Jenkins info
            response = self.fetch_jenkins_data("api/json")
            if "error" in response:
                return response

            basic_info = response

            # Get version from headers
            version = self.session.get(f"{self.url}").headers.get('X-Jenkins', 'Unknown')

            # Prepare system info dictionary
            system_info = {
                'version': version,
                'nodeName': basic_info.get('nodeName', 'Unknown'),
                'nodeDescription': basic_info.get('nodeDescription', ''),
                'mode': basic_info.get('mode', 'Unknown'),
                'useSecurity': basic_info.get('useSecurity', False),
                'views': len(basic_info.get('views', [])),
                'primaryView': basic_info.get('primaryView', {}).get('name', 'Unknown'),
            }

            # Get more system details from the system info page
            response = self.fetch_jenkins_data("systemInfo")
            if "error" not in response and "html" in response:
                html = response["content"]

                # Extract key properties using regex
                properties = {
                    'javaVersion': 'java.runtime.version',
                    'osName': 'os.name',
                    'osVersion': 'os.version',
                    'osArch': 'os.arch',
                    'jenkinsHome': 'JENKINS_HOME',
                    'timezone': 'user.timezone',
                }

                for key, prop in properties.items():
                    system_info[key] = self.extract_property(html, prop)

                # Try to get uptime
                system_info['uptime'] = self._extract_uptime()

            return system_info

        except Exception as e:
            return {"error": f"Error retrieving system info: {str(e)}"}

    def _extract_uptime(self):
        """
        Try to extract Jenkins uptime

        Returns:
            str: Uptime string or 'Unknown'
        """
        try:
            # Try first from metrics API
            response = self.fetch_jenkins_data(f"metrics/{self.client.session.auth[0]}/api/json")
            if "error" not in response:
                uptime_ms = response.get('gauges', {}).get('vm.uptime.milliseconds', {}).get('value')
                if uptime_ms:
                    # Convert to readable format
                    uptime_seconds = uptime_ms / 1000
                    days, remainder = divmod(uptime_seconds, 86400)
                    hours, remainder = divmod(remainder, 3600)
                    minutes, seconds = divmod(remainder, 60)

                    if days > 0:
                        return f"{int(days)}d {int(hours)}h {int(minutes)}m"
                    elif hours > 0:
                        return f"{int(hours)}h {int(minutes)}m"
                    else:
                        return f"{int(minutes)}m {int(seconds)}s"

            # Alternative: try to extract from about page
            response = self.fetch_jenkins_data("about")
            if "error" not in response and "html" in response:
                html = response["content"]
                if "Running for" in html:
                    uptime_pattern = r"Running for:\s*([^<]+)"
                    match = re.search(uptime_pattern, html)
                    if match:
                        return match.group(1).strip()

            return "Unknown"
        except Exception:
            return "Unknown"
