#!/usr/bin/env python3
"""
Jenkins Dashboard
A comprehensive CLI dashboard for Jenkins monitoring and information display

Usage:
  python jenkins_dashboard.py <jenkins_url> <username> <password> [OPTIONS]

Options:
  --no-ssl-verify       Disable SSL certificate verification
  --info                Display basic Jenkins information
  --system              Display detailed system information
  --jobs                Display jobs information
  --nodes               Display nodes information
  --plugins             Display plugins information
  --queue               Display build queue information
  --disk                Display disk usage information
  --hardware            Display hardware information
  --alerts              Display alerts and warnings only
  --users               Display users and permissions information
  --ldap                Display LDAP configuration if exists
  --email               Display email notification settings
  --tools               Display configured build tools
  --notifications       Display notification systems configuration
  --os                  Display OS distribution information
  --os-summary          Display detailed OS distribution summary
  --labels              Display node labels information
  --executors           Display executor usage information
  --build-stats         Display build statistics (duration and frequency)
  --failed-jobs         Display information about failing jobs
  --security            Display security configuration
  --artifacts           Display build artifacts information
  --node-details        Display detailed node information (OS, hardware, software)
  --node-os             Display detailed OS information for nodes
  --node-hw             Display hardware information for nodes
  --node-sw             Display software and system information for nodes
  --all                 Display all information (default if no options specified)
"""

import sys
import argparse
from colorama import init

# Initialize colorama
init(autoreset=True)

# Utils imports
from utils.formatting import Colors, format_header, format_subheader
from utils.api_helpers import get_jenkins_api_url, extract_crumb

# Client imports
from login_client import JenkinsClient

# Collector imports
from collectors.system_collector import JenkinsSystemCollector
from collectors.jobs_collector import JenkinsJobsCollector
from collectors.jobs_summary_collector import JenkinsJobsStatCollector
from collectors.nodes_collector import JenkinsNodesCollector
from collectors.nodes_summary_collector import JenkinsNodesStatCollector
from collectors.queue_collector import JenkinsQueueCollector
from collectors.plugins_collector import JenkinsPluginsCollector
from collectors.disk_collector import JenkinsDiskCollector
from collectors.alerts_collector import JenkinsAlertsCollector
from collectors.hardware_collector import JenkinsHardwareCollector
from collectors.info_collector import JenkinsInfoCollector
from collectors.os_detail_collector import JenkinsOSDetailCollector
from collectors.labels_info_collector import JenkinsLabelsCollector
from collectors.executor_usage_collector import JenkinsExecutorUsageCollector
from collectors.build_stats_collector import JenkinsBuildStatsCollector
from collectors.failed_jobs_collector import JenkinsFailedJobsCollector
from collectors.security_collector import JenkinsSecurityCollector
from collectors.build_artifacts_collector import JenkinsBuildArtifactsCollector
from collectors.users_permissions_collector import JenkinsUsersCollector
from collectors.email_notification_collector import JenkinsEmailCollector
from collectors.tools_collector import JenkinsToolsCollector
from collectors.notification_collector import JenkinsNotificationCollector
from collectors.node_details_collector import JenkinsNodeDetailsCollector

