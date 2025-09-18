#!/usr/bin/env python3
"""
Catalyst Center Templates Web Application
A Flask web application for managing and deploying Catalyst Center templates.
"""

import os
import json
import yaml
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Authentication configuration
AUTH_ENABLED = os.environ.get('AUTH_ENABLED', 'false').lower() == 'true'
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'CXlabs.123')
ALLOWED_IPS = os.environ.get('ALLOWED_IPS', '').split(',') if os.environ.get('ALLOWED_IPS') else []

# Simple user storage (in production, use a database)
users = {
    ADMIN_USERNAME: generate_password_hash(ADMIN_PASSWORD)
}

def check_auth():
    """Check if user is authenticated."""
    if not AUTH_ENABLED:
        return True
    return session.get('authenticated', False)

def check_ip_whitelist():
    """Check if client IP is in allowed list."""
    if not ALLOWED_IPS or not ALLOWED_IPS[0]:
        return True
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    return client_ip in ALLOWED_IPS

def require_auth(f):
    """Decorator to require authentication."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_ip_whitelist():
            return jsonify({'error': 'Access denied from this IP address'}), 403
        if not check_auth():
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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

def load_custom_categories():
    """Load custom categories from categories.json."""
    categories_file = Path('data/categories.json')
    if categories_file.exists():
        try:
            with open(categories_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading custom categories: {e}")
    return {}

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
            if isinstance(data, str):
                # If it's a string, skip this file as it's not a valid template
                logger.warning(f"Skipping JSON file with string content: {template_path}")
                return None
            elif isinstance(data, list):
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
    custom_categories = load_custom_categories()
    
    # Load all categories (built-in + custom)
    all_categories = set(TEMPLATE_DIRS.keys())
    for cat_name in custom_categories.keys():
        if cat_name not in TEMPLATE_DIRS:
            # Add custom category to TEMPLATE_DIRS if not already there
            TEMPLATE_DIRS[cat_name] = str(Path('templates') / cat_name)
        all_categories.add(cat_name)
    
    for category in all_categories:
        templates = get_templates_by_category(category)
        category_info = {
            'count': len(templates),
            'templates': templates[:3]  # Show first 3 templates
        }
        
        # Add custom category metadata if available
        if category in custom_categories:
            category_info.update(custom_categories[category])
        
        categories[category] = category_info
    
    return render_template('index.html', categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and check_password_hash(users[username], password):
            session['authenticated'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and clear session."""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/templates/<category>')
@require_auth
def templates_category(category):
    """Show all templates in a specific category."""
    if category not in TEMPLATE_DIRS:
        return "Category not found", 404
    
    templates = get_templates_by_category(category)
    return render_template('templates.html', category=category, templates=templates)

@app.route('/template/<category>/<path:template_name>')
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
    template['filename'] = template_name  # Ensure filename is set
    
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
@require_auth
def api_templates():
    """API endpoint to get all templates."""
    all_templates = []
    for category in TEMPLATE_DIRS.keys():
        templates = get_templates_by_category(category)
        all_templates.extend(templates)
    
    return jsonify(all_templates)

@app.route('/api/templates/<category>')
@require_auth
def api_templates_category(category):
    """API endpoint to get templates by category."""
    if category not in TEMPLATE_DIRS:
        return jsonify({'error': 'Category not found'}), 404
    
    templates = get_templates_by_category(category)
    return jsonify(templates)

@app.route('/download/<category>/<path:template_name>')
def download_template(category, template_name):
    """Download a template file."""
    try:
        if category not in TEMPLATE_DIRS:
            return jsonify({'error': 'Category not found'}), 404
        
        # Try YAML first, then JSON
        yaml_path = Path(TEMPLATE_DIRS[category]) / f"{template_name}.yaml"
        json_path = Path(TEMPLATE_DIRS[category]) / f"{template_name}.json"
        
        template_path = None
        if yaml_path.exists():
            template_path = yaml_path
        elif json_path.exists():
            template_path = json_path
        
        if not template_path:
            return jsonify({'error': 'Template file not found'}), 404
        
        return send_file(template_path, as_attachment=True, 
                        download_name=f"{template_name}{template_path.suffix}")
    except Exception as e:
        logger.error(f"Error downloading template {template_name}: {e}")
        return jsonify({'error': 'Download failed'}), 500

