#!/usr/bin/env python3
"""
Basic Usage Example for Catalyst Center Templates
This example demonstrates how to use the templates and scripts.
"""

import os
import sys
import json
from pathlib import Path

# Add the scripts directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

from catalyst_center_client import CatalystCenterClient


def load_template(template_path: str) -> dict:
    """Load a template from YAML file."""
    import yaml
    
    with open(template_path, 'r') as file:
        return yaml.safe_load(file)


def render_template(template: dict, parameters: dict) -> str:
    """Render a template with given parameters."""
    from jinja2 import Template
    
    config_lines = template.get('configuration', [])
    config_text = '\n'.join(config_lines)
    
    jinja_template = Template(config_text)
    return jinja_template.render(**parameters)


def main():
    """Main example function."""
    print("Catalyst Center Templates - Basic Usage Example")
    print("=" * 50)
    
    # Example 1: Load and render a network template
    print("\n1. Loading and rendering network template...")
    template_path = "templates/network/basic_switch_config.yaml"
    
    if os.path.exists(template_path):
        template = load_template(template_path)
        print(f"Template: {template['template_name']}")
        print(f"Description: {template['template_description']}")
        
        # Example parameters
        parameters = {
            'hostname': 'SW-ACCESS-01',
            'management_vlan': 100,
            'management_ip': '192.168.100.10',
            'management_mask': '255.255.255.0',
            'default_gateway': '192.168.100.1'
        }
        
        # Render the template
        rendered_config = render_template(template, parameters)
        print("\nRendered Configuration:")
        print("-" * 30)
        print(rendered_config)
    else:
        print(f"Template file not found: {template_path}")
    
    # Example 2: Connect to Catalyst Center (if configured)
    print("\n2. Connecting to Catalyst Center...")
    
    # Check if environment variables are set
    host = os.getenv('DNAC_HOST')
    username = os.getenv('DNAC_USERNAME')
    password = os.getenv('DNAC_PASSWORD')
    
    if host and username and password:
        try:
            client = CatalystCenterClient(host, username, password)
            
            # Get devices
            devices = client.get_devices()
            print(f"Found {len(devices)} devices in Catalyst Center")
            
            # Get sites
            sites = client.get_sites()
            print(f"Found {len(sites)} sites in Catalyst Center")
            
            # Get templates
            templates = client.get_templates()
            print(f"Found {len(templates)} templates in Catalyst Center")
            
        except Exception as e:
            print(f"Error connecting to Catalyst Center: {e}")
    else:
        print("Catalyst Center credentials not configured.")
        print("Please set DNAC_HOST, DNAC_USERNAME, and DNAC_PASSWORD environment variables.")
    
    # Example 3: Load monitoring template
    print("\n3. Loading monitoring template...")
    monitoring_template_path = "templates/monitoring/network_health.yaml"
    
    if os.path.exists(monitoring_template_path):
        monitoring_template = load_template(monitoring_template_path)
        print(f"Monitoring Template: {monitoring_template['template_name']}")
        
        # Show health checks
        health_checks = monitoring_template.get('monitoring_config', {}).get('health_checks', [])
        print(f"Configured {len(health_checks)} health checks:")
        for check in health_checks:
            print(f"  - {check['name']}: {check['description']}")
        
        # Show alerts
        alerts = monitoring_template.get('monitoring_config', {}).get('alerts', [])
        print(f"Configured {len(alerts)} alerts:")
        for alert in alerts:
            print(f"  - {alert['name']} ({alert['severity']}): {alert['description']}")
    
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
