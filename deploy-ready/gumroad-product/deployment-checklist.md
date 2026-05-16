# Deployment Checklist

## Pre-Deployment
- [ ] README.md reviewed
- [ ] .env.example configured
- [ ] Dependencies installed (`pip install -r requirements.txt` or `npm install`)
- [ ] Tests passing (`pytest` or `npm test`)
- [ ] Dockerfile present
- [ ] docker-compose.yml present (optional but recommended)

## Docker Build
- [ ] Image builds successfully: `docker build -t {repo_name} .`
- [ ] Container runs: `docker run -p 8080:8080 {repo_name}`
- [ ] Health endpoint responds: `curl http://localhost:8080/health`

## Production
- [ ] Environment variables set
- [ ] SSL configured (Traefik/Nginx)
- [ ] Logging enabled
- [ ] Monitoring configured (Prometheus/Grafana)
- [ ] Backup strategy defined
