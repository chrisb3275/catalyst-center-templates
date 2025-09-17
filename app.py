#!/usr/bin/env python3
"""
Catalyst Center Templates Web Application
A Flask web application for managing and deploying Catalyst Center templates.
"""

import os
import json
import yaml
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Template directories
TEMPLATE_DIRS = {
    'network': 'templates/network',
    'security': 'templates/security',
    'automation': 'templates/automation',
    'monitoring': 'templates/monitoring',
    'community': 'templates/community'
}

def load_template(template_path):
    """Load a YAML template file."""
    try:
        with open(template_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Error loading template {template_path}: {e}")
        return None

def load_json_template(template_path):
    """Load a JSON template file."""
    try:
        with open(template_path, 'r') as file:
            content = file.read().strip()
            
            # Skip if file is empty or appears to be corrupted
            if not content or len(content) < 10:
                return None
                
            # Try to parse as JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                # If it's not valid JSON, skip this file
                logger.warning(f"Skipping non-JSON file: {template_path}")
                return None
            
            # Handle different JSON structures
            if isinstance(data, list):
                if data:
                    # Check if it's a project with templates array
                    if 'templates' in data[0]:
                        # It's a project file, take the first template from templates array
                        if data[0]['templates']:
                            template_data = data[0]['templates'][0]
                        else:
                            return None
                    else:
                        # It's a direct template array
                        template_data = data[0]
                else:
                    return None
            else:
                template_data = data
            
            # Convert JSON to a standard template format
            return {
                'template_name': template_data.get('name', Path(template_path).stem),
                'template_description': template_data.get('description', 'Community template'),
                'configuration': template_data.get('templateContent', '').split('\n') if template_data.get('templateContent') else [],
                'parameters': template_data.get('templateParams', []),
                'tags': template_data.get('tags', ['community']),
                'author': template_data.get('author', 'Community'),
                'version': template_data.get('version', '1.0'),
                'device_types': template_data.get('deviceTypes', []),
                'software_type': template_data.get('softwareType', ''),
                'software_variant': template_data.get('softwareVariant', '')
            }
    except Exception as e:
        logger.error(f"Error loading JSON template {template_path}: {e}")
        return None

def get_templates_by_category(category):
    """Get all templates in a specific category."""
    templates = []
    template_dir = Path(TEMPLATE_DIRS.get(category, ''))
    
    if template_dir.exists():
        # Look for both YAML and JSON files
        for file_path in template_dir.glob('*.yaml'):
            template = load_template(file_path)
            if template:
                template['file_path'] = str(file_path)
                template['category'] = category
                template['file_type'] = 'yaml'
                template['filename'] = file_path.stem  # Store the actual filename without extension
                templates.append(template)
        
        for file_path in template_dir.glob('*.json'):
            template = load_json_template(file_path)
            if template:
                template['file_path'] = str(file_path)
                template['category'] = category
                template['file_type'] = 'json'
                template['filename'] = file_path.stem  # Store the actual filename without extension
                templates.append(template)
    
    return templates

def render_template_with_params(template, parameters):
    """Render a template with given parameters using Jinja2."""
    try:
        from jinja2 import Template
        config_lines = template.get('configuration', [])
        config_text = '\n'.join(config_lines)
        
        jinja_template = Template(config_text)
        return jinja_template.render(**parameters)
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        return f"Error rendering template: {str(e)}"

@app.route('/')
def index():
    """Home page showing all template categories."""
    categories = {}
    for category in TEMPLATE_DIRS.keys():
        templates = get_templates_by_category(category)
        categories[category] = {
            'count': len(templates),
            'templates': templates[:3]  # Show first 3 templates
        }
    
    return render_template('index.html', categories=categories)

@app.route('/templates/<category>')
def templates_category(category):
    """Show all templates in a specific category."""
    if category not in TEMPLATE_DIRS:
        return "Category not found", 404
    
    templates = get_templates_by_category(category)
    return render_template('templates.html', category=category, templates=templates)

@app.route('/template/<category>/<template_name>')
def template_detail(category, template_name):
    """Show detailed view of a specific template."""
    # Try YAML first, then JSON
    yaml_path = Path(TEMPLATE_DIRS[category]) / f"{template_name}.yaml"
    json_path = Path(TEMPLATE_DIRS[category]) / f"{template_name}.json"
    
    template = None
    template_path = None
    
    if yaml_path.exists():
        template_path = yaml_path
        template = load_template(template_path)
    elif json_path.exists():
        template_path = json_path
        template = load_json_template(template_path)
    
    if not template:
        return "Template not found", 404
    
    template['file_path'] = str(template_path)
    template['category'] = category
    template['file_type'] = template_path.suffix[1:]  # Remove the dot
    
    return render_template('template_detail.html', template=template)

@app.route('/render', methods=['POST'])
def render_template_endpoint():
    """Render a template with provided parameters."""
    try:
        data = request.get_json()
        template_name = data.get('template_name')
        category = data.get('category')
        parameters = data.get('parameters', {})
        
        template_path = Path(TEMPLATE_DIRS[category]) / f"{template_name}.yaml"
        template = load_template(template_path)
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        rendered_config = render_template_with_params(template, parameters)
        
        return jsonify({
            'success': True,
            'rendered_config': rendered_config,
            'template_name': template_name
        })
    
    except Exception as e:
        logger.error(f"Error in render endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates')
def api_templates():
    """API endpoint to get all templates."""
    all_templates = []
    for category in TEMPLATE_DIRS.keys():
        templates = get_templates_by_category(category)
        all_templates.extend(templates)
    
    return jsonify(all_templates)

@app.route('/api/templates/<category>')
def api_templates_category(category):
    """API endpoint to get templates by category."""
    if category not in TEMPLATE_DIRS:
        return jsonify({'error': 'Category not found'}), 404
    
    templates = get_templates_by_category(category)
    return jsonify(templates)

@app.route('/download/<category>/<template_name>')
def download_template(category, template_name):
    """Download a template file."""
    # Try YAML first, then JSON
    yaml_path = Path(TEMPLATE_DIRS[category]) / f"{template_name}.yaml"
    json_path = Path(TEMPLATE_DIRS[category]) / f"{template_name}.json"
    
    template_path = None
    if yaml_path.exists():
        template_path = yaml_path
    elif json_path.exists():
        template_path = json_path
    
    if not template_path:
        return "Template not found", 404
    
    return send_file(template_path, as_attachment=True, 
                    download_name=f"{template_name}{template_path.suffix}")

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'catalyst-center-templates'})

if __name__ == '__main__':
    # Create templates directory for Flask templates
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    # For production, use gunicorn if available
    if not debug and 'gunicorn' in os.environ.get('SERVER_SOFTWARE', ''):
        # Running under gunicorn
        pass
    else:
        # Running directly
        app.run(host='0.0.0.0', port=port, debug=debug)
