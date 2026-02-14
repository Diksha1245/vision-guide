# 🚀 Complete Deployment Guide

Step-by-step guide to deploy Vision Guide to production.

## Prerequisites

- GitHub account
- Domain name (optional)
- Cloud provider account (AWS/GCP/Render)

## Part 1: Backend Deployment

### Option A: Render (Easiest - Free Tier)

**Pros**: Free tier, auto-deploy, managed infrastructure
**Cons**: Cold starts, limited resources

#### Steps:

1. **Create Render Account**
   - Visit [render.com](https://render.com)
   - Sign up with GitHub

2. **Create New Web Service**
   - Dashboard → "New" → "Web Service"
   - Connect your GitHub repository
   - Select `ai-navigation-assistant` repo

3. **Configure Service**
   ```
   Name: vision-guide-backend
   Region: Choose closest to users
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Environment Variables** (if needed)
   ```
   MODEL_NAME=yolov8n.pt
   MIN_CONFIDENCE=0.4
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Note your URL: `https://vision-guide-backend.onrender.com`

6. **Test**
   ```bash
   curl https://vision-guide-backend.onrender.com/health
   ```

#### Render Free Tier Limits:
- 750 hours/month
- Sleeps after 15 min inactivity
- 512MB RAM
- Good for demo/testing

### Option B: AWS EC2 (Production)

**Pros**: Full control, better performance
**Cons**: Requires setup, costs ~$30/month

#### Steps:

1. **Launch EC2 Instance**
   ```
   AMI: Ubuntu Server 20.04 LTS
   Instance Type: t2.medium (2 vCPU, 4GB RAM)
   Storage: 20GB SSD
   Security Group:
     - SSH (22) from your IP
     - HTTP (80) from anywhere
     - HTTPS (443) from anywhere
     - Custom TCP (8000) from anywhere
   ```

2. **Connect via SSH**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

3. **Install Dependencies**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python
   sudo apt install python3-pip python3-venv -y
   
   # Install system libraries
   sudo apt install libgl1-mesa-glx libglib2.0-0 -y
   ```

4. **Clone and Setup**
   ```bash
   # Clone repository
   git clone https://github.com/yourusername/ai-navigation-assistant.git
   cd ai-navigation-assistant/backend
   
   # Run setup
   chmod +x setup.sh
   ./setup.sh
   ```

5. **Create Systemd Service**
   ```bash
   sudo nano /etc/systemd/system/vision-guide.service
   ```
   
   Add:
   ```ini
   [Unit]
   Description=Vision Guide Backend API
   After=network.target
   
   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/ai-navigation-assistant/backend
   Environment="PATH=/home/ubuntu/ai-navigation-assistant/backend/venv/bin"
   ExecStart=/home/ubuntu/ai-navigation-assistant/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

6. **Start Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable vision-guide
   sudo systemctl start vision-guide
   sudo systemctl status vision-guide
   ```

7. **Install Nginx (Reverse Proxy)**
   ```bash
   sudo apt install nginx -y
   sudo nano /etc/nginx/sites-available/vision-guide
   ```
   
   Add:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;  # or EC2 IP
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```
   
   ```bash
   sudo ln -s /etc/nginx/sites-available/vision-guide /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

8. **Setup SSL with Let's Encrypt**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d your-domain.com
   ```

9. **Test**
   ```bash
   curl https://your-domain.com/health
   ```

### Option C: Google Cloud Platform

1. **Create VM Instance**
   ```
   Machine type: e2-medium
   Boot disk: Ubuntu 20.04 LTS, 20GB
   Firewall: Allow HTTP/HTTPS
   ```

2. **Follow similar steps as AWS EC2**

3. **Configure Firewall Rules**
   ```bash
   gcloud compute firewall-rules create allow-vision-guide \
       --allow tcp:8000 \
       --source-ranges 0.0.0.0/0
   ```

## Part 2: Frontend Deployment

### Option A: GitHub Pages (Easiest - Free)

1. **Prepare Repository**
   ```bash
   cd frontend
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Create GitHub Repository**
   - Go to github.com → New Repository
   - Name: `vision-guide-frontend`
   - Public repository

3. **Push Code**
   ```bash
   git remote add origin https://github.com/yourusername/vision-guide-frontend.git
   git branch -M main
   git push -u origin main
   ```

4. **Enable GitHub Pages**
   - Repository → Settings → Pages
   - Source: Deploy from branch
   - Branch: main / root
   - Save

5. **Update API URL**
   - Edit `index.html` default API URL:
   ```html
   <input id="apiUrl" value="https://your-backend-url.com">
   ```

6. **Access Site**
   - URL: `https://yourusername.github.io/vision-guide-frontend/`

### Option B: Netlify (Better Performance)

1. **Create Netlify Account**
   - Visit [netlify.com](https://netlify.com)
   - Sign up with GitHub

2. **New Site from Git**
   - Sites → Add new site → Import existing project
   - Choose GitHub
   - Select repository
   - Deploy settings:
     ```
     Build command: (leave empty)
     Publish directory: .
     ```

3. **Deploy**
   - Click "Deploy site"
   - Get URL: `https://random-name.netlify.app`

4. **Custom Domain** (Optional)
   - Site settings → Domain management
   - Add custom domain
   - Update DNS records

5. **Update API URL**
   - Site settings → Environment variables
   - Add: `API_URL=https://your-backend-url.com`

### Option C: Vercel

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Deploy**
   ```bash
   cd frontend
   vercel
   ```

3. **Follow Prompts**
   - Link to existing project or create new
   - Deploy

4. **Production Deploy**
   ```bash
   vercel --prod
   ```

## Part 3: HTTPS Configuration

### Why HTTPS is Required
- Camera API only works over HTTPS (security requirement)
- Exception: `localhost` for development

### Backend HTTPS

**Option 1: Let's Encrypt (Free)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

**Option 2: Cloudflare (Free)**
1. Add domain to Cloudflare
2. Point A record to your server IP
3. Enable "Full SSL/TLS encryption"

### Frontend HTTPS
- GitHub Pages: Automatic HTTPS
- Netlify: Automatic HTTPS
- Vercel: Automatic HTTPS

## Part 4: Custom Domain Setup

### Buy Domain (Optional)
- Namecheap: ~$10/year
- Google Domains: ~$12/year
- GoDaddy: ~$15/year

### DNS Configuration

**Backend (api.yourdomain.com)**
```
Type: A
Name: api
Value: YOUR_SERVER_IP
TTL: 3600
```

**Frontend (yourdomain.com)**

For GitHub Pages:
```
Type: CNAME
Name: @
Value: yourusername.github.io
```

For Netlify:
```
Type: CNAME
Name: @
Value: your-site.netlify.app
```

## Part 5: Monitoring & Maintenance

### Backend Monitoring

**Check Logs**
```bash
# Systemd logs
sudo journalctl -u vision-guide -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

**Monitor Resources**
```bash
# CPU and memory
htop

# Disk usage
df -h

# Network
sudo iftop
```

**Uptime Monitoring**
- Use [UptimeRobot](https://uptimerobot.com) (free)
- Monitor: `https://your-api.com/health`
- Alert via email/SMS

### Frontend Monitoring

**Netlify Analytics** (Built-in)
- Page views
- Bandwidth usage
- Top pages

**Google Analytics** (Free)
Add to `index.html`:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

## Part 6: Scaling & Optimization

### Backend Optimization

**1. Use Gunicorn with Multiple Workers**
```bash
# Install gunicorn
pip install gunicorn

# Update systemd service
ExecStart=.../venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

**2. Add Redis Cache**
```bash
# Install Redis
sudo apt install redis-server

# Update code to cache results
pip install redis
```

**3. Load Balancing**
- Use AWS ELB or Nginx for multiple instances

**4. GPU Acceleration**
- Use AWS EC2 with GPU (g4dn.xlarge)
- Significantly faster inference

### Frontend Optimization

**1. Image Optimization**
```javascript
// Reduce capture resolution
canvas.toDataURL('image/jpeg', 0.7);  // 70% quality
```

**2. Service Worker (Offline Support)**
```javascript
// Register service worker
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js');
}
```

**3. CDN**
- Use Cloudflare for caching static assets

## Part 7: Cost Optimization

### Free Tier Stack
- **Frontend**: GitHub Pages (FREE)
- **Backend**: Render free tier (FREE)
- **Domain**: Freenom (FREE, .tk/.ml domains)
- **SSL**: Let's Encrypt (FREE)
- **Total**: $0/month

### Budget Stack (~$10/month)
- **Frontend**: Netlify (FREE)
- **Backend**: Render paid tier ($7/month)
- **Domain**: Namecheap ($10/year)
- **Total**: ~$8/month

### Production Stack (~$50/month)
- **Frontend**: Netlify Pro ($19/month)
- **Backend**: AWS EC2 t2.medium ($30/month)
- **Domain**: $10/year
- **Total**: ~$50/month

## Part 8: Troubleshooting

### Backend Issues

**Service won't start**
```bash
# Check logs
sudo journalctl -u vision-guide -n 50

# Test manually
cd /home/ubuntu/ai-navigation-assistant/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Out of memory**
```bash
# Check memory
free -h

# Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Frontend Issues

**Camera not working**
- Ensure HTTPS is enabled
- Check browser permissions
- Test on different device

**API connection failed**
- Verify API URL in settings
- Check CORS headers
- Test API directly: `curl https://api-url/health`

## Part 9: Security Checklist

- [ ] HTTPS enabled on both frontend and backend
- [ ] Firewall configured (only necessary ports open)
- [ ] Regular system updates
- [ ] Strong SSH key (disable password auth)
- [ ] Rate limiting on API
- [ ] CORS restricted to frontend domain
- [ ] Logs monitored for suspicious activity
- [ ] Backups configured

## Part 10: Next Steps

After deployment:
1. ✅ Test from multiple devices
2. ✅ Monitor performance for 24 hours
3. ✅ Gather user feedback
4. ✅ Set up analytics
5. ✅ Create backup strategy
6. ✅ Document any issues
7. ✅ Plan for scaling

---

## Quick Reference

### Important URLs
- Frontend: `https://your-site.com`
- Backend API: `https://api.your-site.com`
- API Docs: `https://api.your-site.com/docs`

### Commands
```bash
# Restart backend
sudo systemctl restart vision-guide

# View logs
sudo journalctl -u vision-guide -f

# Update code
cd ~/ai-navigation-assistant
git pull
sudo systemctl restart vision-guide

# Check status
systemctl status vision-guide
curl https://api.your-site.com/health
```

---

**Deployment Complete! 🎉**

Your Vision Guide is now live and helping visually impaired users navigate the world!