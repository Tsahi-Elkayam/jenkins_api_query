#!/usr/bin/env python3
"""
Jenkins System Information Collector
This module collects detailed Jenkins system information.
"""

import re
from datetime import datetime, timedelta
from collectors.base_collector import BaseCollector

class JenkinsInfoCollector(BaseCollector):
    """Collects detailed Jenkins system information"""

    def get_jenkins_info(self):
        """
        Fetches detailed Jenkins system information

        Returns:
            dict: Jenkins system information
        """
        info = {}

        try:
            # Get basic Jenkins info
            response = self.fetch_jenkins_data("api/json")
            if "error" not in response:
                info['nodeName'] = response.get('nodeName', 'Unknown')
                info['nodeDescription'] = response.get('nodeDescription', '')
                info['primaryView'] = response.get('primaryView', {}).get('name', 'Unknown')
                info['slaveAgentPort'] = response.get('slaveAgentPort', 'Unknown')
                info['useSecurity'] = response.get('useSecurity', False)
                info['views'] = len(response.get('views', []))

            # Get system info from About page (this contains more detailed information)
            response = self.fetch_jenkins_data("systemInfo")
            if "error" not in response and "html" in response:
                html_content = response["content"]

                # Extract Jenkins version (in header if available)
                info['version'] = self.session.get(f"{self.url}").headers.get('X-Jenkins', 'Unknown')

                # Look for JVM-specific information in the HTML content
                system_properties = {
                    'javaRuntimeName': 'java.runtime.name',
                    'javaVersion': 'java.runtime.version',
                    'javaHome': 'java.home',
                    'javaVendor': 'java.vendor',
                    'javaVmName': 'java.vm.name',
                    'timezone': 'user.timezone',
                    'osName': 'os.name',
                    'osVersion': 'os.version',
                    'osArch': 'os.arch'
                }

                # Extract each property from the HTML
                for key, prop in system_properties.items():
                    if prop in html_content:
                        info[key] = self.extract_property(html_content, prop)

            # Get more system information directly
            try:
                # Directly access system information endpoint for more details
                response = self.fetch_jenkins_data("systemInfo")
                if "error" not in response and "html" in response:
                    html = response["content"]

                    # Extract Jenkins-specific directories and configurations
                    jenkins_specific = {
                        'jenkinsHome': 'JENKINS_HOME',
                        'jenkinsWarFile': 'executable-war',
                        'tempDir': 'java.io.tmpdir',
                        'logLevel': 'hudson.logging.LogRecorderManager.level',
                        'servletContainer': 'jenkins.servlet.name',
                        'servletContainerVersion': 'jenkins.servlet.version',
                        'agentProtocols': 'jenkins.AgentProtocol.enabled',
                        'systemConfigFile': 'Config File',
                        'updateCenterSite': 'hudson.model.UpdateCenter.updateCenterUrl'
                    }

                    for key, prop in jenkins_specific.items():
                        if prop in html:
                            info[key] = self.extract_property(html, prop)

                    # Additional manual extraction for important values that may have
                    # different HTML structure
                    if 'JENKINS_HOME' in html:
                        # Try an alternative approach if the standard one failed
                        if info.get('jenkinsHome') == 'Unknown':
                            pattern = "JENKINS_HOME:</td><td[^>]*>(.*?)</td>"
                            match = re.search(pattern, html, re.DOTALL)
                            if match:
                                info['jenkinsHome'] = match.group(1).strip()
            except Exception as e:
                # Don't fail completely on extraction error
                pass

            # Get uptime information
            try:
                response = self.fetch_jenkins_data(f"metrics/{self.client.session.auth[0]}/api/json")
                if "error" not in response:
                    uptime_ms = response.get('gauges', {}).get('vm.uptime.milliseconds', {}).get('value')
                    if uptime_ms:
                        # Convert to readable format
                        uptime_seconds = uptime_ms / 1000
                        uptime_duration = timedelta(seconds=uptime_seconds)
                        days = uptime_duration.days
                        hours, remainder = divmod(uptime_duration.seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        info['uptime'] = f"{days}d {hours}h {minutes}m {seconds}s"

                        # Calculate startup time
                        now = datetime.now()
                        startup_time = now - uptime_duration
                        info['startupTime'] = startup_time.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                # Fallback if metrics endpoint is not available
                info['uptime'] = "Unknown"
                info['startupTime'] = "Unknown"

            # Get security info
            try:
                response = self.fetch_jenkins_data("configureSecurity/api/json")
                if "error" not in response:
                    info['authorizationStrategy'] = self._get_class_name(response.get('authorizationStrategy', {}))
                    info['securityRealm'] = self._get_class_name(response.get('securityRealm', {}))
                    info['crumbIssuer'] = "Enabled" if response.get('useCrumbs', False) else "Disabled"
            except Exception:
                # Don't fail completely on security info error
                pass

            # Get running mode (standalone/clustered)
            try:
                response = self.fetch_jenkins_data("pluginManager/installed/api/json")
                if "error" not in response:
                    plugins = response.get('plugins', [])
                    plugin_names = [p.get('shortName') for p in plugins]

                    if any(p in plugin_names for p in ['cluster', 'ha-clustered', 'kubernetes']):
                        info['runningMode'] = "Clustered"
                    else:
                        info['runningMode'] = "Standalone"
            except Exception:
                info['runningMode'] = "Unknown"

            return info

        except Exception as e:
            return {"error": f"Error retrieving system info: {str(e)}"}

    def _get_class_name(self, obj):
        """Get the class name of an object if available"""
        if isinstance(obj, dict) and 'class' in obj:
            class_name = obj['class']
            # Get the simple name from the full class path
            if '.' in class_name:
                return class_name.split('.')[-1]
            return class_name
        return "Unknown"
