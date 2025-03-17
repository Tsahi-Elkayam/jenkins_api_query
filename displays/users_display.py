#!/usr/bin/env python3
"""
Jenkins Users and Permissions Display Module
This module displays information about Jenkins users and their permissions.
"""

from tabulate import tabulate
from utils.formatting import Colors, format_subheader

def display_users_info(info):
    """
    Display information about Jenkins users

    Args:
        info (dict): Users information

    Returns:
        bool: Success status
    """
    if "error" in info:
        print(f"{Colors.ERROR}Error: {info['error']}{Colors.RESET}")
        return False

    # Display summary
    user_count = info.get('user_count', {})
    total_users = info.get('total_users', 0)

    summary_data = [
        ['Total Users', total_users],
        ['Admin Users', user_count.get('admin', 0)],
        ['Regular Users', user_count.get('regular', 0)],
        ['Service Accounts', user_count.get('service', 0)]
    ]

    print(format_subheader("Jenkins Users Summary"))
    print(tabulate(summary_data, headers=['Metric', 'Count'], tablefmt='grid'))

    # Display users table
    users = info.get('users', [])
    if not users:
        print(f"\n{Colors.WARNING}No user information available{Colors.RESET}")
        return True

    # Prepare users table
    users_table = []
    for user in users:
        # Format user type with color
        user_type = "Admin" if user.get('is_admin', False) else "Service" if user.get('id', '').lower().endswith('bot') or 'service' in user.get('id', '').lower() else "User"

        if user_type == "Admin":
            user_type_str = f"{Colors.ERROR}Admin{Colors.RESET}"
        elif user_type == "Service":
            user_type_str = f"{Colors.INFO}Service{Colors.RESET}"
        else:
            user_type_str = f"{Colors.RESET}User{Colors.RESET}"

        # Format LDAP indicator
        ldap_indicator = "LDAP" if user.get('is_ldap', False) else ""

        users_table.append([
            user.get('id', 'Unknown'),
            user.get('full_name', user.get('id', 'Unknown')),
            user_type_str,
            user.get('last_login', 'Unknown'),
            user.get('api_usage', 'None'),
            ldap_indicator
        ])

    # Sort by user type (admins first) then by ID
    users_table.sort(key=lambda x: ("Admin" not in x[2], "Service" not in x[2], x[0]))

    # Limit to 20 users if more
    if len(users_table) > 20:
        print(f"\n{Colors.INFO}Users (showing 20 of {len(users)} users):{Colors.RESET}")
        print(tabulate(
            users_table[:20],
            headers=['User ID', 'Full Name', 'Type', 'Last Login', 'API Usage', 'Source'],
            tablefmt='grid'
        ))
    else:
        print(f"\n{Colors.INFO}Users:{Colors.RESET}")
        print(tabulate(
            users_table,
            headers=['User ID', 'Full Name', 'Type', 'Last Login', 'API Usage', 'Source'],
            tablefmt='grid'
        ))

    # If admin users exist, show them in a separate table
    admin_users = [user for user in users if user.get('is_admin', False)]
    if admin_users:
        admin_table = []
        for user in admin_users:
            admin_table.append([
                user.get('id', 'Unknown'),
                user.get('full_name', user.get('id', 'Unknown')),
                user.get('last_login', 'Unknown')
            ])

        print(format_subheader(f"Admin Users ({len(admin_users)})"))
        print(tabulate(
            admin_table,
            headers=['User ID', 'Full Name', 'Last Login'],
            tablefmt='grid'
        ))

    return True

def display_ldap_settings(info):
    """
    Display LDAP settings if available

    Args:
        info (dict): Users information with LDAP settings

    Returns:
        bool: Success status
    """
    ldap_settings = info.get('ldap_settings', {})

    if not ldap_settings:
        print(f"\n{Colors.INFO}LDAP: Not configured{Colors.RESET}")
        return True

    # Prepare LDAP table
    ldap_table = []
    for key, value in ldap_settings.items():
        if key != 'enabled':
            # Mask server credentials for security
            if 'server' in key and value:
                # Only show domain part
                parts = value.split('://')
                if len(parts) > 1:
                    domain = parts[1].split(':')[0]
                    value = f"{parts[0]}://{domain}:*****"

            ldap_table.append([key.replace('_', ' ').title(), value])

    print(format_subheader(f"LDAP Configuration ({Colors.STATUS_SUCCESS}Enabled{Colors.RESET})"))
    print(tabulate(ldap_table, headers=['Setting', 'Value'], tablefmt='grid'))

    return True

def display_permissions_info(info):
    """
    Display permissions information

    Args:
        info (dict): Users information with permissions

    Returns:
        bool: Success status
    """
    all_permissions = info.get('all_permissions', [])

    if not all_permissions:
        print(f"\n{Colors.WARNING}No permissions information available{Colors.RESET}")
        return True

    # Group permissions by category
    permission_categories = {}

    for permission in all_permissions:
        # Split by first slash
        if '/' in permission:
            category, name = permission.split('/', 1)
            if category not in permission_categories:
                permission_categories[category] = []
            permission_categories[category].append(name)
        else:
            if 'Other' not in permission_categories:
                permission_categories['Other'] = []
            permission_categories['Other'].append(permission)

    # Display permissions grouped by category
    print(format_subheader("Jenkins Permissions"))

    for category, permissions in sorted(permission_categories.items()):
        # Find users with these permissions
        users_with_category = []

        for user in info.get('users', []):
            if any(f"{category}/{perm}" in user.get('permissions', []) for perm in permissions):
                users_with_category.append(user.get('id', 'Unknown'))

        # Format category with color based on sensitivity
        if category in ['Overall', 'Security', 'Credentials']:
            category_str = f"{Colors.ERROR}{category}{Colors.RESET}"
        elif category in ['Job', 'Run', 'SCM']:
            category_str = f"{Colors.WARNING}{category}{Colors.RESET}"
        else:
            category_str = f"{Colors.INFO}{category}{Colors.RESET}"

        # Display permissions in category
        print(f"\n{category_str} Permissions:")

        perm_table = []
        for perm in sorted(permissions):
            # Count users with this specific permission
            users_with_perm = []
            for user in info.get('users', []):
                if f"{category}/{perm}" in user.get('permissions', []):
                    users_with_perm.append(user.get('id', 'Unknown'))

            perm_table.append([
                perm,
                len(users_with_perm),
                ', '.join(users_with_perm[:3]) + ('...' if len(users_with_perm) > 3 else '')
            ])

        print(tabulate(
            perm_table,
            headers=['Permission', 'Users', 'Example Users'],
            tablefmt='grid'
        ))

    return True
