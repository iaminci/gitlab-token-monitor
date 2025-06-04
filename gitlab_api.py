#!/usr/bin/env python3
"""
GitLab API Client
Handles all GitLab API interactions for token management
"""

import requests
from typing import List, Dict, Optional

class GitLabAPI:
    def __init__(self, gitlab_url: str, headers: Dict[str, str]):
        self.gitlab_url = gitlab_url.rstrip('/')
        self.headers = headers
    
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