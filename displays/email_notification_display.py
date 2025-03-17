#!/usr/bin/env python3
"""
Jenkins Email Notification Display Module
This module displays information about Jenkins email notification settings.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader

def display_email_settings(info):
    """
    Display Jenkins email notification settings

    Args:
        info (dict): Email settings information

    Returns:
        bool: Success status
    """
    if "error" in info:
        print(f"{Colors.ERROR}Error: {info['error']}{Colors.RESET}")
        return False

    # Check if email notification is enabled
    enabled = info.get('enabled', False)
    extended_email = info.get('extended_email', False)

    # Prepare email settings table
    email_table = []

    # Add enabled status with color
    if enabled:
        email_table.append(['Status', f"{Colors.STATUS_SUCCESS}Enabled{Colors.RESET}"])
    else:
        email_table.append(['Status', f"{Colors.WARNING}Disabled{Colors.RESET}"])

    # Add extended email status
    if extended_email:
        email_table.append(['Extended Email', f"{Colors.STATUS_SUCCESS}Enabled{Colors.RESET}"])

    # Add other settings if available
    if 'smtp_server' in info:
        email_table.append(['SMTP Server', info.get('smtp_server', 'Not configured')])

    if 'smtp_port' in info:
        email_table.append(['SMTP Port', info.get('smtp_port', '25')])

    if 'smtp_auth' in info:
        auth_status = "Enabled" if info.get('smtp_auth', False) else "Disabled"
        email_table.append(['SMTP Authentication', auth_status])

    if 'smtp_username' in info:
        email_table.append(['SMTP Username', info.get('smtp_username', '')])

    if 'default_suffix' in info:
        email_table.append(['Default Email Suffix', info.get('default_suffix', '')])

    if 'admin_email' in info:
        email_table.append(['Admin Email', info.get('admin_email', '')])

    if 'reply_to' in info:
        email_table.append(['Reply-To Address', info.get('reply_to', '')])

    if 'content_type' in info:
        email_table.append(['Content Type', info.get('content_type', '')])

    if 'test_available' in info:
        test_status = "Available" if info.get('test_available', False) else "Not available"
        email_table.append(['Test Email Functionality', test_status])

    print(format_subheader("Jenkins Email Notification Settings"))
    print(tabulate(email_table, headers=['Setting', 'Value'], tablefmt='grid'))

    # Display email triggers if available
    triggers = info.get('triggers', [])
    if triggers:
        print(format_subheader("Email Notification Triggers"))
        print(", ".join(triggers))

    # Display recipient examples if available
    recipients = info.get('recipient_examples', [])
    if recipients:
        print(format_subheader("Example Email Recipients"))
        print(", ".join(recipients))

    return True
