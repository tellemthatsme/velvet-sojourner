# AgentForge Platform Quickstart

## Requirements
- Docker + Docker Compose
- 4GB RAM minimum
- Domain (optional, localhost works)

## Start Everything
```bash
docker-compose up -d
```

## Access Points
- Dashboard: http://localhost:8080
- API Docs: http://localhost:8000/docs
- n8n: http://localhost:5678
- Open WebUI: http://localhost:3000
- Grafana: http://localhost:3001

## Add Your API Keys
Edit `.env`:
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
```

## First Deploy
```bash
cd deployer
pip install -r requirements.txt
uvicorn main:app --reload
```

For full docs see AGENTFORGE.md in project root.
