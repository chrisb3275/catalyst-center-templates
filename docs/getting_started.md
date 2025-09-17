# Getting Started with Catalyst Center Templates

This guide will help you get started with the Catalyst Center Templates project.

## Prerequisites

Before you begin, ensure you have the following:

- Python 3.7 or higher
- Access to a Cisco Catalyst Center (DNA Center) instance
- Basic knowledge of network configuration and YAML
- Git (for cloning the repository)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd catalyst-center-templates
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp config/env.example .env
   # Edit .env with your Catalyst Center credentials
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root with your Catalyst Center configuration:

```env
DNAC_HOST=your-catalyst-center-host.com
DNAC_PORT=443
DNAC_USERNAME=your-username
DNAC_PASSWORD=your-password
DNAC_VERIFY_SSL=true
```

### Template Parameters

Each template includes parameters that can be customized for your environment. Review the template files in the `templates/` directory to understand available parameters.

## Usage Examples

### 1. Basic Template Rendering

```python
from scripts.catalyst_center_client import CatalystCenterClient
import yaml

# Load a template
with open('templates/network/basic_switch_config.yaml', 'r') as f:
    template = yaml.safe_load(f)

# Render with parameters
parameters = {
    'hostname': 'SW-ACCESS-01',
    'management_vlan': 100,
    'management_ip': '192.168.100.10'
}

# Use Jinja2 to render the template
from jinja2 import Template
config_text = '\n'.join(template['configuration'])
rendered = Template(config_text).render(**parameters)
print(rendered)
```

### 2. Connecting to Catalyst Center

```python
from scripts.catalyst_center_client import CatalystCenterClient

# Initialize client
client = CatalystCenterClient(
    host='your-catalyst-center-host.com',
    username='your-username',
    password='your-password'
)

# Get devices
devices = client.get_devices()
print(f"Found {len(devices)} devices")

# Get templates
templates = client.get_templates()
print(f"Found {len(templates)} templates")
```

### 3. Running the Example

```bash
python examples/basic_usage.py
```

## Template Categories

### Network Templates
- **Basic Switch Configuration**: Standard switch setup with management VLAN, SSH, SNMP
- **Router Configuration**: Basic router configuration templates
- **VLAN Configuration**: VLAN setup and management templates

### Security Templates
- **Access Control Lists**: Common ACL configurations
- **Port Security**: Port security configurations
- **802.1X Authentication**: Network access control templates

### Automation Templates
- **Device Provisioning**: Automated device onboarding workflows
- **Configuration Management**: Template deployment automation
- **Compliance Checking**: Automated compliance verification

### Monitoring Templates
- **Network Health**: Comprehensive monitoring configuration
- **Performance Metrics**: Bandwidth and performance monitoring
- **Alerting**: Notification and alerting setup

## Best Practices

1. **Test Templates**: Always test templates in a lab environment before production deployment
2. **Version Control**: Use version control for your custom templates
3. **Documentation**: Document any custom parameters or modifications
4. **Backup**: Always backup configurations before applying templates
5. **Validation**: Validate rendered configurations before deployment

## Troubleshooting

### Common Issues

1. **Connection Errors**: Verify Catalyst Center credentials and network connectivity
2. **Template Errors**: Check YAML syntax and parameter values
3. **Permission Errors**: Ensure your account has appropriate permissions in Catalyst Center
4. **SSL Errors**: Verify SSL certificates or disable SSL verification if needed

### Getting Help

- Check the logs in the `logs/` directory
- Review the example files in the `examples/` directory
- Consult the Cisco Catalyst Center documentation
- Create an issue in the project repository

## Next Steps

- Explore the template library in the `templates/` directory
- Customize templates for your specific environment
- Create your own templates following the established patterns
- Set up automated deployment workflows
- Configure monitoring and alerting
