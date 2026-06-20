# LOUS Deployment Guide

## Deployment Options

### 1. Docker Container (Recommended)

#### Single Container Deployment

```bash
# Build the image
docker build -t lous:latest .

# Run the container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/backend/db:/app/backend/db \
  -v $(pwd)/backend/data:/app/backend/data \
  --name lous \
  lous:latest

# Check logs
docker logs -f lous
```

#### Docker Compose (Easier)

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### 2. Cloud Deployment

#### AWS EC2

1. **Launch EC2 Instance:**
   - Ubuntu 22.04 LTS
   - t3.medium or larger
   - Open ports: 80, 443, 8000

2. **Install Docker:**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker ubuntu
   ```

3. **Deploy:**
   ```bash
   git clone <your-repo>
   cd lous
   docker-compose up -d
   ```

4. **Setup Nginx (Optional):**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

#### DigitalOcean Droplet

Similar to EC2, use Docker on a droplet with at least 2GB RAM.

#### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/lous

# Deploy
gcloud run deploy lous \
  --image gcr.io/PROJECT_ID/lous \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### 3. Traditional Server Deployment

#### Requirements
- Ubuntu 22.04 or similar
- Python 3.11+
- Node.js 20+
- Nginx
- Supervisor (for process management)

#### Setup

1. **Install Dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3.11 python3-pip nodejs npm nginx supervisor
   ```

2. **Build Frontend:**
   ```bash
   cd lous/frontend
   npm install
   npm run build
   ```

3. **Setup Backend:**
   ```bash
   cd lous/backend
   pip install -r requirements.txt
   ```

4. **Configure Supervisor:**
   ```ini
   [program:lous]
   command=/usr/bin/python3 /path/to/lous/backend/main.py
   directory=/path/to/lous/backend
   user=www-data
   autostart=true
   autorestart=true
   stderr_logfile=/var/log/lous.err.log
   stdout_logfile=/var/log/lous.out.log
   ```

5. **Configure Nginx:**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       # Serve frontend static files
       location / {
           root /path/to/lous/frontend/dist;
           try_files $uri $uri/ /index.html;
       }
       
       # Proxy API requests
       location /api {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

## Environment Variables

Create a `.env` file in the backend directory:

```env
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_PATH=./db/lous.db
CHROMA_PERSIST_DIRECTORY=./data/chroma

# Add your API keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

## SSL/HTTPS Setup

### Using Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8000/api/health
```

### Docker Health Check

The docker-compose.yml includes a health check that runs every 30 seconds.

### Logs

```bash
# Docker logs
docker-compose logs -f

# Supervisor logs
tail -f /var/log/lous.out.log
tail -f /var/log/lous.err.log
```

## Backup Strategy

### Database Backup

```bash
# Backup SQLite database
cp backend/db/lous.db backend/db/lous.db.backup-$(date +%Y%m%d)

# Automated daily backup (cron)
0 2 * * * cp /path/to/lous/backend/db/lous.db /backups/lous.db.$(date +\%Y\%m\%d)
```

### Full System Backup

```bash
# Backup entire application
tar -czf lous-backup-$(date +%Y%m%d).tar.gz lous/
```

## Security Checklist

- [ ] Change default passwords
- [ ] Enable HTTPS/SSL
- [ ] Set up firewall (UFW)
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets
- [ ] Enable database encryption
- [ ] Set up rate limiting
- [ ] Configure logging
- [ ] Enable authentication tokens (JWT)
- [ ] Regular security updates

## Scaling

### Horizontal Scaling

Use a load balancer (Nginx/HAProxy) with multiple instances:

```yaml
# docker-compose with multiple replicas
services:
  lous:
    deploy:
      replicas: 3
```

### Database Scaling

For production, consider:
- PostgreSQL instead of SQLite
- Redis for session management
- Separate vector database instance

## Performance Optimization

1. **Frontend:**
   - Enable Vite build optimizations
   - Use CDN for static assets
   - Enable gzip compression

2. **Backend:**
   - Use Gunicorn with multiple workers
   - Enable response caching
   - Optimize database queries

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs

# Check disk space
df -h

# Check permissions
ls -la backend/db backend/data
```

### Database locked

```bash
# Stop all instances
docker-compose down

# Check for stale locks
rm backend/db/*.lock

# Restart
docker-compose up -d
```

### High memory usage

- Increase container memory limits
- Optimize ChromaDB settings
- Use pagination for large datasets

## Support

For deployment issues, check:
- Application logs
- Docker logs
- System logs (`journalctl -xe`)
