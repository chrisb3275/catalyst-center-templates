# Development Workflow Guide

This document explains the complete development workflow for the Automation-X Catalyst Center - AT&T application, covering local development with Docker, Git version control, and automatic deployment to Render.

## 🔄 Complete Development to Deployment Workflow

### Overview
```
Local Development → Git → GitHub → Render → Live Application
     ↓              ↓       ↓        ↓           ↓
  Docker Build   Commit   Push   Auto-Deploy   Production
```

## 🛠️ Local Development with Docker

### Prerequisites
- Docker Desktop installed
- Git configured
- Code editor (VS Code, PyCharm, etc.)

### 1. Setting Up Local Environment

```bash
# Clone the repository
git clone https://github.com/chrisb3275/catalyst-center-templates.git
cd catalyst-center-templates

# Start development environment
docker-compose up -d --build
```

### 2. Making Changes

```bash
# Edit your code
vim app.py                    # or use any editor
vim templates/index.html
vim static/css/style.css

# Test changes locally
docker-compose up -d --build  # Rebuilds container with changes
curl http://localhost:8080    # Test the application
```

### 3. Development Features

#### Hot Reloading (Development Mode)
```bash
# Use development compose file for hot reloading
docker-compose -f docker-compose.dev.yml up -d

# Changes to Python files automatically reload
# Changes to templates/static require container restart
```

#### Debugging
```bash
# View application logs
docker-compose logs catalyst-templates

# Access container shell
docker-compose exec catalyst-templates /bin/bash

# Check container status
docker-compose ps
```

## 📝 Git Version Control

### 1. Making Changes
```bash
# Check what files have changed
git status

# Stage specific files
git add app.py
git add templates/new-template.html

# Or stage all changes
git add .

# Commit with descriptive message
git commit -m "Add new template category management feature"
```

### 2. Pushing to GitHub
```bash
# Push to main branch
git push origin main

# Push to feature branch
git push origin feature/new-feature
```

### 3. Branch Strategy
```bash
# Create feature branch
git checkout -b feature/template-search

# Make changes and commit
git add .
git commit -m "Implement advanced template search"

# Push feature branch
git push origin feature/template-search

# Merge to main (via GitHub PR or locally)
git checkout main
git merge feature/template-search
git push origin main
```

## ☁️ Render Cloud Deployment

### Automatic Deployment Process

1. **Git Push Triggers Deployment**
   ```bash
   git push origin main
   # ↓
   # Render detects new commit
   # ↓
   # Automatically starts build process
   # ↓
   # Deploys to production
   ```

2. **Build Process on Render**
   ```yaml
   # Render automatically:
   - Clones repository from GitHub
   - Installs Python dependencies
   - Builds application
   - Deploys to cloud infrastructure
   - Provides HTTPS URL
   ```

3. **Deployment Configuration**
   ```yaml
   # render.yaml (if using)
   services:
     - type: web
       name: catalyst-center-templates
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: gunicorn --bind 0.0.0.0:$PORT app:app
   ```

### Manual Deployment Options

#### Option 1: Force Redeploy
1. Go to Render Dashboard
2. Select your service
3. Click "Manual Deploy" → "Deploy latest commit"

#### Option 2: Deploy Specific Branch
1. Go to Render Dashboard
2. Select your service
3. Go to Settings → Build & Deploy
4. Change branch and redeploy

## 🔧 Development vs Production

### Local Docker (Development)
| Feature | Description |
|---------|-------------|
| **Speed** | Fast iteration, instant feedback |
| **Control** | Full control over environment |
| **Debugging** | Full access to logs and tools |
| **Data** | Persistent on your machine |
| **Access** | Localhost only |
| **Cost** | Free |

### Render (Production)
| Feature | Description |
|---------|-------------|
| **Speed** | 2-3 minute deployment time |
| **Control** | Managed by Render |
| **Debugging** | Limited to Render logs |
| **Data** | Managed by Render |
| **Access** | Global HTTPS URL |
| **Cost** | Free tier available |

## 🚀 Best Practices

### 1. Development Workflow
```bash
# 1. Make changes locally
vim app.py

# 2. Test with Docker
docker-compose up -d --build
curl http://localhost:8080

# 3. Commit changes
git add app.py
git commit -m "Fix search functionality"

# 4. Push to GitHub
git push origin main

# 5. Monitor Render deployment
# Check Render dashboard for status
```

### 2. Code Quality
```bash
# Run linting before committing
python -m flake8 app.py
python -m black app.py

# Test functionality
python -m pytest tests/
```

### 3. Commit Messages
```bash
# Good commit messages
git commit -m "Fix search functionality - handle device_types dictionaries"
git commit -m "Add dark mode toggle to navigation"
git commit -m "Update template categories with new icons"

# Bad commit messages
git commit -m "fix"
git commit -m "update"
git commit -m "changes"
```

## 🐛 Troubleshooting

### Local Docker Issues
```bash
# Container won't start
docker-compose down
docker-compose up -d --build

# Permission issues
sudo chown -R $USER:$USER .

# Port already in use
docker-compose down
lsof -ti:8080 | xargs kill -9
docker-compose up -d
```

### Render Deployment Issues
```bash
# Check build logs in Render dashboard
# Common issues:
# - Missing dependencies in requirements.txt
# - Syntax errors in Python code
# - Missing environment variables
# - Port binding issues
```

### Git Issues
```bash
# Undo last commit (before push)
git reset --soft HEAD~1

# Undo last commit (after push)
git revert HEAD
git push origin main

# Merge conflicts
git status
# Edit conflicted files
git add .
git commit -m "Resolve merge conflicts"
```

## 📊 Monitoring and Maintenance

### Local Monitoring
```bash
# Check container health
docker-compose ps

# View logs
docker-compose logs -f catalyst-templates

# Resource usage
docker stats
```

### Production Monitoring
- **Render Dashboard**: Monitor deployment status
- **Application Logs**: View in Render dashboard
- **Health Check**: `https://your-app.onrender.com/health`
- **Performance**: Monitor response times and errors

## 🔄 Alternative Deployment Methods

### Docker Hub + Watchtower
```yaml
# For advanced users who want more control
version: '3.8'
services:
  app:
    image: yourusername/catalyst-center-templates:latest
    ports:
      - "8080:5000"
  
  watchtower:
    image: containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: --interval 30
```

### GitHub Actions + Docker
```yaml
# .github/workflows/docker.yml
name: Docker Build and Deploy
on:
  push:
    branches: [ main ]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Build Docker image
      run: docker build -t catalyst-center-templates .
    - name: Deploy to server
      run: |
        docker stop catalyst-app || true
        docker run -d --name catalyst-app -p 8080:5000 catalyst-center-templates
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Render Documentation](https://render.com/docs)
- [Git Best Practices](https://git-scm.com/doc)
- [Flask Documentation](https://flask.palletsprojects.com/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with Docker
5. Commit and push your changes
6. Create a Pull Request
7. Monitor Render deployment after merge

---

**Need Help?** Check the troubleshooting section above or create an issue in the GitHub repository.
