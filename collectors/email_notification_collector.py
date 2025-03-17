#!/usr/bin/env python3
"""
Jenkins Email Notification Collector
This module collects information about Jenkins email notification settings.
"""

import re
from collectors.base_collector import BaseCollector

class JenkinsEmailCollector(BaseCollector):
    """Collects information about Jenkins email notification settings"""

    def get_email_settings(self):
        """
        Fetches information about Jenkins email settings

        Returns:
            dict: Email settings information
        """
        try:
            # Try to access email configuration page
            response = self.fetch_jenkins_data("configure")
            if "error" in response:
                return {"error": "Could not access email configuration"}

            html = response.get("content", "")

            # Check if email notification is enabled
            email_settings = {
                'enabled': 'E-mail Notification' in html or 'Email Notification' in html,
                'extended_email': 'Extended E-mail Notification' in html
            }

            # Try to extract SMTP server
            smtp_server_match = re.search(r'SMTP Server"?.*?value="(.*?)"', html)
            if smtp_server_match:
                email_settings['smtp_server'] = smtp_server_match.group(1).strip()

            # Try to extract default email suffix
            suffix_match = re.search(r'[dD]efault [sS]uffix"?.*?value="(.*?)"', html)
            if suffix_match:
                email_settings['default_suffix'] = suffix_match.group(1).strip()

            # Try to extract admin email address
            admin_email_match = re.search(r'[aA]dmin [eE]-?mail [aA]ddress"?.*?value="(.*?)"', html)
            if admin_email_match:
                email_settings['admin_email'] = admin_email_match.group(1).strip()

            # Try to extract reply-to address
            reply_to_match = re.search(r'[rR]eply-?[tT]o [aA]ddress"?.*?value="(.*?)"', html)
            if reply_to_match:
                email_settings['reply_to'] = reply_to_match.group(1).strip()

            # Check for SMTP authentication
            email_settings['smtp_auth'] = 'Use SMTP Authentication' in html

            # Try to extract SMTP username if auth is enabled
            if email_settings['smtp_auth']:
                username_match = re.search(r'User Name"?.*?value="(.*?)"', html)
                if username_match:
                    email_settings['smtp_username'] = username_match.group(1).strip()

            # Try to extract SMTP port
            port_match = re.search(r'SMTP Port"?.*?value="(.*?)"', html)
            if port_match:
                email_settings['smtp_port'] = port_match.group(1).strip()

            # Try to get advanced settings for extended email
            if email_settings['extended_email']:
                # Try to extract content type
                content_type_match = re.search(r'Default Content Type"?.*?value="(.*?)"', html)
                if content_type_match:
                    email_settings['content_type'] = content_type_match.group(1).strip()

                # Check for default triggers
                email_settings['triggers'] = []

                common_triggers = [
                    'Always', 'Success', 'Failure', 'Unstable', 'Fixed', 'Still Failing',
                    'Still Unstable', 'Regression', 'Improvement'
                ]

                for trigger in common_triggers:
                    if f'"{trigger}"' in html or f"'{trigger}'" in html or f">{trigger}<" in html:
                        email_settings['triggers'].append(trigger)

            # Try to get email notification test settings
            try:
                # Access test email page
                response = self.fetch_jenkins_data("descriptorByName/hudson.tasks.Mailer/help")
                if "error" not in response and "html" in response:
                    test_html = response["content"]

                    # Check if test email functionality is available
                    email_settings['test_available'] = 'Test configuration' in test_html
            except Exception:
                email_settings['test_available'] = False

            # Get notification recipients from job configurations
            email_settings['recipient_examples'] = self._get_recipient_examples()

            return email_settings

        except Exception as e:
            return {"error": f"Error retrieving email settings: {str(e)}"}

    def _get_recipient_examples(self):
        """
        Get examples of email recipients from job configurations

        Returns:
            list: Sample recipients
        """
        recipients = set()

        try:
            # Get jobs with basic info
            response = self.fetch_jenkins_data("api/json", params={"tree": "jobs[name,url]"})
            if "error" in response:
                return []

            jobs = response.get('jobs', [])

            # Check first 10 jobs
            for job in jobs[:10]:
                job_url = job.get('url', '')

                if not job_url:
                    continue

                # Get job config
                try:
                    response = self.fetch_jenkins_data(f"{job_url}config.xml")
                    if "error" not in response and "html" in response:
                        config = response["content"]

                        # Look for email recipients
                        recipients_matches = re.findall(r'<recipients>(.*?)</recipients>', config)
                        for match in recipients_matches:
                            # Split by comma, space, or semicolon
                            for recipient in re.split(r'[,;\s]+', match):
                                if recipient and '@' in recipient:
                                    recipients.add(recipient.strip())
                except Exception:
                    continue

            return sorted(list(recipients))

        except Exception:
            return []
