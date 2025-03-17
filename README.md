# Jenkins Dashboard

A comprehensive command-line dashboard for monitoring and diagnosing Jenkins CI/CD environments.

![Jenkins Dashboard Screenshot](https://example.com/jenkins-dashboard-screenshot.png)

## Overview

Jenkins Dashboard is a powerful command-line tool that provides detailed information about your Jenkins environment. It collects data through the Jenkins API and presents it in a well-organized, color-coded format that makes it easy to:

- Monitor system health and performance
- Diagnose infrastructure issues
- Audit security configuration
- Analyze job and build statistics
- Identify optimization opportunities

## Features

- **Comprehensive Data Collection**: Gathers information about jobs, nodes, plugins, disk usage, queue, and more
- **Detailed Security Analysis**: Examines users, permissions, LDAP settings, and security configuration
- **Resource Monitoring**: Tracks hardware resource usage, executor utilization, and disk space
- **Build Intelligence**: Analyzes build durations, frequencies, and failure patterns
- **Color-coded Output**: Makes it easy to identify issues and warnings at a glance
- **Modular Design**: Select specific information to display or view a complete overview
- **Non-intrusive**: Read-only operations that don't modify your Jenkins environment

## Installation

### Prerequisites

- Python 3.6 or higher
- Access to a Jenkins server with API credentials

### Setup

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/jenkins-dashboard.git
   cd jenkins-dashboard
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

## Usage

The basic usage pattern is:

```bash
python jenkins_dashboard.py <jenkins_url> <username> <password> [OPTIONS]
```

### Examples

Display basic information overview:
```bash
python jenkins_dashboard.py https://jenkins.example.com admin password
```

Skip SSL verification (for self-signed certificates):
```bash
python jenkins_dashboard.py https://jenkins.example.com admin password --no-ssl-verify
```

Show detailed system information:
```bash
python jenkins_dashboard.py https://jenkins.example.com admin password --system
```

Display job statistics:
```bash
python jenkins_dashboard.py https://jenkins.example.com admin password --jobs
```

Show nodes and labels information:
```bash
python jenkins_dashboard.py https://jenkins.example.com admin password --nodes --labels
```

View alerts and warnings only:
```bash
python jenkins_dashboard.py https://jenkins.example.com admin password --alerts
```

Display all available information:
```bash
python jenkins_dashboard.py https://jenkins.example.com admin password --all
```

View user and permission information:
```bash
python jenkins_dashboard.py https://jenkins.example.com admin password --users
```

Check tools configuration:
```bash
python jenkins_dashboard.py https://jenkins.example.com admin password --tools
```

### Available Options

| Option | Description |
|--------|-------------|
| `--no-ssl-verify` | Disable SSL certificate verification |
| `--info` | Display basic Jenkins information |
| `--system` | Display detailed system information |
| `--jobs` | Display jobs information |
| `--nodes` | Display nodes information |
| `--plugins` | Display plugins information |
| `--queue` | Display build queue information |
| `--disk` | Display disk usage information |
| `--hardware` | Display hardware information |
| `--alerts` | Display alerts and warnings only |
| `--users` | Display users and permissions information |
| `--ldap` | Display LDAP configuration if exists |
| `--email` | Display email notification settings |
| `--tools` | Display configured build tools |
| `--notifications` | Display notification systems configuration |
| `--os` | Display OS distribution information |
| `--labels` | Display node labels information |
| `--executors` | Display executor usage information |
| `--build-stats` | Display build statistics (duration and frequency) |
| `--failed-jobs` | Display information about failing jobs |
| `--security` | Display security configuration |
| `--artifacts` | Display build artifacts information |
| `--all` | Display all information |

## Security Considerations

This tool needs Jenkins admin credentials to access all the available information. It is recommended to:

- Use the tool over a secure connection (HTTPS)
- Use an API token instead of a password when possible
- Consider creating a read-only admin account specifically for monitoring

The tool does not store or transmit credentials beyond the initial API authentication.

## Dependencies

- `requests`: For making API calls to Jenkins
- `tabulate`: For formatted table output
- `colorama`: For color-coded terminal output
- `urllib3`: For handling HTTP connections
- `re`: For regular expression pattern matching

## Project Structure

The project is organized into several modules:

- `jenkins_dashboard.py`: Main entry point and CLI interface
- `utils/`: Utility functions for formatting and API interactions
- `collectors/`: Classes that collect specific types of information from Jenkins
- `displays/`: Modules for formatting and displaying the collected information
- `login_client.py`: Handles authentication with the Jenkins server

## Extending the Dashboard

### Adding a New Collector

1. Create a new file in the `collectors/` directory
2. Extend the `BaseCollector` class
3. Implement the data collection methods
4. Add the collector to the main dashboard script

### Adding a New Display

1. Create a new file in the `displays/` directory
2. Implement the display functions
3. Add the display to the main dashboard script

## Troubleshooting

**Connection Issues**
- Ensure the Jenkins URL is correct and includes the protocol (http:// or https://)
- Check that the credentials are valid
- Try using the `--no-ssl-verify` option if you're having SSL certificate issues

**Missing Information**
- Some information may require additional Jenkins plugins
- Certain data may only be available to administrators
- Jenkins API behavior can vary between versions

**Performance Issues**
- Use specific options instead of `--all` to reduce API calls
- Jenkins instances with many jobs or nodes may be slower to respond

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- The Jenkins community for their excellent API documentation
- All contributors to this project
