#!/usr/bin/env python3
"""
Online IP Investigation Tools
Generate links for deeper IP investigation
"""

def generate_investigation_links(ip_address):
    """Generate links for investigating an IP address"""
    
    tools = {
        'VirusTotal': f'https://www.virustotal.com/gui/search/{ip_address}',
        'AbuseIPDB': f'https://www.abuseipdb.com/check/{ip_address}',
        'Shodan': f'https://www.shodan.io/host/{ip_address}',
        'Censys': f'https://search.censys.io/hosts/{ip_address}',
        'IPInfo': f'https://ipinfo.io/{ip_address}',
        'IP2Location': f'https://www.ip2location.com/demo/{ip_address}',
        'Whois': f'https://whois.domaintools.com/{ip_address}',
        'ThreatCrowd': f'https://www.threatcrowd.org/ip.php?ip={ip_address}',
        'AlienVault OTX': f'https://otx.alienvault.com/indicator/IPv4/{ip_address}',
        'IBM X-Force': f'https://exchange.xforce.ibmcloud.com/ip/{ip_address}'
    }
    
    print(f"\n{'='*70}")
    print(f"INVESTIGATION LINKS FOR IP: {ip_address}")
    print(f"{'='*70}\n")
    
    for tool_name, url in tools.items():
        print(f"  🔍 {tool_name}:")
        print(f"     {url}\n")
    
    return tools

# Usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        ip = sys.argv[1]
        generate_investigation_links(ip)
    else:
        print("Usage: python ip_investigation.py <ip_address>")
