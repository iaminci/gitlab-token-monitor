#!/usr/bin/env python3
"""
Email Reporter
Handles email notifications and HTML report generation
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
from token_analyzer import TokenAnalyzer

class EmailReporter:
    def __init__(self, smtp_config: Dict, gitlab_url: str, gitlab_api):
        self.smtp_config = smtp_config
        self.gitlab_url = gitlab_url
        self.gitlab_api = gitlab_api
    
    def send_notification(self, token_analysis: Dict):
        """Send email notification about all tokens with their status"""
        stats = TokenAnalyzer.get_summary_stats(token_analysis)
        
        # Check if we should send email
        if not token_analysis.get('include_all_tokens', False) and stats['problematic_count'] == 0:
            print("No expiring tokens found, skipping email notification")
            return
            
        # Create email content
        if stats['problematic_count'] > 0:
            subject = f"GitLab Token Report - {stats['problematic_count']}/{stats['total_tokens']} tokens need attention"
        else:
            subject = f"GitLab Token Report - All {stats['total_tokens']} tokens are healthy"
        
        body = self._create_comprehensive_email_body(token_analysis)
        
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
    
    def _create_comprehensive_email_body(self, token_analysis: Dict) -> str:
        """Create comprehensive HTML email body with all token information"""
        
        # Group tokens by type for each category
        expired_by_type = TokenAnalyzer.group_tokens_by_type(token_analysis['expired'])
        expiring_by_type = TokenAnalyzer.group_tokens_by_type(token_analysis['expiring_soon'])
        healthy_by_type = TokenAnalyzer.group_tokens_by_type(token_analysis['healthy'])
        no_exp_by_type = TokenAnalyzer.group_tokens_by_type(token_analysis['no_expiration'])
        
        stats = TokenAnalyzer.get_summary_stats(token_analysis)
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .summary h3 {{ margin-top: 0; color: #333; }}
                .stats {{ display: flex; gap: 20px; flex-wrap: wrap; }}
                .stat-box {{ background: white; padding: 10px; border-radius: 5px; border-left: 4px solid #007bff; min-width: 120px; }}
                .stat-number {{ font-size: 24px; font-weight: bold; color: #333; }}
                .stat-label {{ color: #666; font-size: 14px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; font-weight: bold; }}
                .expired {{ color: red; font-weight: bold; }}
                .expiring {{ color: orange; font-weight: bold; }}
                .healthy {{ color: green; }}
                .no-expiration {{ color: blue; }}
                .section {{ margin: 30px 0; }}
                .section h3 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 5px; }}
                .token-type {{ margin: 20px 0; }}
                .token-type h4 {{ color: #555; margin: 15px 0 10px 0; }}
                .collapsible {{ margin: 10px 0; }}
                .collapsible summary {{ cursor: pointer; font-weight: bold; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
                .collapsible[open] summary {{ background: #e9ecef; }}
            </style>
        </head>
        <body>
            <h2>GitLab Token Comprehensive Report</h2>
            
            <div class="summary">
                <h3>Token Status Summary</h3>
                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-number">{stats['total_tokens']}</div>
                        <div class="stat-label">Total Tokens</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number expired">{stats['expired_count']}</div>
                        <div class="stat-label">Expired</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number expiring">{stats['expiring_count']}</div>
                        <div class="stat-label">Expiring Soon</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number healthy">{stats['healthy_count']}</div>
                        <div class="stat-label">Healthy</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number no-expiration">{stats['permanent_count']}</div>
                        <div class="stat-label">No Expiration</div>
                    </div>
                </div>
            </div>
        """
        
        # Critical tokens (expired + expiring soon)
        if stats['expired_count'] > 0 or stats['expiring_count'] > 0:
            html += '<div class="section"><h3>🚨 Tokens Requiring Immediate Attention</h3>'
            
            if stats['expired_count'] > 0:
                html += '<h4 class="expired">Expired Tokens</h4>'
                for token_type in ['personal', 'project', 'group']:
                    if expired_by_type[token_type]:
                        html += f'<h5>{token_type.title()} Access Tokens</h5>'
                        html += self._create_token_table(expired_by_type[token_type], token_type, 'expired')
            
            if stats['expiring_count'] > 0:
                html += '<h4 class="expiring">Expiring Soon</h4>'
                for token_type in ['personal', 'project', 'group']:
                    if expiring_by_type[token_type]:
                        html += f'<h5>{token_type.title()} Access Tokens</h5>'
                        html += self._create_token_table(expiring_by_type[token_type], token_type, 'expiring')
            
            html += '</div>'
        
        # Healthy tokens (collapsible)
        if stats['healthy_count'] > 0:
            html += f'''
            <div class="section">
                <details class="collapsible">
                    <summary>✅ Healthy Tokens ({stats['healthy_count']})</summary>
                    <div class="token-type">
            '''
            
            for token_type in ['personal', 'project', 'group']:
                if healthy_by_type[token_type]:
                    html += f'<h4>{token_type.title()} Access Tokens</h4>'
                    html += self._create_token_table(healthy_by_type[token_type], token_type, 'healthy')
            
            html += '</div></details></div>'
        
        # No expiration tokens (collapsible)
        if stats['permanent_count'] > 0:
            html += f'''
            <div class="section">
                <details class="collapsible">
                    <summary>♾️ Tokens with No Expiration ({stats['permanent_count']})</summary>
                    <div class="token-type">
            '''
            
            for token_type in ['personal', 'project', 'group']:
                if no_exp_by_type[token_type]:
                    html += f'<h4>{token_type.title()} Access Tokens</h4>'
                    html += self._create_token_table(no_exp_by_type[token_type], token_type, 'no-expiration')
            
            html += '</div></details></div>'
        
        html += f"""
            <div class="section">
                <h3>Next Steps</h3>
                <p><strong>For Expired/Expiring Tokens:</strong></p>
                <ul>
                    <li>Review and renew tokens before they expire to avoid service interruptions</li>
                    <li>Consider setting longer expiration periods for critical service tokens</li>
                    <li>Update any automated systems using these tokens</li>
                </ul>
                
                <p><strong>Token Management:</strong></p>
                <ul>
                    <li><a href="{self.gitlab_url}/profile/personal_access_tokens">Personal Access Tokens</a></li>
                    <li><a href="{self.gitlab_url}/admin/application_settings/general#js-access-token-settings">Admin Token Settings</a></li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_token_table(self, tokens: List[Dict], token_type: str, status_class: str = "") -> str:
        """Create HTML table for tokens"""
        if not tokens:
            return "<p><em>No tokens in this category</em></p>"
            
        if token_type == 'personal':
            headers = ['Token Name', 'User', 'Email', 'Expires At', 'Status', 'Days Until Expiry', 'Scopes']
            table_html = f'<table><tr>{"".join(f"<th>{h}</th>" for h in headers)}</tr>'
            
            for token in tokens:
                user_info = self.gitlab_api.get_user_info(token['user_id']) if token.get('user_id') else {}
                username = user_info.get('username', 'Unknown') if user_info else 'Unknown'
                email = user_info.get('email', 'Unknown') if user_info else 'Unknown'
                
                table_html += f"""
                <tr>
                    <td>{token.get('name', 'Unnamed')}</td>
                    <td>{username}</td>
                    <td>{email}</td>
                    <td>{token.get('expires_at', 'Never')}</td>
                    <td class="{status_class}">{token.get('status', 'Unknown')}</td>
                    <td class="{status_class}">{token['days_until_expiry']}</td>
                    <td>{', '.join(token.get('scopes', []))}</td>
                </tr>
                """
                
        elif token_type == 'project':
            headers = ['Token Name', 'Project', 'Project Path', 'Expires At', 'Status', 'Days Until Expiry', 'Access Level']
            table_html = f'<table><tr>{"".join(f"<th>{h}</th>" for h in headers)}</tr>'
            
            for token in tokens:
                table_html += f"""
                <tr>
                    <td>{token.get('name', 'Unnamed')}</td>
                    <td>{token.get('project_name', 'Unknown')}</td>
                    <td>{token.get('project_path', 'Unknown')}</td>
                    <td>{token.get('expires_at', 'Never')}</td>
                    <td class="{status_class}">{token.get('status', 'Unknown')}</td>
                    <td class="{status_class}">{token['days_until_expiry']}</td>
                    <td>{token.get('access_level', 'Unknown')}</td>
                </tr>
                """
                
        elif token_type == 'group':
            headers = ['Token Name', 'Group', 'Group Path', 'Expires At', 'Status', 'Days Until Expiry', 'Access Level', 'Scopes']
            table_html = f'<table><tr>{"".join(f"<th>{h}</th>" for h in headers)}</tr>'
            
            for token in tokens:
                group_info = self.gitlab_api.get_group_info(token['group_id']) if token.get('group_id') else {}
                group_name = group_info.get('name', 'Unknown') if group_info else 'Unknown'
                group_path = group_info.get('full_path', 'Unknown') if group_info else 'Unknown'
                
                table_html += f"""
                <tr>
                    <td>{token.get('name', 'Unnamed')}</td>
                    <td>{group_name}</td>
                    <td>{group_path}</td>
                    <td>{token.get('expires_at', 'Never')}</td>
                    <td class="{status_class}">{token.get('status', 'Unknown')}</td>
                    <td class="{status_class}">{token['days_until_expiry']}</td>
                    <td>{token.get('access_level', 'Unknown')}</td>
                    <td>{', '.join(token.get('scopes', []))}</td>
                </tr>
                """
        
        table_html += '</table>'
        return table_html