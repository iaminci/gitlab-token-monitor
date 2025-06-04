#!/usr/bin/env python3
"""
GitLab Token Expiration Monitor - Main Application
Orchestrates the complete token monitoring process
"""

from config import Config
from gitlab_api import GitLabAPI
from token_analyzer import TokenAnalyzer
from email_reporter import EmailReporter

class GitLabTokenMonitor:
    def __init__(self):
        self.config = Config()
        self.gitlab_api = GitLabAPI(self.config.gitlab_url, self.config.get_headers())
        self.email_reporter = EmailReporter(self.config.smtp_config, self.config.gitlab_url, self.gitlab_api)
        self.analyzer = TokenAnalyzer()
    
    def run_monitoring(self):
        """Run the complete monitoring process"""
        print(f"Starting GitLab token expiration monitoring...")
        print(f"Checking for tokens expiring within {self.config.days_threshold} days")
        print(f"Report mode: {'All tokens' if self.config.send_all_tokens else 'Only problematic tokens'}")
        
        all_token_analysis = {
            'expired': [],
            'expiring_soon': [],
            'healthy': [],
            'no_expiration': [],
            'total_count': 0
        }
        
        # Check personal access tokens
        print("Fetching personal access tokens...")
        personal_tokens = self.gitlab_api.get_personal_access_tokens()
        personal_analysis = self.analyzer.analyze_all_tokens(personal_tokens, self.config.days_threshold)
        
        # Merge personal token analysis
        self._merge_analysis(all_token_analysis, personal_analysis)
        
        print(f"Personal Access Tokens: {personal_analysis['total_count']} total, "
              f"{len(personal_analysis['expired'])} expired, "
              f"{len(personal_analysis['expiring_soon'])} expiring soon, "
              f"{len(personal_analysis['healthy'])} healthy, "
              f"{len(personal_analysis['no_expiration'])} permanent")
        
        # Check project access tokens
        if self.config.include_project_tokens:
            project_stats = self._process_project_tokens(all_token_analysis)
            print(f"Project Access Tokens: {project_stats['total']} total, "
                  f"{project_stats['expired']} expired, "
                  f"{project_stats['expiring']} expiring soon, "
                  f"{project_stats['healthy']} healthy, "
                  f"{project_stats['permanent']} permanent")
        
        # Check group access tokens
        if self.config.include_group_tokens:
            group_stats = self._process_group_tokens(all_token_analysis)
            print(f"Group Access Tokens: {group_stats['total']} total, "
                  f"{group_stats['expired']} expired, "
                  f"{group_stats['expiring']} expiring soon, "
                  f"{group_stats['healthy']} healthy, "
                  f"{group_stats['permanent']} permanent")
        
        # Print summary and send notifications
        self._print_summary_and_notify(all_token_analysis)
    
    def _merge_analysis(self, all_analysis: dict, new_analysis: dict):
        """Merge token analysis results"""
        for category in ['expired', 'expiring_soon', 'healthy', 'no_expiration']:
            all_analysis[category].extend(new_analysis[category])
        all_analysis['total_count'] += new_analysis['total_count']
    
    def _process_project_tokens(self, all_token_analysis: dict) -> dict:
        """Process all project tokens and return statistics"""
        print("Fetching project access tokens...")
        projects = self.gitlab_api.get_all_projects()
        
        project_total = 0
        for project in projects:
            project_tokens = self.gitlab_api.get_project_access_tokens(project['id'])
            if project_tokens:
                project_analysis = self.analyzer.analyze_all_tokens(project_tokens, self.config.days_threshold)
                
                # Add project info to tokens
                for category in ['expired', 'expiring_soon', 'healthy', 'no_expiration']:
                    for token in project_analysis[category]:
                        token['project_name'] = project['name']
                        token['project_path'] = project.get('path_with_namespace', project['name'])
                
                self._merge_analysis(all_token_analysis, project_analysis)
                project_total += project_analysis['total_count']
        
        return {
            'total': project_total,
            'expired': len([t for t in all_token_analysis['expired'] if t.get('token_type') == 'project']),
            'expiring': len([t for t in all_token_analysis['expiring_soon'] if t.get('token_type') == 'project']),
            'healthy': len([t for t in all_token_analysis['healthy'] if t.get('token_type') == 'project']),
            'permanent': len([t for t in all_token_analysis['no_expiration'] if t.get('token_type') == 'project'])
        }
    
    def _process_group_tokens(self, all_token_analysis: dict) -> dict:
        """Process all group tokens and return statistics"""
        print("Fetching group access tokens...")
        groups = self.gitlab_api.get_all_groups()
        
        group_total = 0
        for group in groups:
            group_tokens = self.gitlab_api.get_group_access_tokens(group['id'])
            if group_tokens:
                group_analysis = self.analyzer.analyze_all_tokens(group_tokens, self.config.days_threshold)
                
                # Add group info to tokens
                for category in ['expired', 'expiring_soon', 'healthy', 'no_expiration']:
                    for token in group_analysis[category]:
                        token['group_name'] = group['name']
                        token['group_path'] = group.get('full_path', group['name'])
                
                self._merge_analysis(all_token_analysis, group_analysis)
                group_total += group_analysis['total_count']
        
        return {
            'total': group_total,
            'expired': len([t for t in all_token_analysis['expired'] if t.get('token_type') == 'group']),
            'expiring': len([t for t in all_token_analysis['expiring_soon'] if t.get('token_type') == 'group']),
            'healthy': len([t for t in all_token_analysis['healthy'] if t.get('token_type') == 'group']),
            'permanent': len([t for t in all_token_analysis['no_expiration'] if t.get('token_type') == 'group'])
        }
    
    def _print_summary_and_notify(self, all_token_analysis: dict):
        """Print summary statistics and send email notifications"""
        stats = self.analyzer.get_summary_stats(all_token_analysis)
        
        print(f"\n=== SUMMARY ===")
        print(f"Total tokens: {stats['total_tokens']}")
        print(f"Expired: {stats['expired_count']}")
        print(f"Expiring soon: {stats['expiring_count']}")
        print(f"Healthy: {stats['healthy_count']}")
        print(f"Permanent: {stats['permanent_count']}")
        
        # Send notifications
        if self.config.send_all_tokens or stats['problematic_count'] > 0:
            all_token_analysis['include_all_tokens'] = self.config.send_all_tokens
            print(f"\nSending email report...")
            self.email_reporter.send_notification(all_token_analysis)
        else:
            print("\nNo problematic tokens found, skipping email notification")
            print("Use SEND_ALL_TOKENS=true to receive reports even when all tokens are healthy")
        
        print("Monitoring complete!")

def main():
    """Main entry point"""
    print("GitLab Token Monitor Starting...")
    
    try:
        print("Loading configuration...")
        monitor = GitLabTokenMonitor()
        print("Configuration loaded successfully!")
        
        print("Starting monitoring process...")
        monitor.run_monitoring()
        
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user")
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all required files are in the same directory:")
        print("- config.py")
        print("- gitlab_api.py") 
        print("- token_analyzer.py")
        print("- email_reporter.py")
    except Exception as e:
        print(f"Error during monitoring: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()