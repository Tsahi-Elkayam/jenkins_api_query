#!/usr/bin/env python3
"""
Jenkins Security Configuration Collector
This module collects information about Jenkins security configuration.
"""

from collectors.base_collector import BaseCollector
import re
import requests

class JenkinsSecurityCollector(BaseCollector):
    """Collects information about Jenkins security configuration"""

    def get_security_config(self):
        """
        Fetches information about Jenkins security configuration

        Returns:
            dict: Security configuration information
        """
        try:
            # Skip the API approach and go directly to HTML parsing
            print("Using HTML parsing for security configuration...")

            # Initialize security configuration
            security_config = {}

            # Try to get security configuration page
            try:
                response = self.session.get(f"{self.url}manage/configureSecurity/")
                if response.status_code == 200:
                    html_content = response.text
                    print("Successfully accessed security config page via HTML")
                else:
                    return {"error": f"Could not access security configuration page: HTTP {response.status_code}"}
            except requests.RequestException as e:
                return {"error": f"Error accessing security configuration page: {str(e)}"}

            # Parse HTML to extract security information

            # Check for LDAP
            if 'LDAP' in html_content:
                security_config['security_realm'] = 'LDAPSecurityRealm'

                # Try to extract LDAP server
                server_match = re.search(r'name="_.?server"[^>]*value="([^"]+)"', html_content)
                if server_match:
                    if 'realm_details' not in security_config:
                        security_config['realm_details'] = {}
                    security_config['realm_details']['server'] = server_match.group(1)
            else:
                security_config['security_realm'] = 'Unknown'

            # Check for authorization strategy
            if 'Matrix Authorization' in html_content:
                security_config['authorization_strategy'] = 'GlobalMatrixAuthorizationStrategy'
            elif 'Project-based Matrix' in html_content:
                security_config['authorization_strategy'] = 'ProjectMatrixAuthorizationStrategy'
            elif 'Role-Based Strategy' in html_content:
                security_config['authorization_strategy'] = 'RoleBasedAuthorizationStrategy'
            elif 'Logged-in users can do anything' in html_content:
                security_config['authorization_strategy'] = 'FullControlOnceLoggedInAuthorizationStrategy'
            else:
                security_config['authorization_strategy'] = 'Unknown'

            # Check for CSRF protection
            security_config['csrf_protection'] = 'CSRF Protection' in html_content

            # Check for security headers
            try:
                headers = self.session.get(f"{self.url}").headers
                security_config['headers'] = {
                    'content_security_policy': 'Content-Security-Policy' in headers,
                    'x_content_type_options': 'X-Content-Type-Options' in headers,
                    'x_frame_options': 'X-Frame-Options' in headers
                }
            except Exception as e:
                security_config['headers'] = {"error": str(e)}

            # Recommended security options
            security_recommendations = [
                {'name': 'CSRF Protection', 'value': security_config.get('csrf_protection', False), 'recommended': True},
                {'name': 'Content Security Policy', 'value': security_config.get('headers', {}).get('content_security_policy', False), 'recommended': True},
                {'name': 'X-Content-Type-Options', 'value': security_config.get('headers', {}).get('x_content_type_options', False), 'recommended': True},
                {'name': 'X-Frame-Options', 'value': security_config.get('headers', {}).get('x_frame_options', False), 'recommended': True}
            ]

            # Add recommendations status
            for rec in security_recommendations:
                if rec['value'] == rec['recommended']:
                    rec['status'] = 'Good'
                else:
                    rec['status'] = 'Warning'

            security_config['recommendations'] = security_recommendations

            return security_config

        except Exception as e:
            return {"error": f"Error retrieving security configuration: {str(e)}"}

    def _get_class_name(self, obj):
        """Get class name from object"""
        if isinstance(obj, dict) and 'class' in obj:
            class_name = obj['class']
            # Get simple name
            if '.' in class_name:
                return class_name.split('.')[-1]
            return class_name
        return "Unknown"

    def _extract_properties(self, obj):
        """Extract useful properties from object"""
        properties = {}
        if not isinstance(obj, dict):
            return properties

        # Skip internal properties
        skip_properties = ['class', '_class', 'stapler-class', '$class']

        for key, value in obj.items():
            if key not in skip_properties:
                properties[key] = value

        return properties

    def _check_agent_security(self):
        """Check agent -> master security settings"""
        # This will not be used in HTML approach
        return "Unknown"

    def _check_api_token_settings(self):
        """Check API token settings"""
        # This will not be used in HTML approach
        return "Unknown"
