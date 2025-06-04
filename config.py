#!/usr/bin/env python3
"""
GitLab Token Monitor Configuration
Handles environment variables and configuration settings
"""

import os
import sys
from typing import Dict, List

class Config:
    def __init__(self):
        self.gitlab_url = os.getenv('GITLAB_URL', 'https://your-gitlab.com')
        self.admin_token = os.getenv('GITLAB_ADMIN_TOKEN', 'your-admin-token')
        
        # SMTP Configuration
        self.smtp_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '465')),  # SSL port
            'from_email': os.getenv('FROM_EMAIL', 'alerts@yourcompany.com'),
            'to_emails': os.getenv('TO_EMAILS', 'admin@yourcompany.com').split(','),
            'username': os.getenv('SMTP_USERNAME'),
            'password': os.getenv('SMTP_PASSWORD'),
            'use_ssl': os.getenv('SMTP_USE_SSL', 'true').lower() == 'true',
            'use_tls': os.getenv('SMTP_USE_TLS', 'false').lower() == 'true'
        }
        
        # Monitoring Configuration
        self.days_threshold = int(os.getenv('DAYS_THRESHOLD', '7'))
        self.include_project_tokens = os.getenv('INCLUDE_PROJECT_TOKENS', 'true').lower() == 'true'
        self.include_group_tokens = os.getenv('INCLUDE_GROUP_TOKENS', 'true').lower() == 'true'
        self.send_all_tokens = os.getenv('SEND_ALL_TOKENS', 'false').lower() == 'true'
        
        # Validate required configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration"""
        print(f"Validating configuration...")
        print(f"GitLab URL: {self.gitlab_url}")
        print(f"Admin Token: {'Set' if self.admin_token and self.admin_token != 'your-admin-token' else 'NOT SET'}")
        print(f"From Email: {self.smtp_config['from_email']}")
        print(f"To Emails: {self.smtp_config['to_emails']}")
        
        if not self.admin_token or self.admin_token == 'your-admin-token':
            print("❌ Error: GITLAB_ADMIN_TOKEN environment variable is required")
            print("Set it with: export GITLAB_ADMIN_TOKEN='your-token-here'")
            sys.exit(1)
        
        if not self.smtp_config['from_email'] or self.smtp_config['from_email'] == 'alerts@yourcompany.com':
            print("❌ Error: FROM_EMAIL environment variable is required")
            print("Set it with: export FROM_EMAIL='your-email@company.com'")
            sys.exit(1)
            
        print("✅ Configuration validation passed!")
    
    def get_headers(self) -> Dict[str, str]:
        """Get GitLab API headers"""
        return {
            'PRIVATE-TOKEN': self.admin_token,
            'Content-Type': 'application/json'
        }