# Quick Reference Guide

## 🚀 Essential Commands

### Local Development
```bash
# Start application
docker-compose up -d --build

# View logs
docker-compose logs -f catalyst-templates

# Stop application
docker-compose down

# Restart with changes
docker-compose down && docker-compose up -d --build
```

### Git Workflow
```bash
# Check status
git status

# Stage changes
git add .

# Commit changes
git commit -m "Descriptive message"

# Push to GitHub
git push origin main
```

### Testing
```bash
# Test local app
curl http://localhost:8080

# Test health endpoint
curl http://localhost:8080/health

# Test search
curl "http://localhost:8080/search?q=test"
```

## 🔧 Troubleshooting

### Common Issues
| Problem | Solution |
|---------|----------|
| Port 8080 in use | `lsof -ti:8080 \| xargs kill -9` |
| Container won't start | `docker-compose down && docker-compose up -d --build` |
| Changes not reflected | Restart container or check volume mounts |
| Search not working | Check logs: `docker-compose logs catalyst-templates` |

### Useful Commands
```bash
# Check running containers
docker ps

# View container logs
docker-compose logs catalyst-templates

# Access container shell
docker-compose exec catalyst-templates /bin/bash

# Check disk usage
docker system df

# Clean up unused containers
docker system prune
```

## 📱 URLs

- **Local Development**: http://localhost:8080
- **Health Check**: http://localhost:8080/health
- **API Endpoint**: http://localhost:8080/api/templates
- **Search**: http://localhost:8080/search?q=query

## 📚 Documentation

- **[DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md)** - Complete workflow guide
- **[README-Docker.md](README-Docker.md)** - Docker setup
- **[DEPLOY_TO_RENDER.md](DEPLOY_TO_RENDER.md)** - Render deployment
- **[README.md](README.md)** - Main project documentation

## 🎯 Development Tips

1. **Always test locally** before pushing to GitHub
2. **Use descriptive commit messages**
3. **Check Render dashboard** after pushing
4. **Monitor logs** for errors
5. **Keep documentation updated**

---

**Need Help?** Check the full documentation or create an issue in the repository.
