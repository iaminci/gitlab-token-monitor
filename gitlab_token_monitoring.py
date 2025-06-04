#!/usr/bin/env python3
"""
GitLab Token Expiration Monitor
Monitors personal access tokens and project access tokens for expiration
Sends email notifications for tokens expiring within specified days
"""

import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import sys
import os
from typing import List, Dict, Optional

class GitLabTokenMonitor:
    def __init__(self, gitlab_url: str, admin_token: str, smtp_config: Dict):
        self.gitlab_url = gitlab_url.rstrip('/')
        self.admin_token = admin_token
        self.smtp_config = smtp_config
        self.headers = {
            'PRIVATE-TOKEN': admin_token,
            'Content-Type': 'application/json'
        }
    
    def get_personal_access_tokens(self) -> List[Dict]:
        """Get all personal access tokens from GitLab"""
        url = f"{self.gitlab_url}/api/v4/personal_access_tokens"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching personal access tokens: {e}")
            return []
    
    def get_project_access_tokens(self, project_id: int) -> List[Dict]:
        """Get project access tokens for a specific project"""
        url = f"{self.gitlab_url}/api/v4/projects/{project_id}/access_tokens"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            tokens = response.json()
            # Add token type for identification
            for token in tokens:
                token['token_type'] = 'project'
                token['project_id'] = project_id
            return tokens
        except requests.exceptions.RequestException as e:
            print(f"Error fetching project access tokens for project {project_id}: {e}")
            return []
    
    def get_group_access_tokens(self, group_id: int) -> List[Dict]:
        """Get group access tokens for a specific group"""
        url = f"{self.gitlab_url}/api/v4/groups/{group_id}/access_tokens"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            tokens = response.json()
            # Add token type for identification
            for token in tokens:
                token['token_type'] = 'group'
                token['group_id'] = group_id
            return tokens
        except requests.exceptions.RequestException as e:
            print(f"Error fetching group access tokens for group {group_id}: {e}")
            return []
    
    def get_all_groups(self) -> List[Dict]:
        """Get all groups in GitLab instance"""
        url = f"{self.gitlab_url}/api/v4/groups"
        params = {'simple': 'true', 'per_page': 100, 'all_available': 'true'}
        groups = []
        page = 1
        
        try:
            while True:
                params['page'] = page
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                page_groups = response.json()
                if not page_groups:
                    break
                    
                groups.extend(page_groups)
                page += 1
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching groups: {e}")
            
        return groups
    
    def get_all_projects(self) -> List[Dict]:
        """Get all projects in GitLab instance"""
        url = f"{self.gitlab_url}/api/v4/projects"
        params = {'simple': 'true', 'per_page': 100}
        projects = []
        page = 1
        
        try:
            while True:
                params['page'] = page
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                page_projects = response.json()
                if not page_projects:
                    break
                    
                projects.extend(page_projects)
                page += 1
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching projects: {e}")
            
        return projects
    
    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """Get user information by ID"""
        url = f"{self.gitlab_url}/api/v4/users/{user_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching user info for ID {user_id}: {e}")
            return None
    
    def get_group_info(self, group_id: int) -> Optional[Dict]:
        """Get group information by ID"""
        url = f"{self.gitlab_url}/api/v4/groups/{group_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching group info for ID {group_id}: {e}")
            return None
        """Get user information by ID"""
        url = f"{self.gitlab_url}/api/v4/users/{user_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching user info for ID {user_id}: {e}")
            return None
    
    def check_token_expiration(self, tokens: List[Dict], days_threshold: int = 7) -> List[Dict]:
        """Check which tokens are expiring within the threshold"""
        expiring_tokens = []
        threshold_date = datetime.now() + timedelta(days=days_threshold)
        
        for token in tokens:
            if not token.get('expires_at'):
                continue  # Token doesn't expire
                
            try:
                expires_at = datetime.fromisoformat(token['expires_at'].replace('Z', '+00:00'))
                # Convert to naive datetime for comparison
                expires_at = expires_at.replace(tzinfo=None)
                
                if expires_at <= threshold_date:
                    days_until_expiry = (expires_at - datetime.now()).days
                    token['days_until_expiry'] = days_until_expiry
                    expiring_tokens.append(token)
                    
            except ValueError as e:
                print(f"Error parsing date for token {token.get('name', 'unknown')}: {e}")
                
        return expiring_tokens
    
    def send_email_notification(self, expiring_tokens: List[Dict]):
        """Send email notification about expiring tokens"""
        if not expiring_tokens:
            return
            
        # Group tokens by type
        personal_tokens = [t for t in expiring_tokens if t.get('user_id') and not t.get('token_type')]
        project_tokens = [t for t in expiring_tokens if t.get('token_type') == 'project']
        group_tokens = [t for t in expiring_tokens if t.get('token_type') == 'group']
        
        # Create email content
        subject = f"GitLab Token Expiration Alert - {len(expiring_tokens)} tokens expiring"
        
        body = self._create_email_body(personal_tokens, project_tokens, group_tokens)
        
        # Send email
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['from_email']
            msg['To'] = ', '.join(self.smtp_config['to_emails'])
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            if self.smtp_config.get('use_ssl', True):
                server = smtplib.SMTP_SSL(self.smtp_config['smtp_server'], self.smtp_config['smtp_port'])
            else:
                server = smtplib.SMTP(self.smtp_config['smtp_server'], self.smtp_config['smtp_port'])
                if self.smtp_config.get('use_tls'):
                    server.starttls()
            
            if self.smtp_config.get('username'):
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                
            server.send_message(msg)
            server.quit()
            
            print(f"Email notification sent successfully to {', '.join(self.smtp_config['to_emails'])}")
            
        except Exception as e:
            print(f"Error sending email: {e}")
    
    def _create_email_body(self, personal_tokens: List[Dict], project_tokens: List[Dict], group_tokens: List[Dict]) -> str:
        """Create HTML email body"""
        html = """
        <html>
        <head>
            <style>
                table { border-collapse: collapse; width: 100%; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .expired { color: red; font-weight: bold; }
                .warning { color: orange; font-weight: bold; }
            </style>
        </head>
        <body>
            <h2>GitLab Token Expiration Alert</h2>
            <p>The following tokens are expiring soon or have already expired:</p>
        """
        
        if personal_tokens:
            html += "<h3>Personal Access Tokens</h3>"
            html += """
            <table>
                <tr>
                    <th>Token Name</th>
                    <th>User</th>
                    <th>Email</th>
                    <th>Expires At</th>
                    <th>Days Until Expiry</th>
                    <th>Scopes</th>
                </tr>
            """
            
            for token in personal_tokens:
                user_info = self.get_user_info(token['user_id']) if token.get('user_id') else {}
                username = user_info.get('username', 'Unknown') if user_info else 'Unknown'
                email = user_info.get('email', 'Unknown') if user_info else 'Unknown'
                
                status_class = 'expired' if token['days_until_expiry'] < 0 else 'warning'
                
                html += f"""
                <tr>
                    <td>{token.get('name', 'Unnamed')}</td>
                    <td>{username}</td>
                    <td>{email}</td>
                    <td>{token.get('expires_at', 'Unknown')}</td>
                    <td class="{status_class}">{token['days_until_expiry']}</td>
                    <td>{', '.join(token.get('scopes', []))}</td>
                </tr>
                """
            
            html += "</table>"
        
        if group_tokens:
            html += "<h3>Group Access Tokens</h3>"
            html += """
            <table>
                <tr>
                    <th>Token Name</th>
                    <th>Group</th>
                    <th>Group Path</th>
                    <th>Expires At</th>
                    <th>Days Until Expiry</th>
                    <th>Access Level</th>
                    <th>Scopes</th>
                </tr>
            """
            
            for token in group_tokens:
                group_info = self.get_group_info(token['group_id']) if token.get('group_id') else {}
                group_name = group_info.get('name', 'Unknown') if group_info else 'Unknown'
                group_path = group_info.get('full_path', 'Unknown') if group_info else 'Unknown'
                
                status_class = 'expired' if token['days_until_expiry'] < 0 else 'warning'
                
                html += f"""
                <tr>
                    <td>{token.get('name', 'Unnamed')}</td>
                    <td>{group_name}</td>
                    <td>{group_path}</td>
                    <td>{token.get('expires_at', 'Unknown')}</td>
                    <td class="{status_class}">{token['days_until_expiry']}</td>
                    <td>{token.get('access_level', 'Unknown')}</td>
                    <td>{', '.join(token.get('scopes', []))}</td>
                </tr>
                """
            
            html += "</table>"
        
        if project_tokens:
            html += "<h3>Project Access Tokens</h3>"
            html += """
            <table>
                <tr>
                    <th>Token Name</th>
                    <th>Project ID</th>
                    <th>Expires At</th>
                    <th>Days Until Expiry</th>
                    <th>Access Level</th>
                </tr>
            """
            
            for token in project_tokens:
                status_class = 'expired' if token['days_until_expiry'] < 0 else 'warning'
                
                html += f"""
                <tr>
                    <td>{token.get('name', 'Unnamed')}</td>
                    <td>{token.get('project_id', 'Unknown')}</td>
                    <td>{token.get('expires_at', 'Unknown')}</td>
                    <td class="{status_class}">{token['days_until_expiry']}</td>
                    <td>{token.get('access_level', 'Unknown')}</td>
                </tr>
                """
            
            html += "</table>"
        
        html += """
            <p><strong>Action Required:</strong> Please review and renew these tokens before they expire to avoid service interruptions.</p>
            <p>You can manage your tokens in GitLab at:</p>
            <ul>
                <li><a href="{0}/profile/personal_access_tokens">Personal Access Tokens</a></li>
                <li><a href="{0}/admin/application_settings/general#js-access-token-settings">Admin Token Settings</a></li>
            </ul>
        </body>
        </html>
        """.format(self.gitlab_url)
        
        return html
    
    def run_monitoring(self, days_threshold: int = 7, include_project_tokens: bool = True, include_group_tokens: bool = True):
        """Run the complete monitoring process"""
        print(f"Starting GitLab token expiration monitoring...")
        print(f"Checking for tokens expiring within {days_threshold} days")
        
        all_expiring_tokens = []
        
        # Check personal access tokens
        print("Fetching personal access tokens...")
        personal_tokens = self.get_personal_access_tokens()
        expiring_personal = self.check_token_expiration(personal_tokens, days_threshold)
        all_expiring_tokens.extend(expiring_personal)
        
        print(f"Found {len(expiring_personal)} expiring personal access tokens")
        
        # Check project access tokens
        if include_project_tokens:
            print("Fetching project access tokens...")
            projects = self.get_all_projects()
            
            for project in projects:
                project_tokens = self.get_project_access_tokens(project['id'])
                expiring_project = self.check_token_expiration(project_tokens, days_threshold)
                
                # Add project info to tokens
                for token in expiring_project:
                    token['project_name'] = project['name']
                    token['project_path'] = project.get('path_with_namespace', project['name'])
                
                all_expiring_tokens.extend(expiring_project)
            
            project_token_count = len([t for t in all_expiring_tokens if t.get('token_type') == 'project'])
            print(f"Found {project_token_count} expiring project access tokens")
        
        # Check group access tokens
        if include_group_tokens:
            print("Fetching group access tokens...")
            groups = self.get_all_groups()
            
            for group in groups:
                group_tokens = self.get_group_access_tokens(group['id'])
                expiring_group = self.check_token_expiration(group_tokens, days_threshold)
                
                # Add group info to tokens
                for token in expiring_group:
                    token['group_name'] = group['name']
                    token['group_path'] = group.get('full_path', group['name'])
                
                all_expiring_tokens.extend(expiring_group)
            
            group_token_count = len([t for t in all_expiring_tokens if t.get('token_type') == 'group'])
            print(f"Found {group_token_count} expiring group access tokens")
        
        # Send notifications
        if all_expiring_tokens:
            print(f"Total expiring tokens: {len(all_expiring_tokens)}")
            self.send_email_notification(all_expiring_tokens)
        else:
            print("No expiring tokens found")
        
        print("Monitoring complete!")