@app.route('/preview/<category>/<path:template_name>')
def preview_template(category, template_name):
    """Preview a template file content."""
    try:
        if category not in TEMPLATE_DIRS:
            return jsonify({'error': 'Category not found'}), 404
        
        # Try YAML first, then JSON
        yaml_path = Path(TEMPLATE_DIRS[category]) / f"{template_name}.yaml"
        json_path = Path(TEMPLATE_DIRS[category]) / f"{template_name}.json"
        
        template_path = None
        if yaml_path.exists():
            template_path = yaml_path
        elif json_path.exists():
            template_path = json_path
        
        if not template_path:
            return jsonify({'error': 'Template file not found'}), 404
        
        # Read file content
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'content': content,
            'filename': template_path.name,
            'file_type': template_path.suffix[1:]
        })
    except Exception as e:
        logger.error(f"Error previewing template {template_name}: {e}")
        return jsonify({'error': 'Preview failed'}), 500

@app.route('/search')
def search_templates():
    """Search templates by name, description, or tags with advanced filters."""
    query = request.args.get('q', '').strip().lower()
    category = request.args.get('category', '')
    sort_by = request.args.get('sort', 'name')  # name, version, author, date
    sort_order = request.args.get('order', 'asc')  # asc, desc
    file_type = request.args.get('type', '')  # yaml, json
    author = request.args.get('author', '').strip().lower()
    
    if not query and not category and not file_type and not author:
        return redirect(url_for('index'))
    
    # Get all templates
    all_templates = []
    for cat in TEMPLATE_DIRS.keys():
        if not category or cat == category:
            templates = get_templates_by_category(cat)
            all_templates.extend(templates)
    
    # Filter templates based on search criteria
    filtered_templates = []
    for template in all_templates:
        # Text search
        if query:
            # Extract device type names from dictionaries
            device_type_names = []
            for device_type in template.get('device_types', []):
                if isinstance(device_type, dict):
                    device_type_names.append(device_type.get('productFamily', ''))
                    device_type_names.append(device_type.get('productSeries', ''))
                else:
                    device_type_names.append(str(device_type))
            
            # Extract tag names from dictionaries or strings
            tag_names = []
            for tag in template.get('tags', []):
                if isinstance(tag, dict):
                    tag_names.append(tag.get('name', str(tag)))
                else:
                    tag_names.append(str(tag))
            
            searchable_text = ' '.join([
                template.get('template_name', ''),
                template.get('template_description', ''),
                ' '.join(tag_names),
                template.get('author', ''),
                ' '.join(device_type_names)
            ]).lower()
            
            if query not in searchable_text:
                continue
        
        # File type filter
        if file_type and template.get('file_type', '') != file_type:
            continue
            
        # Author filter
        if author and author not in template.get('author', '').lower():
            continue
            
        filtered_templates.append(template)
    
    # Sort templates
    if sort_by == 'name':
        filtered_templates.sort(key=lambda x: x.get('template_name', '').lower(), 
                              reverse=(sort_order == 'desc'))
    elif sort_by == 'version':
        filtered_templates.sort(key=lambda x: x.get('version', '0'), 
                              reverse=(sort_order == 'desc'))
    elif sort_by == 'author':
        filtered_templates.sort(key=lambda x: x.get('author', '').lower(), 
                              reverse=(sort_order == 'desc'))
    
    # Group by category for display
    categories = {}
    for template in filtered_templates:
        cat = template.get('category', 'unknown')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(template)
    
    return render_template('search_results.html', 
                         query=query, 
                         categories=categories,
                         total_results=len(filtered_templates),
                         sort_by=sort_by,
                         sort_order=sort_order,
                         file_type=file_type,
                         author=author,
                         selected_category=category)

@app.route('/bulk-download', methods=['POST'])
def bulk_download():
    """Download multiple templates as a ZIP file."""
    try:
        import zipfile
        import io
        
        data = request.get_json()
        template_ids = data.get('templates', [])
        
        if not template_ids:
            return jsonify({'error': 'No templates selected'}), 400
        
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for template_id in template_ids:
                # Parse template_id (format: "category:filename")
                if ':' not in template_id:
                    continue
                    
                category, filename = template_id.split(':', 1)
                
                if category not in TEMPLATE_DIRS:
                    continue
                
                # Try YAML first, then JSON
                yaml_path = Path(TEMPLATE_DIRS[category]) / f"{filename}.yaml"
                json_path = Path(TEMPLATE_DIRS[category]) / f"{filename}.json"
                
                template_path = None
                if yaml_path.exists():
                    template_path = yaml_path
                elif json_path.exists():
                    template_path = json_path
                
                if template_path:
                    # Add file to ZIP
                    zip_file.write(template_path, f"{category}/{template_path.name}")
        
        zip_buffer.seek(0)
        
        return send_file(
            io.BytesIO(zip_buffer.getvalue()),
            as_attachment=True,
            download_name=f"templates_bulk_{len(template_ids)}_files.zip",
            mimetype='application/zip'
        )
        
    except Exception as e:
        logger.error(f"Error in bulk download: {e}")
        return jsonify({'error': 'Bulk download failed'}), 500

