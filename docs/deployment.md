# Deployment Guide

This guide covers various deployment options for making your Catalyst Center Templates project publicly accessible.

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Access the application:**
   Open your browser to `http://localhost:5000`

## Deployment Options

### 1. Heroku (Recommended for beginners)

Heroku is the easiest way to deploy your application publicly.

#### Prerequisites
- Heroku account
- Heroku CLI installed

#### Steps

1. **Login to Heroku:**
   ```bash
   heroku login
   ```

2. **Create a new app:**
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key-here
   heroku config:set FLASK_ENV=production
   ```

4. **Deploy:**
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```

5. **Open your app:**
   ```bash
   heroku open
   ```

### 2. Docker Deployment

#### Using Docker Compose (Recommended)

1. **Build and run:**
   ```bash
   docker-compose up -d
   ```

2. **Access the application:**
   - HTTP: `http://localhost`
   - HTTPS: `https://localhost` (if SSL certificates are configured)

#### Using Docker directly

1. **Build the image:**
   ```bash
   docker build -t catalyst-center-templates .
   ```

2. **Run the container:**
   ```bash
   docker run -p 5000:5000 catalyst-center-templates
   ```

### 3. Cloud Platform Deployment

#### Google Cloud Platform (GCP)

1. **Install Google Cloud SDK**

2. **Deploy to App Engine:**
   ```bash
   gcloud app deploy
   ```

3. **Access your app:**
   ```bash
   gcloud app browse
   ```

#### Amazon Web Services (AWS)

1. **Deploy using Elastic Beanstalk:**
   ```bash
   eb init
   eb create production
   eb deploy
   ```

2. **Access your app:**
   ```bash
   eb open
   ```

#### Microsoft Azure

1. **Deploy using Azure App Service:**
   ```bash
   az webapp up --name your-app-name --resource-group your-resource-group
   ```

### 4. VPS/Server Deployment

#### Using Nginx + Gunicorn

1. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3-pip nginx
   pip3 install -r requirements.txt
   ```

2. **Configure Nginx:**
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/catalyst-templates
   sudo ln -s /etc/nginx/sites-available/catalyst-templates /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

3. **Run with Gunicorn:**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
   ```

4. **Set up SSL (Let's Encrypt):**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

## Environment Configuration

### Required Environment Variables

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

### Security Considerations

1. **Change the secret key** in production
2. **Use HTTPS** for all deployments
3. **Set up proper firewall rules**
4. **Regular security updates**
5. **Monitor logs** for suspicious activity

## Monitoring and Maintenance

### Health Checks

The application includes a health check endpoint:
- URL: `/health`
- Returns: JSON with status information

### Logging

Logs are written to:
- Console output (for development)
- `logs/catalyst_center.log` (for production)

### Performance Optimization

1. **Enable gzip compression** (configured in nginx.conf)
2. **Use a CDN** for static files
3. **Implement caching** for frequently accessed data
4. **Monitor resource usage**

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Find process using port 5000
   lsof -i :5000
   # Kill the process
   kill -9 <PID>
   ```

2. **Permission denied:**
   ```bash
   # Make sure the app has write permissions
   chmod -R 755 /path/to/your/app
   ```

3. **SSL certificate issues:**
   ```bash
   # Test SSL configuration
   openssl s_client -connect your-domain.com:443
   ```

### Debug Mode

For development, you can enable debug mode:
```bash
export FLASK_ENV=development
python app.py
```

## Scaling

### Horizontal Scaling

1. **Load balancer** (nginx, HAProxy)
2. **Multiple app instances**
3. **Database clustering** (if using a database)

### Vertical Scaling

1. **Increase server resources**
2. **Optimize application code**
3. **Use caching strategies**

## Backup and Recovery

### Regular Backups

1. **Application code** (Git repository)
2. **Configuration files**
3. **Log files**
4. **Database** (if applicable)

### Recovery Procedures

1. **Code deployment** from Git
2. **Configuration restoration**
3. **Service restart**
4. **Health check verification**

## Support

For deployment issues:
1. Check the logs
2. Verify environment variables
3. Test locally first
4. Check firewall settings
5. Review security groups (cloud platforms)

## Next Steps

After successful deployment:
1. Set up monitoring (Prometheus, Grafana)
2. Configure automated backups
3. Set up CI/CD pipeline
4. Implement security scanning
5. Plan for disaster recovery