def main():
    # Configuration
    config = {
        'gitlab_url': os.getenv('GITLAB_URL', 'https://your-gitlab.com'),
        'admin_token': os.getenv('GITLAB_ADMIN_TOKEN', 'your-admin-token'),
        'smtp_config': {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '465')),  # SSL port
            'from_email': os.getenv('FROM_EMAIL', 'alerts@yourcompany.com'),
            'to_emails': os.getenv('TO_EMAILS', 'admin@yourcompany.com').split(','),
            'username': os.getenv('SMTP_USERNAME'),
            'password': os.getenv('SMTP_PASSWORD'),
            'use_ssl': os.getenv('SMTP_USE_SSL', 'true').lower() == 'true',
            'use_tls': os.getenv('SMTP_USE_TLS', 'false').lower() == 'true'
        },
        'days_threshold': int(os.getenv('DAYS_THRESHOLD', '7')),
        'include_project_tokens': os.getenv('INCLUDE_PROJECT_TOKENS', 'true').lower() == 'true',
        'include_group_tokens': os.getenv('INCLUDE_GROUP_TOKENS', 'true').lower() == 'true'
    }
    
    # Validate required config
    if not config['admin_token'] or config['admin_token'] == 'your-admin-token':
        print("Error: GITLAB_ADMIN_TOKEN environment variable is required")
        sys.exit(1)
    
    if not config['smtp_config']['from_email'] or config['smtp_config']['from_email'] == 'alerts@yourcompany.com':
        print("Error: FROM_EMAIL environment variable is required")
        sys.exit(1)
    
    # Initialize and run monitor
    monitor = GitLabTokenMonitor(
        config['gitlab_url'],
        config['admin_token'],
        config['smtp_config']
    )
    
    monitor.run_monitoring(
        config['days_threshold'],
        config['include_project_tokens'],
        config['include_group_tokens']
    )


if __name__ == "__main__":
    main()