@app.route('/manage-categories')
def manage_categories():
    """Manage template categories page."""
    return render_template('manage_categories.html')

@app.route('/create-category', methods=['GET', 'POST'])
def create_category():
    """Create a new template category."""
    if request.method == 'GET':
        return render_template('create_category.html')
    
    data = request.get_json()
    category_name = data.get('name', '').strip().lower()
    description = data.get('description', '').strip()
    icon = data.get('icon', 'fas fa-folder')
    color = data.get('color', 'secondary')
    
    if not category_name:
        return jsonify({'error': 'Category name is required'}), 400
    
    # Validate category name (alphanumeric and hyphens only)
    import re
    if not re.match(r'^[a-z0-9-]+$', category_name):
        return jsonify({'error': 'Category name can only contain lowercase letters, numbers, and hyphens'}), 400
    
    if category_name in TEMPLATE_DIRS:
        return jsonify({'error': 'Category already exists'}), 400
    
    # Create category directory
    category_dir = Path('templates') / category_name
    category_dir.mkdir(parents=True, exist_ok=True)
    
    # Update TEMPLATE_DIRS
    TEMPLATE_DIRS[category_name] = str(category_dir)
    
    # Save category metadata
    category_metadata = {
        'name': category_name,
        'display_name': data.get('display_name', category_name.title()),
        'description': description,
        'icon': icon,
        'color': color,
        'created_at': datetime.now().isoformat()
    }
    
    # Save to categories.json
    categories_file = Path('data/categories.json')
    categories_file.parent.mkdir(parents=True, exist_ok=True)
    
    if categories_file.exists():
        with open(categories_file, 'r') as f:
            categories_data = json.load(f)
    else:
        categories_data = {}
    
    categories_data[category_name] = category_metadata
    
    with open(categories_file, 'w') as f:
        json.dump(categories_data, f, indent=2)
    
    return jsonify({
        'success': True,
        'message': f'Category "{category_name}" created successfully',
        'category': category_metadata
    })

