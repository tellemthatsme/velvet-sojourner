# API Documentation
## [REPO_NAME]

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
Bearer token required

### Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| POST | /deploy | Deploy service |

### Example Request
```bash
curl -X POST http://localhost:8000/api/v1/deploy \
  -H "Content-Type: application/json" \
  -d '{"repo": "my-repo"}'
```
