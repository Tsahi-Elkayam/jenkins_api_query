#!/usr/bin/env python3
"""
Jenkins Notification Systems Collector
This module collects information about notification systems configured in Jenkins.
"""

import re
from collectors.base_collector import BaseCollector

class JenkinsNotificationCollector(BaseCollector):
    """Collects information about notification systems in Jenkins"""

    def get_notification_info(self):
        """
        Fetches information about notification systems in Jenkins

        Returns:
            dict: Notification systems information
        """
        try:
            # Get notification plugins info
            notification_info = {
                'slack': self._get_slack_info(),
                'teams': self._get_teams_info(),
                'email': self._get_email_info(),
                'other': []
            }

            # Check for other notification systems
            configure_response = self.fetch_jenkins_data("configure")
            if "error" not in configure_response and "html" in configure_response:
                html = configure_response["content"]

                # Check for other common notification systems
                other_notifications = [
                    ('Telegram', r'[tT]elegram'),
                    ('IRC', r'IRC|Internet Relay Chat'),
                    ('Jabber', r'[jJ]abber|XMPP'),
                    ('Mattermost', r'[mM]attermost'),
                    ('Discord', r'[dD]iscord'),
                    ('Google Chat', r'[gG]oogle\s+[cC]hat|Hangouts'),
                    ('Webhooks', r'[wW]ebhooks?')
                ]

                for name, pattern in other_notifications:
                    if re.search(pattern, html):
                        notification_info['other'].append({
                            'name': name,
                            'enabled': True
                        })

            # Get notification usage in jobs
            notification_info['usage'] = self._get_notification_usage()

            return notification_info

        except Exception as e:
            return {"error": f"Error retrieving notification systems information: {str(e)}"}

    def _get_slack_info(self):
        """
        Get Slack notification configuration

        Returns:
            dict: Slack configuration information
        """
        slack_info = {
            'enabled': False
        }

        try:
            # Check if Slack plugin is installed
            response = self.fetch_jenkins_data("pluginManager/api/json?depth=1")
            if "error" not in response:
                plugins = response.get('plugins', [])

                # Look for Slack plugin
                for plugin in plugins:
                    if 'slack' in plugin.get('shortName', '').lower():
                        slack_info['enabled'] = plugin.get('active', False)
                        slack_info['version'] = plugin.get('version', 'Unknown')
                        break

            # If Slack is enabled, try to get configuration
            if slack_info['enabled']:
                # Try to access Slack configuration
                response = self.fetch_jenkins_data("jenkins/descriptorByName/jenkins.plugins.slack.SlackNotifier/configure")
                if "error" not in response and "html" in response:
                    html = response["content"]

                    # Extract workspace
                    workspace_match = re.search(r'[tT]eam [sS]ubdomain.*?value="(.*?)"', html)
                    if workspace_match:
                        slack_info['workspace'] = workspace_match.group(1).strip()

                    # Extract channel
                    channel_match = re.search(r'[dD]efault [cC]hannel.*?value="(.*?)"', html)
                    if channel_match:
                        slack_info['default_channel'] = channel_match.group(1).strip()

                    # Check if token is configured
                    slack_info['token_configured'] = 'Integration Token' in html and 'value="••••••••"' in html

            # If no specific Slack page, try general configuration
            if 'workspace' not in slack_info and slack_info['enabled']:
                response = self.fetch_jenkins_data("configure")
                if "error" not in response and "html" in response:
                    html = response["content"]

                    # Look for Slack section
                    if 'Slack' in html:
                        # Extract workspace
                        workspace_match = re.search(r'[tT]eam [sS]ubdomain.*?value="(.*?)"', html)
                        if workspace_match:
                            slack_info['workspace'] = workspace_match.group(1).strip()

                        # Extract channel
                        channel_match = re.search(r'[dD]efault [cC]hannel.*?value="(.*?)"', html)
                        if channel_match:
                            slack_info['default_channel'] = channel_match.group(1).strip()

                        # Check if token is configured
                        slack_info['token_configured'] = 'Integration Token' in html and 'value="••••••••"' in html
        except Exception:
            # Don't fail completely if Slack info can't be retrieved
            pass

        return slack_info

    def _get_teams_info(self):
        """
        Get Microsoft Teams notification configuration

        Returns:
            dict: Teams configuration information
        """
        teams_info = {
            'enabled': False
        }

        try:
            # Check if Teams plugin is installed
            response = self.fetch_jenkins_data("pluginManager/api/json?depth=1")
            if "error" not in response:
                plugins = response.get('plugins', [])

                # Look for Teams plugin
                for plugin in plugins:
                    if 'microsoft-teams' in plugin.get('shortName', '').lower() or 'office-365' in plugin.get('shortName', '').lower():
                        teams_info['enabled'] = plugin.get('active', False)
                        teams_info['version'] = plugin.get('version', 'Unknown')
                        break

            # If Teams is enabled, try to get configuration
            if teams_info['enabled']:
                response = self.fetch_jenkins_data("configure")
                if "error" not in response and "html" in response:
                    html = response["content"]

                    # Look for Teams section
                    if 'Microsoft Teams' in html or 'Office 365' in html:
                        # Extract webhook URL (partial for security)
                        webhook_match = re.search(r'[wW]ebhook [uU][rR][lL].*?value="https://(.*?)"', html)
                        if webhook_match:
                            teams_info['webhook'] = f"https://{webhook_match.group(1)[:10]}..."

                        # Check if webhook is configured
                        teams_info['webhook_configured'] = 'Webhook URL' in html and 'value="https://' in html
        except Exception:
            # Don't fail completely if Teams info can't be retrieved
            pass

        return teams_info

    def _get_email_info(self):
        """
        Get basic email notification status

        Returns:
            dict: Email notification configuration
        """
        email_info = {
            'enabled': False
        }

        try:
            # Check configure page for email notification
            response = self.fetch_jenkins_data("configure")
            if "error" not in response and "html" in response:
                html = response["content"]

                # Check if email notification is enabled
                email_info['enabled'] = 'E-mail Notification' in html or 'Email Notification' in html
                email_info['extended_email'] = 'Extended E-mail Notification' in html

                # Try to extract SMTP server
                smtp_server_match = re.search(r'SMTP Server"?.*?value="(.*?)"', html)
                if smtp_server_match:
                    email_info['smtp_server'] = smtp_server_match.group(1).strip()
        except Exception:
            # Don't fail completely if email info can't be retrieved
            pass

        return email_info

    def _get_notification_usage(self):
        """
        Get notification usage in jobs

        Returns:
            dict: Notification usage statistics
        """
        usage_info = {
            'slack': 0,
            'teams': 0,
            'email': 0,
            'other': 0,
            'total_jobs_checked': 0
        }

        try:
            # Get a sample of jobs
            response = self.fetch_jenkins_data("api/json", params={"tree": "jobs[name,url]"})
            if "error" in response:
                return usage_info

            jobs = response.get('jobs', [])

            # Check a sample of jobs for notification usage
            for job in jobs[:20]:  # Limit to 20 jobs for performance
                job_url = job.get('url', '')

                if not job_url:
                    continue

                usage_info['total_jobs_checked'] += 1

                # Get job config
                try:
                    response = self.fetch_jenkins_data(f"{job_url}config.xml")
                    if "error" not in response and "html" in response:
                        config = response["content"]

                        # Check for notification systems in the config
                        if 'slack' in config.lower():
                            usage_info['slack'] += 1

                        if 'teams' in config.lower() or 'office365' in config.lower() or 'office-365' in config.lower():
                            usage_info['teams'] += 1

                        if 'mailto' in config.lower() or 'email' in config.lower() or 'e-mail' in config.lower():
                            usage_info['email'] += 1

                        # Check for other notification systems
                        other_patterns = ['telegram', 'irc', 'jabber', 'xmpp', 'mattermost', 'discord', 'webhook', 'notification']
                        if any(pattern in config.lower() for pattern in other_patterns):
                            usage_info['other'] += 1
                except Exception:
                    continue
        except Exception:
            # Don't fail completely if usage info can't be retrieved
            pass

        return usage_info
