# AI Agent Starter Kit - Deployment Guide
## Deploy Your AI Agent Platform in Under 10 Minutes

---

## Quick Deploy Options

### Option 1: Railway (Recommended for Beginners)

**Time:** 5 minutes | **Cost:** $5-50/month | **Difficulty:** Easy

1. **Fork the repository** to your GitHub account
2. **Click Deploy:** [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)
3. **Add environment variables** in Railway dashboard:
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `LITELLM_MASTER_KEY`
4. **Done!** Your API will be live at `https://your-app.railway.app`

**Pros:**
- One-click deploy
- Automatic HTTPS
- Built-in database
- Easy scaling

**Cons:**
- Vendor lock-in
- Costs can scale quickly

---

### Option 2: Vercel (Serverless)

**Time:** 3 minutes | **Cost:** Free-$20/month | **Difficulty:** Easy

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Deploy:**
   ```bash
   cd ai-agent-starter-kit
   vercel --prod
   ```

3. **Add environment variables:**
   ```bash
   vercel env add OPENAI_API_KEY
   vercel env add ANTHROPIC_API_KEY
   ```

**Pros:**
- Generous free tier
- Global CDN
- Instant deploys

**Cons:**
- Function timeout limits (10s hobby, 60s pro)
- Cold starts

---

### Option 3: Docker (Self-Hosted)

**Time:** 10 minutes | **Cost:** $5-100/month | **Difficulty:** Medium

1. **Install Docker:**
   ```bash
   # macOS
   brew install docker

   # Ubuntu/Debian
   sudo apt-get install docker.io docker-compose

   # Windows
   # Download Docker Desktop
   ```

2. **Clone and configure:**
   ```bash
   git clone https://github.com/yourusername/ai-agent-starter-kit.git
   cd ai-agent-starter-kit
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Launch:**
   ```bash
   docker-compose up -d
   ```

4. **Verify:**
   ```bash
   curl http://localhost:3000
   ```

**Pros:**
- Full control
- No vendor lock-in
- Runs anywhere

**Cons:**
- Requires server management
- Manual scaling

---

### Option 4: AWS/GCP/Azure (Enterprise)

**Time:** 30 minutes | **Cost:** $50-500/month | **Difficulty:** Hard

See `deployment/cloud/` directory for:
- Terraform configurations
- Kubernetes manifests
- CloudFormation templates

---

## Post-Deployment Setup

### 1. Configure API Keys

Add your LLM provider keys:

```bash
# For Docker
docker-compose exec gateway python setup.py

# For Railway
railway variables set OPENAI_API_KEY=sk-...

# For Vercel
vercel env add OPENAI_API_KEY
```

### 2. Test the API

```bash
# Health check
curl https://your-app.url/

# List models
curl https://your-app.url/v1/models \
  -H "X-API-Key: your-api-key"

# Run an agent
curl -X POST https://your-app.url/v1/agents/run \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "agent_type": "crewai",
    "task": "Research the latest AI trends",
    "model": "gpt-4o"
  }'
```

### 3. Set Up Monitoring

Enable these integrations:
- **Langfuse:** LLM observability
- **Sentry:** Error tracking
- **Prometheus:** Metrics
- **Grafana:** Dashboards

### 4. Configure Custom Domain

**Railway:**
```bash
railway domain add yourdomain.com
```

**Vercel:**
```bash
vercel domains add yourdomain.com
```

**Docker (with Nginx):**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
    }
}
```

---

## Scaling Guide

### Vertical Scaling (Bigger Server)

```yaml
# docker-compose.yml
services:
  gateway:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
```

### Horizontal Scaling (More Servers)

```yaml
# docker-compose.yml
services:
  gateway:
    deploy:
      replicas: 3
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Auto-Scaling (Kubernetes)

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gateway
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: gateway
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: gateway-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: gateway
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Security Checklist

Before going live:

- [ ] Change default API keys
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Set up rate limiting
- [ ] Configure CORS properly
- [ ] Enable authentication
- [ ] Set up audit logging
- [ ] Restrict database access
- [ ] Use secrets manager (not env vars in production)
- [ ] Enable DDoS protection
- [ ] Set up backups

---

## Troubleshooting

### Common Issues

**"Connection refused"**
```bash
# Check if containers are running
docker-compose ps

# Check logs
docker-compose logs gateway
```

**"Rate limit exceeded"**
```bash
# Add more accounts to rate manager
# Or upgrade LLM provider plan
```

**"Out of memory"**
```bash
# Increase Docker memory limit
# Or scale horizontally
```

**"CORS errors"**
```bash
# Update CORS_ORIGINS in .env
CORS_ORIGINS=https://yourdomain.com
```

---

## Production Checklist

- [ ] SSL certificate installed
- [ ] Custom domain configured
- [ ] Monitoring enabled
- [ ] Alerts configured
- [ ] Backups scheduled
- [ ] Documentation updated
- [ ] Team access granted
- [ ] Billing alerts set
- [ ] Disaster recovery plan
- [ ] Load testing completed

---

## Support

Need help deploying?

- 📚 [Documentation](https://docs.aiagentkit.com)
- 💬 [Discord Community](https://discord.gg/aiagentkit)
- 📧 [Email Support](mailto:support@aiagentkit.com)
- 🐛 [GitHub Issues](https://github.com/yourusername/ai-agent-starter-kit/issues)

---

**Happy Deploying! 🚀**
