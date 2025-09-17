#!/usr/bin/env python3
"""
Catalyst Center API Client
A Python client for interacting with Cisco Catalyst Center (DNA Center) APIs.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from urllib3.exceptions import InsecureRequestWarning
import urllib3

try:
    from dnacentersdk import DNACenterAPI
    from dnacentersdk.exceptions import ApiError
except ImportError:
    print("Please install dnacentersdk: pip install dnacentersdk")
    exit(1)

# Suppress SSL warnings if needed
urllib3.disable_warnings(InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CatalystCenterClient:
    """Client for interacting with Catalyst Center APIs."""
    
    def __init__(self, host: str, username: str, password: str, 
                 port: int = 443, verify_ssl: bool = True):
        """
        Initialize the Catalyst Center client.
        
        Args:
            host: Catalyst Center hostname or IP
            username: Username for authentication
            password: Password for authentication
            port: Port number (default: 443)
            verify_ssl: Whether to verify SSL certificates
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.verify_ssl = verify_ssl
        
        # Initialize the API client
        self.api = DNACenterAPI(
            base_url=f"https://{host}:{port}",
            username=username,
            password=password,
            verify=verify_ssl
        )
        
        logger.info(f"Connected to Catalyst Center at {host}:{port}")
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """Get all devices from Catalyst Center."""
        try:
            devices = self.api.devices.get_device_list()
            logger.info(f"Retrieved {len(devices.response)} devices")
            return devices.response
        except ApiError as e:
            logger.error(f"Error retrieving devices: {e}")
            return []
    
    def get_sites(self) -> List[Dict[str, Any]]:
        """Get all sites from Catalyst Center."""
        try:
            sites = self.api.sites.get_sites()
            logger.info(f"Retrieved {len(sites.response)} sites")
            return sites.response
        except ApiError as e:
            logger.error(f"Error retrieving sites: {e}")
            return []
    
    def get_network_health(self) -> Dict[str, Any]:
        """Get network health information."""
        try:
            health = self.api.clients.get_overall_network_health()
            logger.info("Retrieved network health information")
            return health.response
        except ApiError as e:
            logger.error(f"Error retrieving network health: {e}")
            return {}
    
    def deploy_template(self, template_id: str, target_devices: List[str], 
                       parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy a template to target devices.
        
        Args:
            template_id: ID of the template to deploy
            target_devices: List of device IDs to deploy to
            parameters: Template parameters
            
        Returns:
            Deployment result
        """
        try:
            deployment = self.api.configuration_templates.deploy_template(
                template_id=template_id,
                target_info=target_devices,
                params=parameters
            )
            logger.info(f"Template {template_id} deployment initiated")
            return deployment
        except ApiError as e:
            logger.error(f"Error deploying template: {e}")
            return {}
    
    def get_templates(self) -> List[Dict[str, Any]]:
        """Get all configuration templates."""
        try:
            templates = self.api.configuration_templates.get_templates()
            logger.info(f"Retrieved {len(templates.response)} templates")
            return templates.response
        except ApiError as e:
            logger.error(f"Error retrieving templates: {e}")
            return []


def main():
    """Example usage of the Catalyst Center client."""
    # Load configuration from environment variables
    host = os.getenv('DNAC_HOST', 'your-catalyst-center-host.com')
    username = os.getenv('DNAC_USERNAME', 'your-username')
    password = os.getenv('DNAC_PASSWORD', 'your-password')
    verify_ssl = os.getenv('DNAC_VERIFY_SSL', 'true').lower() == 'true'
    
    if host == 'your-catalyst-center-host.com':
        print("Please configure your Catalyst Center credentials in the environment variables")
        return
    
    # Initialize client
    client = CatalystCenterClient(host, username, password, verify_ssl=verify_ssl)
    
    # Example operations
    print("Getting devices...")
    devices = client.get_devices()
    print(f"Found {len(devices)} devices")
    
    print("Getting sites...")
    sites = client.get_sites()
    print(f"Found {len(sites)} sites")
    
    print("Getting templates...")
    templates = client.get_templates()
    print(f"Found {len(templates)} templates")


if __name__ == "__main__":
    main()