# Display imports
from displays.system_display import display_system_summary
from displays.jobs_display import display_jobs_overview, display_job_types, display_recent_builds
from displays.jobs_summary_display import display_jobs_summary
from displays.nodes_display import display_nodes_overview, display_node_labels_distribution
from displays.nodes_summary_display import display_nodes_summary
from displays.queue_display import display_queue_summary
from displays.plugins_display import display_plugins_summary
from displays.disk_display import display_disk_summary
from displays.alerts_display import display_alerts
from displays.hardware_display import display_hardware_summary
from displays.info_display import display_jenkins_info
from displays.os_display import display_os_distribution, display_linux_details, display_os_details_table
from displays.os_display import display_detailed_os_distribution, display_os_distribution_summary
from displays.labels_display import display_node_labels_table, display_label_usage
from displays.executor_display import display_executor_usage
from displays.build_stats_display import display_build_durations, display_build_frequencies
from displays.failed_jobs_display import display_failed_jobs
from displays.security_display import display_security_config
from displays.build_artifacts_display import display_build_artifacts
from displays.users_display import display_users_info, display_ldap_settings, display_permissions_info
from displays.email_notification_display import display_email_settings
from displays.tools_display import display_tools_info
from displays.notification_display import display_notification_info
from displays.node_details_display import display_os_details, display_hardware_details, display_software_details, display_all_node_details

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Jenkins Dashboard - A comprehensive CLI dashboard for Jenkins monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python jenkins_dashboard.py jenkins.example.com admin password
  python jenkins_dashboard.py https://jenkins.example.com admin password --no-ssl-verify
  python jenkins_dashboard.py https://jenkins.example.com admin password --info
  python jenkins_dashboard.py https://jenkins.example.com admin password --system
  python jenkins_dashboard.py https://jenkins.example.com admin password --jobs
  python jenkins_dashboard.py https://jenkins.example.com admin password --all
        """
    )

    parser.add_argument("url", help="Jenkins URL")
    parser.add_argument("username", help="Jenkins username")
    parser.add_argument("password", help="Jenkins password")
    parser.add_argument("--no-ssl-verify", action="store_true",
                      help="Disable SSL certificate verification")

    # Basic information options
    parser.add_argument("--info", action="store_true",
                      help="Display basic Jenkins information")
    parser.add_argument("--system", action="store_true",
                      help="Display detailed system information")

    # Job-related options
    parser.add_argument("--jobs", action="store_true",
                      help="Display jobs information")
    parser.add_argument("--failed-jobs", action="store_true",
                      help="Display information about failing jobs")
    parser.add_argument("--build-stats", action="store_true",
                      help="Display build statistics (duration and frequency)")
    parser.add_argument("--artifacts", action="store_true",
                      help="Display build artifacts information")

    # Node-related options
    parser.add_argument("--nodes", action="store_true",
                      help="Display nodes information")
    parser.add_argument("--labels", action="store_true",
                      help="Display node labels information")
    parser.add_argument("--executors", action="store_true",
                      help="Display executor usage information")
    parser.add_argument("--os", action="store_true",
                      help="Display OS distribution information")
    parser.add_argument("--os-summary", action="store_true",
                      help="Display detailed OS distribution summary")
    parser.add_argument("--hardware", action="store_true",
                      help="Display hardware information")

    # Node details options
    parser.add_argument("--node-details", action="store_true", 
                      help="Display detailed node information (OS, hardware, software)")
    parser.add_argument("--node-os", action="store_true",
                      help="Display detailed OS information for nodes")
    parser.add_argument("--node-hw", action="store_true",
                      help="Display hardware information for nodes")
    parser.add_argument("--node-sw", action="store_true", 
                      help="Display software and system information for nodes")

    # Infrastructure options
    parser.add_argument("--plugins", action="store_true",
                      help="Display plugins information")
    parser.add_argument("--queue", action="store_true",
                      help="Display build queue information")
    parser.add_argument("--disk", action="store_true",
                      help="Display disk usage information")

    # Security and configuration options
    parser.add_argument("--security", action="store_true",
                      help="Display security configuration")
    parser.add_argument("--users", action="store_true",
                      help="Display users and permissions information")
    parser.add_argument("--ldap", action="store_true",
                      help="Display LDAP configuration if exists")
    parser.add_argument("--email", action="store_true",
                      help="Display email notification settings")
    parser.add_argument("--tools", action="store_true",
                      help="Display configured build tools")
    parser.add_argument("--notifications", action="store_true",
                      help="Display notification systems configuration")

    # Status options
    parser.add_argument("--alerts", action="store_true",
                      help="Display alerts and warnings only")

    # Combined options
    parser.add_argument("--all", action="store_true",
                      help="Display all information")

    return parser.parse_args()

def display_overview(client):
    """
    Display a comprehensive overview of Jenkins status

    Args:
        client: Authenticated JenkinsClient
    """
    print(format_header("JENKINS DASHBOARD OVERVIEW"))

    # Display system information
    try:
        system_collector = JenkinsSystemCollector(client)
        system_info = system_collector.get_system_info()
        display_system_summary(system_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting system information: {str(e)}{Colors.RESET}")

    # Display jobs summary
    try:
        jobs_collector = JenkinsJobsStatCollector(client)
        jobs_info = jobs_collector.get_jobs_summary()
        display_jobs_summary(jobs_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting jobs information: {str(e)}{Colors.RESET}")

    # Display nodes summary
    try:
        nodes_collector = JenkinsNodesStatCollector(client)
        nodes_info = nodes_collector.get_nodes_summary()
        display_nodes_summary(nodes_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting nodes information: {str(e)}{Colors.RESET}")

    # Display queue information
    try:
        queue_collector = JenkinsQueueCollector(client)
        queue_info = queue_collector.get_queue_summary()
        display_queue_summary(queue_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting queue information: {str(e)}{Colors.RESET}")

    # Display plugins information
    try:
        plugins_collector = JenkinsPluginsCollector(client)
        plugins_info = plugins_collector.get_plugins_summary()
        display_plugins_summary(plugins_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting plugins information: {str(e)}{Colors.RESET}")

    # Display disk usage information
    try:
        disk_collector = JenkinsDiskCollector(client)
        disk_info = disk_collector.get_disk_summary()
        display_disk_summary(disk_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting disk information: {str(e)}{Colors.RESET}")

    # Display hardware information
    try:
        hardware_collector = JenkinsHardwareCollector(client)
        hardware_info = hardware_collector.get_hardware_info()
        display_hardware_summary(hardware_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting hardware information: {str(e)}{Colors.RESET}")

    # Display basic users information
    try:
        users_collector = JenkinsUsersCollector(client)
        users_info = users_collector.get_users_info()
        display_users_info(users_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting users information: {str(e)}{Colors.RESET}")

    # Display OS distribution
    try:
        os_collector = JenkinsOSDetailCollector(client)
        os_info = os_collector.get_os_details()
        display_os_distribution(os_info)

        # Display detailed OS distribution if available
        nodes_collector = JenkinsNodesCollector(client)
        nodes_overview = nodes_collector.get_nodes_overview()
        if 'os_distribution' in nodes_overview:
            display_detailed_os_distribution(nodes_overview['os_distribution'])
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting OS information: {str(e)}{Colors.RESET}")

    # Display failed jobs
    try:
        failed_jobs_collector = JenkinsFailedJobsCollector(client)
        failed_jobs_info = failed_jobs_collector.get_failed_jobs()
        display_failed_jobs(failed_jobs_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting failed jobs information: {str(e)}{Colors.RESET}")

    # Generate and display alerts
    try:
        alerts_collector = JenkinsAlertsCollector(client)

        # Get data from previous collectors if available
        try:
            alerts_collector.analyze_disk_usage(disk_info)
        except:
            pass

        try:
            alerts_collector.analyze_nodes(nodes_info)
        except:
            pass

        try:
            alerts_collector.analyze_jobs(jobs_info)
        except:
            pass

        try:
            alerts_collector.analyze_queue(queue_info)
        except:
            pass

        try:
            alerts_collector.analyze_plugins(plugins_info)
        except:
            pass

        try:
            alerts_collector.analyze_system(system_info)
        except:
            pass

        alerts_info = alerts_collector.get_alerts_summary()
        display_alerts(alerts_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error generating alerts: {str(e)}{Colors.RESET}")

    print(format_header("JENKINS DASHBOARD OVERVIEW END"))

def display_comprehensive_overview(client):
    """
    Display a comprehensive overview of all Jenkins information

    Args:
        client: Authenticated JenkinsClient
    """
    print(format_header("COMPREHENSIVE JENKINS DASHBOARD"))

    # System Information Section
    print(format_header("SYSTEM INFORMATION"))

    # Basic system information
    try:
        system_collector = JenkinsSystemCollector(client)
        system_info = system_collector.get_system_info()
        display_system_summary(system_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting system information: {str(e)}{Colors.RESET}")

    # Detailed system information
    try:
        info_collector = JenkinsInfoCollector(client)
        jenkins_info = info_collector.get_jenkins_info()
        display_jenkins_info(jenkins_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting detailed system information: {str(e)}{Colors.RESET}")

    # Security configuration
    try:
        security_collector = JenkinsSecurityCollector(client)
        security_info = security_collector.get_security_config()
        display_security_config(security_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting security information: {str(e)}{Colors.RESET}")

    # Users and permissions
    try:
        users_collector = JenkinsUsersCollector(client)
        users_info = users_collector.get_users_info()
        display_users_info(users_info)
        display_ldap_settings(users_info)
        display_permissions_info(users_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting users information: {str(e)}{Colors.RESET}")

    # Jobs Section
    print(format_header("JOBS INFORMATION"))

    # Jobs summary
    try:
        jobs_collector = JenkinsJobsStatCollector(client)
        jobs_info = jobs_collector.get_jobs_summary()
        display_jobs_summary(jobs_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting jobs summary: {str(e)}{Colors.RESET}")

    # Detailed jobs information
    try:
        jobs_collector = JenkinsJobsCollector(client)
        jobs_overview = jobs_collector.get_jobs_overview()
        display_jobs_overview(jobs_overview)

        job_types = jobs_collector.get_job_types()
        display_job_types(job_types)

        recent_builds = jobs_collector.get_recent_builds(10)
        display_recent_builds(recent_builds)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting detailed jobs information: {str(e)}{Colors.RESET}")

    # Failed jobs
    try:
        failed_jobs_collector = JenkinsFailedJobsCollector(client)
        failed_jobs_info = failed_jobs_collector.get_failed_jobs()
        display_failed_jobs(failed_jobs_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting failed jobs information: {str(e)}{Colors.RESET}")

    # Build statistics
    try:
        build_stats_collector = JenkinsBuildStatsCollector(client)
        build_durations = build_stats_collector.get_build_durations()
        display_build_durations(build_durations)

        build_frequencies = build_stats_collector.get_build_frequencies()
        display_build_frequencies(build_frequencies)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting build statistics: {str(e)}{Colors.RESET}")

    # Build artifacts
    try:
        artifacts_collector = JenkinsBuildArtifactsCollector(client)
        artifacts_info = artifacts_collector.get_build_artifacts()
        display_build_artifacts(artifacts_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting build artifacts information: {str(e)}{Colors.RESET}")

    # Nodes Section
    print(format_header("NODES INFORMATION"))

    # Nodes summary
    try:
        nodes_collector = JenkinsNodesStatCollector(client)
        nodes_info = nodes_collector.get_nodes_summary()
        display_nodes_summary(nodes_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting nodes summary: {str(e)}{Colors.RESET}")

    # Detailed nodes information
    try:
        nodes_collector = JenkinsNodesCollector(client)
        nodes_overview = nodes_collector.get_nodes_overview()
        display_nodes_overview(nodes_overview)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting detailed nodes information: {str(e)}{Colors.RESET}")

    # Node detailed information section
    print(format_header("NODES DETAILED INFORMATION"))

    # Node OS, Hardware, and Software details
    try:
        node_details_collector = JenkinsNodeDetailsCollector(client)
        node_details = node_details_collector.get_all_node_details()
        display_all_node_details(node_details)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting detailed node information: {str(e)}{Colors.RESET}")

    # OS information
    try:
        os_collector = JenkinsOSDetailCollector(client)
        os_info = os_collector.get_os_details()
        display_os_distribution(os_info, detailed=True)

        # Display detailed OS distribution
        nodes_collector = JenkinsNodesCollector(client)
        nodes_overview = nodes_collector.get_nodes_overview()
        if 'os_distribution' in nodes_overview:
            display_detailed_os_distribution(nodes_overview['os_distribution'])

        linux_info = os_collector.get_linux_details()
        display_linux_details(linux_info)

        display_os_details_table(os_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting OS information: {str(e)}{Colors.RESET}")

    # Labels information
    try:
        labels_collector = JenkinsLabelsCollector(client)
        labels_info = labels_collector.get_labels_details()
        display_node_labels_distribution(labels_info)
        display_node_labels_table(labels_info)

        labels_usage = labels_collector.get_label_usage()
        display_label_usage(labels_usage)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting labels information: {str(e)}{Colors.RESET}")

    # Executor usage
    try:
        executor_collector = JenkinsExecutorUsageCollector(client)
        executor_info = executor_collector.get_executor_usage()
        display_executor_usage(executor_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting executor usage information: {str(e)}{Colors.RESET}")

    # Hardware information
    try:
        hardware_collector = JenkinsHardwareCollector(client)
        hardware_info = hardware_collector.get_hardware_info()
        display_hardware_summary(hardware_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting hardware information: {str(e)}{Colors.RESET}")

    # Infrastructure Section
    print(format_header("INFRASTRUCTURE INFORMATION"))

    # Plugins information
    try:
        plugins_collector = JenkinsPluginsCollector(client)
        plugins_info = plugins_collector.get_plugins_summary()
        display_plugins_summary(plugins_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting plugins information: {str(e)}{Colors.RESET}")

    # Queue information
    try:
        queue_collector = JenkinsQueueCollector(client)
        queue_info = queue_collector.get_queue_summary()
        display_queue_summary(queue_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting queue information: {str(e)}{Colors.RESET}")

    # Disk usage information
    try:
        disk_collector = JenkinsDiskCollector(client)
        disk_info = disk_collector.get_disk_summary()
        display_disk_summary(disk_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting disk information: {str(e)}{Colors.RESET}")

    # Tools information
    try:
        tools_collector = JenkinsToolsCollector(client)
        tools_info = tools_collector.get_tools_info()
        display_tools_info(tools_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting tools information: {str(e)}{Colors.RESET}")

    # Configuration Section
    print(format_header("CONFIGURATION INFORMATION"))

    # Email settings
    try:
        email_collector = JenkinsEmailCollector(client)
        email_info = email_collector.get_email_settings()
        display_email_settings(email_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting email settings: {str(e)}{Colors.RESET}")

    # Notification systems
    try:
        notification_collector = JenkinsNotificationCollector(client)
        notification_info = notification_collector.get_notification_info()
        display_notification_info(notification_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error collecting notification systems information: {str(e)}{Colors.RESET}")

    # Alerts and Warnings
    print(format_header("ALERTS AND WARNINGS"))

    # Generate and display alerts
    try:
        alerts_collector = JenkinsAlertsCollector(client)

        # Try to get data from already collected information
        try:
            disk_collector = JenkinsDiskCollector(client)
            disk_info = disk_collector.get_disk_summary()
            alerts_collector.analyze_disk_usage(disk_info)
        except:
            pass

        try:
            nodes_collector = JenkinsNodesCollector(client)
            nodes_info = nodes_collector.get_nodes_overview()
            alerts_collector.analyze_nodes(nodes_info)
        except:
            pass

        try:
            jobs_collector = JenkinsJobsCollector(client)
            jobs_info = jobs_collector.get_jobs_overview()
            alerts_collector.analyze_jobs(jobs_info)
        except:
            pass

        try:
            queue_collector = JenkinsQueueCollector(client)
            queue_info = queue_collector.get_queue_summary()
            alerts_collector.analyze_queue(queue_info)
        except:
            pass

        try:
            plugins_collector = JenkinsPluginsCollector(client)
            plugins_info = plugins_collector.get_plugins_summary()
            alerts_collector.analyze_plugins(plugins_info)
        except:
            pass

        try:
            system_collector = JenkinsSystemCollector(client)
            system_info = system_collector.get_system_info()
            alerts_collector.analyze_system(system_info)
        except:
            pass

        alerts_info = alerts_collector.get_alerts_summary()
        display_alerts(alerts_info)
    except Exception as e:
        print(f"{Colors.ERROR}Error generating alerts: {str(e)}{Colors.RESET}")

    print(format_header("COMPREHENSIVE JENKINS DASHBOARD END"))

def main():
    """Main entry point"""
    # Parse command line arguments
    args = parse_arguments()

    print(f"{Colors.INFO}Connecting to Jenkins at {args.url}...{Colors.RESET}")

    # Create client and login
    skip_ssl = args.no_ssl_verify
    if skip_ssl:
        print(f"{Colors.WARNING}SSL verification: Disabled{Colors.RESET}")

    client = JenkinsClient(skip_ssl_verify=skip_ssl)
    login_result = client.login(args.url, args.username, args.password)

    if not login_result.get('success', False):
        print(f"{Colors.ERROR}Error: {login_result.get('message', 'Unknown login error')}{Colors.RESET}")
        sys.exit(1)

    print(f"{Colors.SUCCESS}Successfully connected to Jenkins {login_result.get('version', 'Unknown')}{Colors.RESET}")

    # Determine what information to display
    show_all = args.all

    # For comprehensive overview, show everything
    if show_all:
        display_comprehensive_overview(client)
        return

    # Check if any specific options are selected
    any_option_selected = any([
        args.info, args.system, args.jobs, args.nodes, args.plugins,
        args.queue, args.disk, args.hardware, args.alerts, args.users,
        args.ldap, args.email, args.tools, args.notifications, args.os,
        args.os_summary, args.labels, args.executors, args.build_stats,
        args.failed_jobs, args.security, args.artifacts, args.node_details,
        args.node_os, args.node_hw, args.node_sw
    ])

    # If no specific options, show basic overview
    if not any_option_selected:
        display_overview(client)
        return

    # Show specific information based on flags
    if args.info:
        print(format_header("JENKINS INFORMATION"))
        try:
            info_collector = JenkinsInfoCollector(client)
            jenkins_info = info_collector.get_jenkins_info()
            display_jenkins_info(jenkins_info)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.system:
        print(format_header("JENKINS SYSTEM INFORMATION"))
        try:
            system_collector = JenkinsSystemCollector(client)
            system_info = system_collector.get_system_info()
            display_system_summary(system_info)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.jobs:
        print(format_header("JENKINS JOBS INFORMATION"))
        try:
            # Get jobs summary
            jobs_summary_collector = JenkinsJobsStatCollector(client)
            jobs_summary = jobs_summary_collector.get_jobs_summary()
            display_jobs_summary(jobs_summary)

            # Get detailed jobs information
            jobs_collector = JenkinsJobsCollector(client)
            jobs_overview = jobs_collector.get_jobs_overview()
            display_jobs_overview(jobs_overview)

            job_types = jobs_collector.get_job_types()
            display_job_types(job_types)

            recent_builds = jobs_collector.get_recent_builds(10)
            display_recent_builds(recent_builds)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.nodes:
        print(format_header("JENKINS NODES INFORMATION"))
        try:
            # Get nodes summary
            nodes_summary_collector = JenkinsNodesStatCollector(client)
            nodes_summary = nodes_summary_collector.get_nodes_summary()
            display_nodes_summary(nodes_summary)

            # Get detailed nodes information
            nodes_collector = JenkinsNodesCollector(client)
            nodes_overview = nodes_collector.get_nodes_overview()
            display_nodes_overview(nodes_overview)
            display_node_labels_distribution(nodes_overview)

            # Display detailed OS distribution
            if 'os_distribution' in nodes_overview:
                display_detailed_os_distribution(nodes_overview['os_distribution'])
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.node_details or args.node_os or args.node_hw or args.node_sw:
        print(format_header("JENKINS NODES DETAILED INFORMATION"))
        try:
            node_details_collector = JenkinsNodeDetailsCollector(client)
            
            if args.node_details:
                # Get all details
                details = node_details_collector.get_all_node_details()
                display_all_node_details(details)
            else:
                # Get specific details
                if args.node_os:
                    os_details = node_details_collector.get_os_details_table()
                    display_os_details(os_details)
                
                if args.node_hw:
                    hw_details = node_details_collector.get_hardware_details_table()
                    display_hardware_details(hw_details)
                
                if args.node_sw:
                    sw_details = node_details_collector.get_software_details_table()
                    display_software_details(sw_details)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.plugins:
        print(format_header("JENKINS PLUGINS INFORMATION"))
        try:
            plugins_collector = JenkinsPluginsCollector(client)
            plugins_info = plugins_collector.get_plugins_summary()
            display_plugins_summary(plugins_info)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.queue:
        print(format_header("JENKINS QUEUE INFORMATION"))
        try:
            queue_collector = JenkinsQueueCollector(client)
            queue_info = queue_collector.get_queue_summary()
            display_queue_summary(queue_info)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.disk:
        print(format_header("JENKINS DISK USAGE INFORMATION"))
        try:
            disk_collector = JenkinsDiskCollector(client)
            disk_info = disk_collector.get_disk_summary()
            display_disk_summary(disk_info)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.hardware:
        print(format_header("JENKINS HARDWARE INFORMATION"))
        try:
            hardware_collector = JenkinsHardwareCollector(client)
            hardware_info = hardware_collector.get_hardware_info()
            display_hardware_summary(hardware_info)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.os:
        print(format_header("JENKINS OS INFORMATION"))
        try:
            os_collector = JenkinsOSDetailCollector(client)
            os_info = os_collector.get_os_details()
            display_os_distribution(os_info, detailed=True)

            # Display detailed OS distribution
            nodes_collector = JenkinsNodesCollector(client)
            nodes_overview = nodes_collector.get_nodes_overview()
            if 'os_distribution' in nodes_overview:
                display_detailed_os_distribution(nodes_overview['os_distribution'])

            linux_info = os_collector.get_linux_details()
            display_linux_details(linux_info)

            display_os_details_table(os_info)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.os_summary:
        print(format_header("JENKINS OS DISTRIBUTION SUMMARY"))
        try:
            nodes_collector = JenkinsNodesCollector(client)
            os_summary = nodes_collector.get_os_distribution_summary()
            display_os_distribution_summary(os_summary)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.labels:
        print(format_header("JENKINS LABELS INFORMATION"))
        try:
            labels_collector = JenkinsLabelsCollector(client)
            labels_info = labels_collector.get_labels_details()
            display_node_labels_distribution(labels_info)
            display_node_labels_table(labels_info)

            labels_usage = labels_collector.get_label_usage()
            display_label_usage(labels_usage)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.executors:
        print(format_header("JENKINS EXECUTOR USAGE INFORMATION"))
        try:
            executor_collector = JenkinsExecutorUsageCollector(client)
            executor_info = executor_collector.get_executor_usage()
            display_executor_usage(executor_info)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.build_stats:
        print(format_header("JENKINS BUILD STATISTICS"))
        try:
            build_stats_collector = JenkinsBuildStatsCollector(client)
            build_durations = build_stats_collector.get_build_durations()
            display_build_durations(build_durations)

            build_frequencies = build_stats_collector.get_build_frequencies()
            display_build_frequencies(build_frequencies)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.failed_jobs:
        print(format_header("JENKINS FAILED JOBS"))
        try:
            failed_jobs_collector = JenkinsFailedJobsCollector(client)
            failed_jobs_info = failed_jobs_collector.get_failed_jobs()
            display_failed_jobs(failed_jobs_info)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.security:
        print(format_header("JENKINS SECURITY CONFIGURATION"))
        try:
            security_collector = JenkinsSecurityCollector(client)
            security_info = security_collector.get_security_config()
            display_security_config(security_info)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.artifacts:
        print(format_header("JENKINS BUILD ARTIFACTS"))
        try:
            artifacts_collector = JenkinsBuildArtifactsCollector(client)
            artifacts_info = artifacts_collector.get_build_artifacts()
            display_build_artifacts(artifacts_info)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.users or args.ldap:
        print(format_header("JENKINS USERS AND PERMISSIONS"))
        try:
            users_collector = JenkinsUsersCollector(client)
            users_info = users_collector.get_users_info()

            if args.users:
                display_users_info(users_info)
                display_permissions_info(users_info)

            if args.ldap:
                display_ldap_settings(users_info)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.email:
        print(format_header("JENKINS EMAIL NOTIFICATION SETTINGS"))
        try:
            email_collector = JenkinsEmailCollector(client)
            email_info = email_collector.get_email_settings()
            display_email_settings(email_info)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.tools:
        print(format_header("JENKINS TOOLS CONFIGURATION"))
        try:
            tools_collector = JenkinsToolsCollector(client)
            tools_info = tools_collector.get_tools_info()
            display_tools_info(tools_info)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.notifications:
        print(format_header("JENKINS NOTIFICATION SYSTEMS"))
        try:
            notification_collector = JenkinsNotificationCollector(client)
            notification_info = notification_collector.get_notification_info()
            display_notification_info(notification_info)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

    if args.alerts:
        print(format_header("JENKINS ALERTS AND WARNINGS"))
        try:
            # Initialize needed collectors
            disk_collector = JenkinsDiskCollector(client)
            disk_info = disk_collector.get_disk_summary()

            nodes_collector = JenkinsNodesCollector(client)
            nodes_info = nodes_collector.get_nodes_overview()

            jobs_collector = JenkinsJobsCollector(client)
            jobs_info = jobs_collector.get_jobs_overview()

            queue_collector = JenkinsQueueCollector(client)
            queue_info = queue_collector.get_queue_summary()

            plugins_collector = JenkinsPluginsCollector(client)
            plugins_info = plugins_collector.get_plugins_summary()

            system_collector = JenkinsSystemCollector(client)
            system_info = system_collector.get_system_info()

            # Analyze data and show alerts
            alerts_collector = JenkinsAlertsCollector(client)
            alerts_collector.analyze_disk_usage(disk_info)
            alerts_collector.analyze_nodes(nodes_info)
            alerts_collector.analyze_jobs(jobs_info)
            alerts_collector.analyze_queue(queue_info)
            alerts_collector.analyze_plugins(plugins_info)
            alerts_collector.analyze_system(system_info)

            alerts_info = alerts_collector.get_alerts_summary()
            display_alerts(alerts_info)
        except Exception as e:
            print(f"{Colors.ERROR}Error: {str(e)}{Colors.RESET}")

if __name__ == "__main__":
    main()
