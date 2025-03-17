#!/usr/bin/env python3
"""
Jenkins Tools Collector
This module collects information about tools configured in Jenkins.
"""

import re
from collectors.base_collector import BaseCollector

class JenkinsToolsCollector(BaseCollector):
    """Collects information about tools configured in Jenkins"""

    def get_tools_info(self):
        """
        Fetches information about configured tools in Jenkins

        Returns:
            dict: Tools information
        """
        try:
            # Access global tool configuration page
            response = self.fetch_jenkins_data("configureTools")
            if "error" in response:
                # Try alternative path
                response = self.fetch_jenkins_data("configure")
                if "error" in response:
                    return {"error": "Could not access tools configuration"}

            html = response.get("content", "")

            # Initialize tools dictionary
            tools_info = {
                'jdk': [],
                'git': [],
                'maven': [],
                'ant': [],
                'gradle': [],
                'docker': [],
                'nodejs': [],
                'sonarqube': [],
                'other': []
            }

            # Check for JDK installations
            tools_info['jdk'] = self._extract_jdk_tools(html)

            # Check for Git installations
            tools_info['git'] = self._extract_git_tools(html)

            # Check for Maven installations
            tools_info['maven'] = self._extract_maven_tools(html)

            # Check for Ant installations
            tools_info['ant'] = self._extract_ant_tools(html)

            # Check for Gradle installations
            tools_info['gradle'] = self._extract_gradle_tools(html)

            # Check for Docker installations
            tools_info['docker'] = self._extract_docker_tools(html)

            # Check for NodeJS installations
            tools_info['nodejs'] = self._extract_nodejs_tools(html)

            # Check for SonarQube scanner installations
            tools_info['sonarqube'] = self._extract_sonar_tools(html)

            # Add total count
            total_tools = sum(len(tools) for tools in tools_info.values())
            tools_info['total_tools'] = total_tools

            # Check if auto-installation is used
            tools_info['uses_auto_install'] = 'Install automatically' in html

            # Try to get common usage
            tools_info['tool_usage'] = self._get_tool_usage()

            return tools_info

        except Exception as e:
            return {"error": f"Error retrieving tools information: {str(e)}"}

    def _extract_jdk_tools(self, html):
        """
        Extract JDK installations from HTML

        Args:
            html: HTML content

        Returns:
            list: JDK installations
        """
        jdk_tools = []

        # Look for JDK section
        if 'JDK installations' in html:
            # Extract JDK names and paths
            jdk_name_pattern = r'JDK installations.*?name="?.*?name"?.*?value="(.*?)"'
            jdk_names = re.findall(jdk_name_pattern, html, re.DOTALL)

            jdk_home_pattern = r'JDK installations.*?home.*?value="(.*?)"'
            jdk_homes = re.findall(jdk_home_pattern, html, re.DOTALL)

            # Extract auto-install info - typically a version like "jdk-8u121-oth-JPR"
            jdk_auto_pattern = r'JDK installations.*?jdk-\d+u\d+-oth-JPR'
            jdk_auto = re.findall(jdk_auto_pattern, html, re.DOTALL)

            # Process JDK tools
            for i, name in enumerate(jdk_names):
                jdk_info = {
                    'name': name,
                    'type': 'JDK',
                    'auto_install': len(jdk_auto) > i and jdk_auto[i]
                }

                # Add home if available
                if i < len(jdk_homes):
                    jdk_info['path'] = jdk_homes[i]

                jdk_tools.append(jdk_info)

        return jdk_tools

    def _extract_git_tools(self, html):
        """
        Extract Git installations from HTML

        Args:
            html: HTML content

        Returns:
            list: Git installations
        """
        git_tools = []

        # Look for Git section
        if 'Git installations' in html:
            # Extract Git names and paths
            git_name_pattern = r'Git installations.*?name="?.*?name"?.*?value="(.*?)"'
            git_names = re.findall(git_name_pattern, html, re.DOTALL)

            git_path_pattern = r'Git installations.*?home.*?value="(.*?)"'
            git_paths = re.findall(git_path_pattern, html, re.DOTALL)

            # Process Git tools
            for i, name in enumerate(git_names):
                git_info = {
                    'name': name,
                    'type': 'Git'
                }

                # Add path if available
                if i < len(git_paths):
                    git_info['path'] = git_paths[i]

                git_tools.append(git_info)

        return git_tools

    def _extract_maven_tools(self, html):
        """
        Extract Maven installations from HTML

        Args:
            html: HTML content

        Returns:
            list: Maven installations
        """
        maven_tools = []

        # Look for Maven section
        if 'Maven installations' in html:
            # Extract Maven names and paths
            maven_name_pattern = r'Maven installations.*?name="?.*?name"?.*?value="(.*?)"'
            maven_names = re.findall(maven_name_pattern, html, re.DOTALL)

            maven_path_pattern = r'Maven installations.*?home.*?value="(.*?)"'
            maven_paths = re.findall(maven_path_pattern, html, re.DOTALL)

            # Extract auto-install versions
            maven_auto_pattern = r'Maven installations.*?id="[^"]*" value="([\d\.]+)"'
            maven_versions = re.findall(maven_auto_pattern, html, re.DOTALL)

            # Process Maven tools
            for i, name in enumerate(maven_names):
                maven_info = {
                    'name': name,
                    'type': 'Maven',
                    'auto_install': i < len(maven_versions)
                }

                # Add path if available
                if i < len(maven_paths):
                    maven_info['path'] = maven_paths[i]

                # Add version if auto-install
                if i < len(maven_versions):
                    maven_info['version'] = maven_versions[i]

                maven_tools.append(maven_info)

        return maven_tools

    def _extract_ant_tools(self, html):
        """
        Extract Ant installations from HTML

        Args:
            html: HTML content

        Returns:
            list: Ant installations
        """
        ant_tools = []

        # Look for Ant section
        if 'Ant installations' in html:
            # Extract Ant names and paths
            ant_name_pattern = r'Ant installations.*?name="?.*?name"?.*?value="(.*?)"'
            ant_names = re.findall(ant_name_pattern, html, re.DOTALL)

            ant_path_pattern = r'Ant installations.*?home.*?value="(.*?)"'
            ant_paths = re.findall(ant_path_pattern, html, re.DOTALL)

            # Process Ant tools
            for i, name in enumerate(ant_names):
                ant_info = {
                    'name': name,
                    'type': 'Ant'
                }

                # Add path if available
                if i < len(ant_paths):
                    ant_info['path'] = ant_paths[i]

                ant_tools.append(ant_info)

        return ant_tools

    def _extract_gradle_tools(self, html):
        """
        Extract Gradle installations from HTML

        Args:
            html: HTML content

        Returns:
            list: Gradle installations
        """
        gradle_tools = []

        # Look for Gradle section
        if 'Gradle installations' in html:
            # Extract Gradle names and paths
            gradle_name_pattern = r'Gradle installations.*?name="?.*?name"?.*?value="(.*?)"'
            gradle_names = re.findall(gradle_name_pattern, html, re.DOTALL)

            gradle_path_pattern = r'Gradle installations.*?home.*?value="(.*?)"'
            gradle_paths = re.findall(gradle_path_pattern, html, re.DOTALL)

            # Process Gradle tools
            for i, name in enumerate(gradle_names):
                gradle_info = {
                    'name': name,
                    'type': 'Gradle'
                }

                # Add path if available
                if i < len(gradle_paths):
                    gradle_info['path'] = gradle_paths[i]

                gradle_tools.append(gradle_info)

        return gradle_tools

    def _extract_docker_tools(self, html):
        """
        Extract Docker installations from HTML

        Args:
            html: HTML content

        Returns:
            list: Docker installations
        """
        docker_tools = []

        # Look for Docker section
        if 'Docker' in html:
            # Extract Docker installations
            docker_name_pattern = r'Docker.*?name="?.*?name"?.*?value="(.*?)"'
            docker_names = re.findall(docker_name_pattern, html, re.DOTALL)

            # Process Docker tools
            for name in docker_names:
                docker_tools.append({
                    'name': name,
                    'type': 'Docker'
                })

        return docker_tools

    def _extract_nodejs_tools(self, html):
        """
        Extract NodeJS installations from HTML

        Args:
            html: HTML content

        Returns:
            list: NodeJS installations
        """
        nodejs_tools = []

        # Look for NodeJS section
        if 'NodeJS' in html or 'Node.js' in html:
            # Extract NodeJS names and paths
            nodejs_name_pattern = r'NodeJS.*?name="?.*?name"?.*?value="(.*?)"'
            nodejs_names = re.findall(nodejs_name_pattern, html, re.DOTALL)

            # Process NodeJS tools
            for name in nodejs_names:
                nodejs_tools.append({
                    'name': name,
                    'type': 'NodeJS'
                })

        return nodejs_tools

    def _extract_sonar_tools(self, html):
        """
        Extract SonarQube scanner installations from HTML

        Args:
            html: HTML content

        Returns:
            list: SonarQube scanner installations
        """
        sonar_tools = []

        # Look for SonarQube section
        if 'SonarQube' in html:
            # Extract SonarQube scanner names and paths
            sonar_name_pattern = r'SonarQube.*?name="?.*?name"?.*?value="(.*?)"'
            sonar_names = re.findall(sonar_name_pattern, html, re.DOTALL)

            # Process SonarQube tools
            for name in sonar_names:
                sonar_tools.append({
                    'name': name,
                    'type': 'SonarQube Scanner'
                })

        return sonar_tools

    def _get_tool_usage(self):
        """
        Try to determine which tools are used in jobs

        Returns:
            dict: Tool usage statistics
        """
        tool_usage = {}

        try:
            # Get a sample of jobs
            response = self.fetch_jenkins_data("api/json", params={"tree": "jobs[name,url]"})
            if "error" in response:
                return {}

            jobs = response.get('jobs', [])

            # Check a sample of jobs for tool usage
            for job in jobs[:20]:  # Limit to 20 jobs for performance
                job_url = job.get('url', '')
                job_name = job.get('name', 'Unknown')

                if not job_url:
                    continue

                # Get job config
                try:
                    response = self.fetch_jenkins_data(f"{job_url}config.xml")
                    if "error" not in response and "html" in response:
                        config = response["content"]

                        # Check for tool usage in the config
                        if 'jdk' in config.lower():
                            tool_usage.setdefault('jdk', []).append(job_name)

                        if 'git' in config.lower():
                            tool_usage.setdefault('git', []).append(job_name)

                        if 'maven' in config.lower():
                            tool_usage.setdefault('maven', []).append(job_name)

                        if 'ant' in config.lower():
                            tool_usage.setdefault('ant', []).append(job_name)

                        if 'gradle' in config.lower():
                            tool_usage.setdefault('gradle', []).append(job_name)

                        if 'docker' in config.lower():
                            tool_usage.setdefault('docker', []).append(job_name)

                        if 'nodejs' in config.lower() or 'node.js' in config.lower():
                            tool_usage.setdefault('nodejs', []).append(job_name)

                        if 'sonar' in config.lower():
                            tool_usage.setdefault('sonarqube', []).append(job_name)
                except Exception:
                    continue

            # Limit job lists to 5 examples
            for tool_type, jobs in tool_usage.items():
                tool_usage[tool_type] = jobs[:5]

            return tool_usage

        except Exception:
            return {}
