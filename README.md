# Catalyst Center Templates

A comprehensive collection of templates and automation scripts for Cisco Catalyst Center (DNA Center) with a modern web interface.

## 🌐 Live Demo

**Deploy to Render (Free):**
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/yourusername/catalyst-center-templates)

## 🚀 Quick Start

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/catalyst-center-templates.git
   cd catalyst-center-templates
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open your browser:**
   Visit `http://localhost:5000`

### Deploy to Render (Free)

1. **Fork this repository** to your GitHub account
2. **Go to [render.com](https://render.com)** and sign up
3. **Click "New +" → "Web Service"**
4. **Connect your GitHub repository**
5. **Configure:**
   - **Name**: `catalyst-center-templates`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Plan**: `Free`
6. **Click "Create Web Service"**

Your app will be live at `https://your-app-name.onrender.com`

## 📁 Project Structure

```
catalyst-center-templates/
├── app.py                 # Flask web application
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── templates.html
│   └── template_detail.html
├── static/               # CSS and JavaScript
│   ├── css/style.css
│   └── js/app.js
├── templates/            # YAML template files
│   ├── network/          # Network configuration templates
│   ├── security/         # Security policy templates
│   ├── automation/       # Automation workflow templates
│   └── monitoring/       # Monitoring and alerting templates
├── scripts/              # Python automation scripts
├── examples/             # Usage examples
├── docs/                 # Documentation
└── config/               # Configuration files
```

## 🎯 Features

### Web Interface
- **Modern UI** with Bootstrap 5 and responsive design
- **Template Browser** organized by categories
- **Interactive Template Renderer** with parameter forms
- **API Endpoints** for programmatic access
- **Download Functionality** for template files
- **Health Monitoring** with status endpoints

### Template Categories
- **Network Templates**: Switch, router, and access point configurations
- **Security Templates**: ACLs, port security, and authentication
- **Automation Templates**: Device provisioning and workflow automation
- **Monitoring Templates**: Health checks, alerting, and reporting

### API Access
- `GET /api/templates` - Get all templates
- `GET /api/templates/{category}` - Get templates by category
- `POST /render` - Render template with parameters
- `GET /health` - Health check endpoint

## 🔧 Configuration

### Environment Variables

```bash
# Flask configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
PORT=5000

# Optional: Catalyst Center credentials
DNAC_HOST=your-catalyst-center-host.com
DNAC_USERNAME=your-username
DNAC_PASSWORD=your-password
DNAC_VERIFY_SSL=true
```

## 📚 Usage Examples

### Using the Web Interface

1. **Browse Templates**: Visit the home page to see all available templates
2. **View Details**: Click on any template to see parameters and configuration
3. **Render Template**: Use the interactive form to render templates with custom parameters
4. **Download**: Download template files for offline use

### Using the API

```bash
# Get all templates
curl https://your-app.onrender.com/api/templates

# Get network templates
curl https://your-app.onrender.com/api/templates/network

# Render a template
curl -X POST https://your-app.onrender.com/render \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "basic_switch_config",
    "category": "network",
    "parameters": {
      "hostname": "SW-ACCESS-01",
      "management_vlan": 100,
      "management_ip": "192.168.100.10"
    }
  }'
```

### Using Python Scripts

```python
from scripts.catalyst_center_client import CatalystCenterClient

# Connect to Catalyst Center
client = CatalystCenterClient(
    host='your-catalyst-center-host.com',
    username='your-username',
    password='your-password'
)

# Get devices
devices = client.get_devices()
print(f"Found {len(devices)} devices")
```

## 🛠️ Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run in development mode
export FLASK_ENV=development
python app.py
```

### Testing

```bash
# Run tests
python -m pytest

# Test API endpoints
curl http://localhost:5000/health
curl http://localhost:5000/api/templates
```

## 📖 Documentation

- [Getting Started Guide](docs/getting_started.md)
- [Deployment Guide](docs/deployment.md)
- [Free Hosting Guide](docs/free_hosting_guide.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Cisco Catalyst Center](https://www.cisco.com/c/en/us/products/cloud-systems-management/dna-center/)
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Bootstrap](https://getbootstrap.com/) - CSS framework
- [Render](https://render.com/) - Free hosting platform

## 📞 Support

- Create an [issue](https://github.com/yourusername/catalyst-center-templates/issues) for bug reports
- Start a [discussion](https://github.com/yourusername/catalyst-center-templates/discussions) for questions
- Check the [documentation](docs/) for guides

---

**Made with ❤️ for the networking community**