# Security Configuration Guide

## 🔒 **Authentication Setup**

### **Environment Variables for Render:**

Set these environment variables in your Render dashboard:

```bash
# Enable Authentication
AUTH_ENABLED=true

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=CXlabs.123

# IP Whitelist (optional - comma-separated)
ALLOWED_IPS=192.168.1.0/24,10.0.0.0/8

# Secret Key (generate a strong random key)
SECRET_KEY=your-super-secret-key-change-this-in-production
```

### **How to Set Environment Variables in Render:**

1. **Go to your Render Dashboard**
2. **Select your service**
3. **Go to "Environment" tab**
4. **Add the variables above**
5. **Redeploy your service**

## 🛡️ **Security Features Implemented:**

### **1. Authentication**
- ✅ **Login/Logout system** with session management
- ✅ **Password hashing** using Werkzeug security
- ✅ **Session-based authentication**
- ✅ **Protected routes** with @require_auth decorator

### **2. Access Control**
- ✅ **IP whitelisting** (optional)
- ✅ **Protected API endpoints**
- ✅ **Secure session management**

### **3. Security Headers** (Recommended)
Add these to your Render configuration:

```yaml
# render.yaml
services:
  - type: web
    name: catalyst-center-templates
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT app:app
    envVars:
      - key: AUTH_ENABLED
        value: true
      - key: ADMIN_USERNAME
        value: admin
      - key: ADMIN_PASSWORD
        value: CXlabs.123
      - key: SECRET_KEY
        generateValue: true
```

## 🔧 **Additional Security Measures:**

### **1. HTTPS (Automatic on Render)**
- ✅ **SSL/TLS encryption** provided by Render
- ✅ **Secure cookies** for session management

### **2. Rate Limiting** (Optional)
Consider adding rate limiting for API endpoints:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/templates')
@limiter.limit("10 per minute")
@require_auth
def api_templates():
    # ... existing code
```

### **3. Database Security** (For Production)
Replace the simple user storage with a database:

```python
# Use SQLAlchemy or similar for user management
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
```

## 🚀 **Deployment Steps:**

### **1. Enable Authentication:**
```bash
# Set in Render environment variables
AUTH_ENABLED=true
ADMIN_USERNAME=admin
ADMIN_PASSWORD=CXlabs.123
SECRET_KEY=your-secret-key
```

### **2. Test Authentication:**
1. **Visit your Render URL**
2. **You should be redirected to login**
3. **Login with admin/CXlabs.123**
4. **Access the application**

### **3. Optional: IP Whitelisting**
```bash
# Add to Render environment variables
ALLOWED_IPS=your-office-ip,your-home-ip
```

## 🔍 **Security Testing:**

### **Test Authentication:**
```bash
# Test without authentication (should redirect to login)
curl -I https://your-app.onrender.com/api/templates

# Test with authentication
curl -H "Cookie: session=your-session-cookie" https://your-app.onrender.com/api/templates
```

### **Test IP Whitelisting:**
```bash
# Test from allowed IP (should work)
curl https://your-app.onrender.com/

# Test from blocked IP (should return 403)
curl https://your-app.onrender.com/
```

## 📋 **Security Checklist:**

- ✅ **Authentication enabled**
- ✅ **Strong passwords**
- ✅ **HTTPS enabled** (Render default)
- ✅ **Session security**
- ✅ **API protection**
- ⚠️ **IP whitelisting** (optional)
- ⚠️ **Rate limiting** (optional)
- ⚠️ **Database security** (for production)

## 🆘 **Troubleshooting:**

### **Can't Access After Enabling Auth:**
1. Check environment variables in Render
2. Verify AUTH_ENABLED=true
3. Check username/password are correct
4. Clear browser cookies and try again

### **IP Whitelist Issues:**
1. Check your current IP: `curl ifconfig.me`
2. Add your IP to ALLOWED_IPS
3. Redeploy the service

### **Session Issues:**
1. Check SECRET_KEY is set
2. Clear browser cookies
3. Try incognito/private browsing
