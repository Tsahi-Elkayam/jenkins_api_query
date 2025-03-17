#!/usr/bin/env python3
"""
Jenkins Users and Permissions Collector
This module collects information about Jenkins users, permissions, and LDAP configuration.
"""

from collectors.base_collector import BaseCollector
import re
import json

class JenkinsUsersCollector(BaseCollector):
    """Collects information about Jenkins users and permissions"""

    def get_users_info(self):
        """
        Fetches information about Jenkins users and permissions

        Returns:
            dict: Users and permissions information
        """
        try:
            # Initialize response dictionary
            users_info = {
                'users': [],
                'ldap': {
                    'configured': False,
                    'settings': {}
                },
                'permissions': {
                    'strategy': 'Unknown',
                    'matrix': {}
                }
            }

            # Try to get users
            users_info['users'] = self._get_users()

            # Try multiple approaches to get LDAP configuration
            ldap_config = self._get_ldap_config()
            if ldap_config:
                users_info['ldap'] = ldap_config

            # Try multiple approaches to get permissions configuration
            perm_config = self._get_permissions_config()
            if perm_config:
                users_info['permissions'] = perm_config

            return users_info
        except Exception as e:
            return {"error": f"Error retrieving users information: {str(e)}"}

    def _get_users(self):
        """Get list of Jenkins users"""
        # Try multiple possible paths
        possible_paths = [
            "asynchPeople/api/json",
            "manage/asynchPeople/api/json",
            "securityRealm/user/api/json",
            "manage/securityRealm/user/api/json",
            "people/api/json"
        ]

        for path in possible_paths:
            response = self.fetch_jenkins_data(path)

            if "error" not in response:
                if "users" in response:
                    users = []
                    for user in response.get("users", []):
                        if "user" in user:
                            user_data = user.get("user", {})
                            users.append({
                                "name": user_data.get("fullName", "Unknown"),
                                "id": user_data.get("id", "Unknown")
                            })
                    return users
                elif "people" in response:
                    users = []
                    for person in response.get("people", []):
                        users.append({
                            "name": person.get("user", {}).get("fullName", "Unknown"),
                            "id": person.get("user", {}).get("id", "Unknown")
                        })
                    return users

        # If all API attempts fail, try to extract from HTML
        try:
            response = self.session.get(f"{self.url}manage/securityRealm/")
            if response.status_code == 200:
                html = response.text
                # Very basic regex to find users
                user_matches = re.findall(r'user-([^"]+)"[^>]*>([^<]+)<', html)
                if user_matches:
                    return [{"id": user_id, "name": user_name} for user_id, user_name in user_matches]
        except Exception:
            pass

        return []

    def _get_ldap_config(self):
        """Get LDAP configuration"""
        ldap_config = {
            'configured': False,
            'settings': {}
        }

        # First check security realm type
        try:
            # Try multiple paths
            for path in ['securityRealm/api/json', 'manage/securityRealm/api/json']:
                response = self.fetch_jenkins_data(path)
                if "error" not in response and "_class" in response:
                    if "LDAPSecurityRealm" in response.get("_class", ""):
                        ldap_config['configured'] = True
                        break
        except Exception:
            pass

        if not ldap_config['configured']:
            # If not found through API, try to check security configuration page
            try:
                response = self.session.get(f"{self.url}manage/configureSecurity/")
                if response.status_code == 200 and "LDAP" in response.text:
                    ldap_config['configured'] = True
            except Exception:
                pass

        # If LDAP is configured, try to get details
        if ldap_config['configured']:
            # Try to get LDAP settings from configureSecurity page
            try:
                response = self.session.get(f"{self.url}manage/configureSecurity/")
                if response.status_code == 200:
                    html = response.text

                    # Extract server URL
                    server_match = re.search(r'name="_.?server"[^>]*value="([^"]+)"', html)
                    if server_match:
                        ldap_config['settings']['server'] = server_match.group(1)

                    # Extract root DN
                    root_dn_match = re.search(r'name="_.?rootDN"[^>]*value="([^"]+)"', html)
                    if root_dn_match:
                        ldap_config['settings']['root_dn'] = root_dn_match.group(1)

                    # Extract user search base
                    user_search_match = re.search(r'name="_.?userSearchBase"[^>]*value="([^"]+)"', html)
                    if user_search_match:
                        ldap_config['settings']['user_search_base'] = user_search_match.group(1)

                    # Extract group search base
                    group_search_match = re.search(r'name="_.?groupSearchBase"[^>]*value="([^"]+)"', html)
                    if group_search_match:
                        ldap_config['settings']['group_search_base'] = group_search_match.group(1)
            except Exception:
                pass

        return ldap_config

    def _get_permissions_config(self):
        """Get permissions configuration"""
        permissions_config = {
            'strategy': 'Unknown',
            'matrix': {}
        }

        # Try to get authorization strategy
        try:
            for path in ['configureSecurity/api/json', 'manage/configureSecurity/api/json']:
                response = self.fetch_jenkins_data(path)
                if "error" not in response and "authorizationStrategy" in response:
                    auth_strategy = response.get("authorizationStrategy", {})
                    auth_class = auth_strategy.get("_class", "")

                    if "ProjectMatrixAuthorizationStrategy" in auth_class:
                        permissions_config['strategy'] = "Project-based Matrix Authorization"
                    elif "GlobalMatrixAuthorizationStrategy" in auth_class:
                        permissions_config['strategy'] = "Matrix Authorization"
                    elif "LegacyAuthorizationStrategy" in auth_class:
                        permissions_config['strategy'] = "Legacy Authorization"
                    elif "RoleBasedAuthorizationStrategy" in auth_class:
                        permissions_config['strategy'] = "Role-based Authorization"
                    else:
                        permissions_config['strategy'] = auth_class.split(".")[-1]

                    # Try to extract permission matrix
                    if "data" in auth_strategy:
                        for permission, users in auth_strategy.get("data", {}).items():
                            permissions_config['matrix'][permission] = users
                    break
        except Exception:
            pass

        # If we couldn't get from API, try to extract from HTML
        if permissions_config['strategy'] == 'Unknown' or not permissions_config['matrix']:
            try:
                response = self.session.get(f"{self.url}manage/configureSecurity/")
                if response.status_code == 200:
                    html = response.text

                    # Check for Matrix Authorization
                    if "Matrix Authorization" in html:
                        permissions_config['strategy'] = "Matrix Authorization"
                    elif "Project-based Matrix" in html:
                        permissions_config['strategy'] = "Project-based Matrix Authorization"
                    elif "Role-Based Strategy" in html:
                        permissions_config['strategy'] = "Role-based Authorization"

                    # Try to find users and their permissions
                    # This is complex to extract from HTML without proper parsing
                    # Just extract user list from the matrix
                    users = set()
                    user_matches = re.findall(r'row-group-(\w+)"', html)
                    if user_matches:
                        for user in user_matches:
                            users.add(user)

                        permissions_config['matrix']['users'] = list(users)
            except Exception:
                pass

        # If we still don't have data, check if we can extract from roles plugin
        if permissions_config['strategy'] == 'Role-based Authorization' and not permissions_config['matrix']:
            try:
                response = self.fetch_jenkins_data("role-strategy/api/json")
                if "error" not in response:
                    permissions_config['matrix'] = response
            except Exception:
                pass

        return permissions_config
