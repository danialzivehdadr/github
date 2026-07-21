#!/usr/bin/env python3
"""
IP Geolocation Tracker
Track and map attacker IP addresses
"""

import requests
import json

def trace_ip_detailed(ip_address):
    """Get detailed geolocation for an IP"""
    
    # Using multiple APIs for accuracy
    apis = [
        f'http://ip-api.com/json/{ip_address}',
        f'https://ipinfo.io/{ip_address}/json',
        f'https://ipapi.co/{ip_address}/json/'
    ]
    
    results = []
    
    for api_url in apis:
        try:
            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                results.append(data)
        except:
            continue
    
    # Consolidate results
    if results:
        primary = results[0]
        
        return {
            'ip': ip_address,
            'country': primary.get('country', 'Unknown'),
            'region': primary.get('region', primary.get('regionName', 'Unknown')),
            'city': primary.get('city', 'Unknown'),
            'latitude': primary.get('lat', primary.get('latitude', 'Unknown')),
            'longitude': primary.get('lon', primary.get('longitude', 'Unknown')),
            'isp': primary.get('isp', primary.get('org', 'Unknown')),
            'timezone': primary.get('timezone', 'Unknown'),
            'map_url': f"https://www.google.com/maps?q={primary.get('lat', 0)},{primary.get('lon', 0)}"
        }
    
    return None

def generate_attacker_profile(ip_list):
    """Generate comprehensive attacker profile"""
    
    print("\n" + "="*70)
    print("ATTACKER GEOGRAPHIC PROFILE")
    print("="*70)
    
    locations = {}
    
    for ip in ip_list:
        info = trace_ip_detailed(ip)
        
        if info:
            location = f"{info['city']}, {info['country']}"
            
            if location not in locations:
                locations[location] = {
                    'count': 0,
                    'ips': [],
                    'isp': info['isp'],
                    'coordinates': (info['latitude'], info['longitude'])
                }
            
            locations[location]['count'] += 1
            locations[location]['ips'].append(ip)
    
    print(f"\n🌍 Attacker Locations:")
    for location, data in sorted(locations.items(), key=lambda x: x[1]['count'], reverse=True):
        print(f"\n  📍 {location}")
        print(f"     Attack Count: {data['count']}")
        print(f"     IPs: {', '.join(data['ips'][:5])}")
        print(f"     ISP: {data['isp']}")
        print(f"     Map: https://www.google.com/maps?q={data['coordinates'][0]},{data['coordinates'][1]}")
    
    return locations

# Usage
if __name__ == "__main__":
    # Example IPs (replace with actual attacker IPs)
    attacker_ips = [
        '192.168.1.100',
        '10.0.0.50',
        '172.16.0.1'
    ]
    
    generate_attacker_profile(attacker_ips)
