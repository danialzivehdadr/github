#!/usr/bin/env python3
"""
GitHub Security Events Analyzer
Extract suspicious IPs from GitHub security logs
"""

import requests
import json

def get_github_security_events(token):
    """Get security events from GitHub API"""
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Get audit log (requires GitHub Enterprise)
    url = 'https://api.github.com/orgs/YOUR_ORG/audit-log'
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            events = response.json()
            
            suspicious_ips = []
            
            for event in events:
                if 'actor_ip' in event:
                    ip = event['actor_ip']
                    action = event.get('action', '')
                    
                    # Filter suspicious actions
                    if any(keyword in action.lower() for keyword in 
                           ['clone', 'push', 'pull', 'delete', 'create']):
                        suspicious_ips.append({
                            'ip': ip,
                            'action': action,
                            'timestamp': event.get('@timestamp', ''),
                            'actor': event.get('actor', '')
                        })
            
            return suspicious_ips
        else:
            print(f"Error: {response.status_code}")
            return []
    
    except Exception as e:
        print(f"Error: {e}")
        return []

# Usage
if __name__ == "__main__":
    # Replace with your GitHub personal access token
    GITHUB_TOKEN = 'your_token_here'
    
    events = get_github_security_events(GITHUB_TOKEN)
    
    if events:
        print("\n" + "="*70)
        print("GITHUB SECURITY EVENTS")
        print("="*70)
        
        for event in events[:20]:  # Show last 20 events
            print(f"\nIP: {event['ip']}")
            print(f"Action: {event['action']}")
            print(f"Actor: {event['actor']}")
            print(f"Time: {event['timestamp']}")
    else:
        print("No security events found")