@app.route('/upload', methods=['GET', 'POST'])
def upload_template():
    """Upload a new template file."""
    if request.method == 'GET':
        return render_template('upload.html')
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    category = request.form.get('category', 'community')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if category not in TEMPLATE_DIRS:
        return jsonify({'error': 'Invalid category'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_dir = Path(TEMPLATE_DIRS[category])
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / filename
        file.save(file_path)
        
        return jsonify({
            'success': True,
            'message': f'Template uploaded successfully to {category} category',
            'filename': filename,
            'category': category
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'yaml', 'yml', 'json'}

@app.route('/api/categories')
@require_auth
def api_categories():
    """API endpoint to get all categories with metadata."""
    custom_categories = load_custom_categories()
    return jsonify(custom_categories)

@app.route('/api/categories/<category_name>', methods=['PUT'])
def update_category(category_name):
    """Update a category's metadata."""
    data = request.get_json()
    
    categories_file = Path('data/categories.json')
    if not categories_file.exists():
        return jsonify({'error': 'No categories found'}), 404
    
    try:
        with open(categories_file, 'r') as f:
            categories_data = json.load(f)
        
        if category_name not in categories_data:
            return jsonify({'error': 'Category not found'}), 404
        
        # Update category data
        categories_data[category_name].update({
            'display_name': data.get('display_name', categories_data[category_name].get('display_name', category_name.title())),
            'description': data.get('description', categories_data[category_name].get('description', '')),
            'icon': data.get('icon', categories_data[category_name].get('icon', 'fas fa-folder')),
            'color': data.get('color', categories_data[category_name].get('color', 'secondary')),
            'updated_at': datetime.now().isoformat()
        })
        
        with open(categories_file, 'w') as f:
            json.dump(categories_data, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'Category "{category_name}" updated successfully',
            'category': categories_data[category_name]
        })
    except Exception as e:
        logger.error(f"Error updating category {category_name}: {e}")
        return jsonify({'error': 'Failed to update category'}), 500

@app.route('/api/categories/<category_name>', methods=['DELETE'])
def delete_category(category_name):
    """Delete a category and move templates to community."""
    categories_file = Path('data/categories.json')
    if not categories_file.exists():
        return jsonify({'error': 'No categories found'}), 404
    
    try:
        with open(categories_file, 'r') as f:
            categories_data = json.load(f)
        
        if category_name not in categories_data:
            return jsonify({'error': 'Category not found'}), 404
        
        # Move templates to community category
        category_dir = Path('templates') / category_name
        community_dir = Path('templates') / 'community'
        community_dir.mkdir(parents=True, exist_ok=True)
        
        if category_dir.exists():
            for template_file in category_dir.iterdir():
                if template_file.is_file():
                    # Move file to community directory
                    new_path = community_dir / template_file.name
                    template_file.rename(new_path)
            
            # Remove empty category directory
            category_dir.rmdir()
        
        # Remove from categories data
        del categories_data[category_name]
        
        with open(categories_file, 'w') as f:
            json.dump(categories_data, f, indent=2)
        
        # Remove from TEMPLATE_DIRS if it exists
        if category_name in TEMPLATE_DIRS:
            del TEMPLATE_DIRS[category_name]
        
        return jsonify({
            'success': True,
            'message': f'Category "{category_name}" deleted successfully. Templates moved to community category.'
        })
    except Exception as e:
        logger.error(f"Error deleting category {category_name}: {e}")
        return jsonify({'error': 'Failed to delete category'}), 500

@app.route('/api/templates/move', methods=['POST'])
def move_template():
    """Move a template from one category to another."""
    data = request.get_json()
    template_name = data.get('template_name')
    from_category = data.get('from_category')
    to_category = data.get('to_category')
    
    if not all([template_name, from_category, to_category]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    if from_category == to_category:
        return jsonify({'error': 'Source and destination categories are the same'}), 400
    
    # Validate categories exist
    if from_category not in TEMPLATE_DIRS:
        return jsonify({'error': f'Source category "{from_category}" does not exist'}), 404
    
    if to_category not in TEMPLATE_DIRS:
        return jsonify({'error': f'Destination category "{to_category}" does not exist'}), 404
    
    try:
        from_path = Path(TEMPLATE_DIRS[from_category]) / template_name
        to_path = Path(TEMPLATE_DIRS[to_category]) / template_name
        
        # Check if source file exists
        if not from_path.exists():
            return jsonify({'error': f'Template "{template_name}" not found in "{from_category}"'}), 404
        
        # Check if destination file already exists
        if to_path.exists():
            return jsonify({'error': f'Template "{template_name}" already exists in "{to_category}"'}), 409
        
        # Create destination directory if it doesn't exist
        to_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Move the file
        from_path.rename(to_path)
        
        logger.info(f"Moved template '{template_name}' from '{from_category}' to '{to_category}'")
        
        return jsonify({
            'success': True,
            'message': f'Template "{template_name}" moved from "{from_category}" to "{to_category}" successfully'
        })
        
    except Exception as e:
        logger.error(f"Error moving template {template_name}: {e}")
        return jsonify({'error': 'Failed to move template'}), 500

@app.route('/api/templates/<category>/<template_name>/move', methods=['GET'])
def get_move_template_form(category, template_name):
    """Get the move template form data."""
    try:
        # Get all available categories
        all_categories = {}
        custom_categories = load_custom_categories()
        
        # Add built-in categories
        built_in_categories = {
            'network': {'display_name': 'Network', 'icon': 'fas fa-network-wired', 'color': 'primary'},
            'security': {'display_name': 'Security', 'icon': 'fas fa-shield-alt', 'color': 'success'},
            'automation': {'display_name': 'Automation', 'icon': 'fas fa-robot', 'color': 'warning'},
            'monitoring': {'display_name': 'Monitoring', 'icon': 'fas fa-chart-line', 'color': 'info'},
            'community': {'display_name': 'Community', 'icon': 'fas fa-users', 'color': 'secondary'}
        }
        
        all_categories.update(built_in_categories)
        all_categories.update(custom_categories)
        
        # Remove current category from options
        if category in all_categories:
            del all_categories[category]
        
        return jsonify({
            'template_name': template_name,
            'current_category': category,
            'available_categories': all_categories
        })
        
    except Exception as e:
        logger.error(f"Error getting move form data: {e}")
        return jsonify({'error': 'Failed to load move form data'}), 500

@app.route('/test-logos')
def test_logos():
    """Test endpoint to check if logos are accessible."""
    import os
    att_path = os.path.join('static', 'images', 'att-logo.svg')
    cisco_path = os.path.join('static', 'images', 'cisco-logo.svg')
    
    return jsonify({
        'att_exists': os.path.exists(att_path),
        'cisco_exists': os.path.exists(cisco_path),
        'att_size': os.path.getsize(att_path) if os.path.exists(att_path) else 0,
        'cisco_size': os.path.getsize(cisco_path) if os.path.exists(cisco_path) else 0
    })

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
