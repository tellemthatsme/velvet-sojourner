# API Documentation

## Prompt API (Port 5000)

### Endpoints

#### Health Check
```bash
GET http://localhost:5000/api/health
```

#### List Prompts
```bash
GET http://localhost:5000/api/prompts
GET http://localhost:5000/api/prompts?tag=python
GET http://localhost:5000/api/prompts?category=code
GET http://localhost:5000/api/prompts?favorite=true
GET http://localhost:5000/api/prompts?search=query
```

#### Create Prompt
```bash
POST http://localhost:5000/api/prompts
Content-Type: application/json

{
  "title": "My Prompt",
  "content": "You are a helpful assistant...",
  "description": "A useful prompt",
  "tags": ["python", "coding"],
  "category": "code"
}
```

#### Get Prompt
```bash
GET http://localhost:5000/api/prompts/{id}
```

#### Update Prompt
```bash
PUT http://localhost:5000/api/prompts/{id}
Content-Type: application/json

{
  "title": "Updated Title",
  "content": "Updated content..."
}
```

#### Delete Prompt
```bash
DELETE http://localhost:5000/api/prompts/{id}
```

#### Toggle Favorite
```bash
POST http://localhost:5000/api/prompts/{id}/favorite
```

#### Get Versions
```bash
GET http://localhost:5000/api/prompts/{id}/versions
```

#### Restore Version
```bash
POST http://localhost:5000/api/prompts/{id}/restore
Content-Type: application/json

{
  "version": 2
}
```

#### Search
```bash
GET http://localhost:5000/api/search?q=query
```

#### List Tags
```bash
GET http://localhost:5000/api/tags
```

#### List Categories
```bash
GET http://localhost:5000/api/categories
```

#### Export All
```bash
GET http://localhost:5000/api/export
```

#### Import
```bash
POST http://localhost:5000/api/import
Content-Type: application/json

{
  "prompts": [...],
  "replace": false
}
```

#### Statistics
```bash
GET http://localhost:5000/api/stats
```

## Search API (Port 5001)

### Endpoints

#### Health Check
```bash
GET http://localhost:5001/api/health
```

#### Search
```bash
GET http://localhost:5001/api/search?q=query
GET http://localhost:5001/api/search?q=query&regex=true
GET http://localhost:5001/api/search?q=query&case=true
GET http://localhost:5001/api/search?q=query&limit=50
```

#### Search Files
```bash
GET http://localhost:5001/api/search/files?q=query
```

#### Get File
```bash
GET http://localhost:5001/api/file?path=./docs/readme.md
```

#### List Files
```bash
GET http://localhost:5001/api/list
```

#### Statistics
```bash
GET http://localhost:5001/api/stats
```

#### Reindex
```bash
POST http://localhost:5001/api/reindex
```

## Response Formats

### Success Response
```json
{
  "status": "ok",
  "data": {...}
}
```

### Error Response
```json
{
  "error": "Description of error"
}
```

### List Response
```json
{
  "count": 10,
  "prompts": [...]
}
```

### Search Response
```json
{
  "query": "search term",
  "count": 5,
  "total_found": 10,
  "search_time": 0.123,
  "results": [...]
}
```
