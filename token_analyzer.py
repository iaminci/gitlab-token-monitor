#!/usr/bin/env python3
"""
Token Analyzer
Handles token expiration analysis and categorization
"""

from datetime import datetime, timedelta
from typing import List, Dict

class TokenAnalyzer:
    @staticmethod
    def analyze_all_tokens(tokens: List[Dict], days_threshold: int = 7) -> Dict:
        """Analyze all tokens and categorize them by expiration status"""
        result = {
            'expiring_soon': [],
            'expired': [],
            'healthy': [],
            'no_expiration': [],
            'total_count': len(tokens)
        }
        
        threshold_date = datetime.now() + timedelta(days=days_threshold)
        current_date = datetime.now()
        
        for token in tokens:
            if not token.get('expires_at'):
                # Token doesn't expire (permanent token)
                token['status'] = 'No Expiration'
                token['days_until_expiry'] = 'Never'
                result['no_expiration'].append(token)
                continue
                
            try:
                expires_at = datetime.fromisoformat(token['expires_at'].replace('Z', '+00:00'))
                # Convert to naive datetime for comparison
                expires_at = expires_at.replace(tzinfo=None)
                
                days_until_expiry = (expires_at - current_date).days
                token['days_until_expiry'] = days_until_expiry
                
                if expires_at <= current_date:
                    # Already expired
                    token['status'] = 'Expired'
                    result['expired'].append(token)
                elif expires_at <= threshold_date:
                    # Expiring within threshold
                    token['status'] = 'Expiring Soon'
                    result['expiring_soon'].append(token)
                else:
                    # Healthy (expires beyond threshold)
                    token['status'] = 'Healthy'
                    result['healthy'].append(token)
                    
            except ValueError as e:
                print(f"Error parsing date for token {token.get('name', 'unknown')}: {e}")
                token['status'] = 'Error'
                token['days_until_expiry'] = 'Unknown'
                result['healthy'].append(token)  # Put error tokens in healthy for safety
                
        return result
    
    @staticmethod
    def group_tokens_by_type(tokens: List[Dict]) -> Dict[str, List[Dict]]:
        """Group tokens by their type (personal, project, group)"""
        return {
            'personal': [t for t in tokens if t.get('user_id') and not t.get('token_type')],
            'project': [t for t in tokens if t.get('token_type') == 'project'],
            'group': [t for t in tokens if t.get('token_type') == 'group']
        }
    
    @staticmethod
    def get_summary_stats(token_analysis: Dict) -> Dict[str, int]:
        """Get summary statistics from token analysis"""
        return {
            'total_tokens': token_analysis['total_count'],
            'expired_count': len(token_analysis['expired']),
            'expiring_count': len(token_analysis['expiring_soon']),
            'healthy_count': len(token_analysis['healthy']),
            'permanent_count': len(token_analysis['no_expiration']),
            'problematic_count': len(token_analysis['expired']) + len(token_analysis['expiring_soon'])
        }