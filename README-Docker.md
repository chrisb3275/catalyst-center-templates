# Docker Setup for Catalyst Center Templates

This guide will help you run the Catalyst Center Templates application locally using Docker.

## Prerequisites

- Docker Desktop installed on your system
- Docker Compose (usually included with Docker Desktop)
- Git (to clone the repository)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/chrisb3275/catalyst-center-templates.git
cd catalyst-center-templates

# Make the setup script executable
chmod +x scripts/docker-setup.sh

# Run initial setup
./scripts/docker-setup.sh setup
```

### 2. Start the Application

#### Production Mode (Recommended)
```bash
# Start the application
./scripts/docker-setup.sh start

# Or use docker-compose directly
docker-compose up -d
```

#### Development Mode (with hot reloading)
```bash
# Start in development mode
./scripts/docker-setup.sh start-dev

# Or use docker-compose directly
docker-compose -f docker-compose.dev.yml up
```

### 3. Access the Application

- **Main Application**: http://localhost:5000
- **With Nginx** (if enabled): http://localhost:80
- **Health Check**: http://localhost:5000/health

## Docker Commands

### Basic Operations

```bash
# Start the application
docker-compose up -d

# Start in development mode
docker-compose -f docker-compose.dev.yml up

# Stop the application
docker-compose down

# View logs
docker-compose logs -f

# Rebuild and start
docker-compose up --build -d
```

### Advanced Operations

```bash
# Start with Nginx reverse proxy
docker-compose --profile nginx up -d

# Start with database
docker-compose --profile database up -d

# Start everything (app + nginx + database)
docker-compose --profile nginx --profile database up -d

# Clean up everything
docker-compose down -v
docker system prune -f
```

## Configuration

### Environment Variables

You can customize the application by creating a `.env` file:

```bash
# .env
FLASK_ENV=production
FLASK_DEBUG=0
DATABASE_URL=postgresql://catalyst_user:catalyst_password@postgres:5432/catalyst_templates
```

### Volume Mounts

The application uses the following volume mounts:

- `./templates` → `/app/templates` (Template files)
- `./data` → `/app/data` (Category metadata)
- `./logs` → `/app/logs` (Application logs)
- `./output` → `/app/output` (Generated outputs)

### Ports

- **5000**: Main Flask application
- **80**: Nginx (if enabled)
- **443**: Nginx HTTPS (if enabled)
- **5432**: PostgreSQL (if enabled)

## Development

### Hot Reloading

For development with hot reloading:

```bash
# Start development mode
docker-compose -f docker-compose.dev.yml up

# The application will automatically reload when you change files
```

### Debugging

```bash
# View logs in real-time
docker-compose logs -f catalyst-templates

# Access container shell
docker-compose exec catalyst-templates bash

# Check container status
docker-compose ps
```

## Production Deployment

### With Nginx

```bash
# Start with Nginx reverse proxy
docker-compose --profile nginx up -d

# Configure SSL certificates in ./ssl/ directory
# Update nginx.conf for HTTPS
```

### With Database

```bash
# Start with PostgreSQL database
docker-compose --profile database up -d

# The database will persist data in a Docker volume
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using port 5000
   lsof -i :5000
   
   # Kill the process or change the port in docker-compose.yml
   ```

2. **Permission issues**
   ```bash
   # Fix ownership
   sudo chown -R $USER:$USER .
   ```

3. **Container won't start**
   ```bash
   # Check logs
   docker-compose logs catalyst-templates
   
   # Rebuild without cache
   docker-compose build --no-cache
   ```

4. **Database connection issues**
   ```bash
   # Check if database is running
   docker-compose ps
   
   # Check database logs
   docker-compose logs postgres
   ```

### Reset Everything

```bash
# Stop and remove everything
docker-compose down -v
docker-compose -f docker-compose.dev.yml down -v

# Remove all images
docker rmi $(docker images -q)

# Clean up system
docker system prune -a -f

# Start fresh
./scripts/docker-setup.sh setup
./scripts/docker-setup.sh start
```

## File Structure

```
catalyst-center-templates/
├── Dockerfile              # Production Docker image
├── Dockerfile.dev          # Development Docker image
├── docker-compose.yml      # Production compose file
├── docker-compose.dev.yml  # Development compose file
├── nginx.conf              # Nginx configuration
├── .dockerignore           # Docker ignore file
├── scripts/
│   └── docker-setup.sh     # Setup script
└── README-Docker.md        # This file
```

## Security Notes

- The application runs as a non-root user inside the container
- Nginx provides rate limiting and security headers
- Database credentials should be changed in production
- SSL certificates should be properly configured for HTTPS

## Support

If you encounter any issues:

1. Check the logs: `docker-compose logs -f`
2. Verify Docker is running: `docker --version`
3. Check port availability: `netstat -tulpn | grep :5000`
4. Review the troubleshooting section above

For more help, check the main README.md or create an issue on GitHub.
