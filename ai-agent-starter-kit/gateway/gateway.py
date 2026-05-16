# AI Agent Starter Kit - Gateway API
# Unified API for accessing all agents and MCP servers

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
import redis
import json
import os
from datetime import datetime

app = FastAPI(
    title="AI Agent Starter Kit API",
    description="Unified gateway for AI agents and MCP servers",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
try:
    redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
except:
    redis_client = None

# Configuration
LITELLM_URL = os.getenv("LITELLM_URL", "http://litellm:4000")
MCP_HUB_URL = os.getenv("MCP_HUB_URL", "http://mcp-hub:3001")

# =============================================================================
# Models
# =============================================================================

class AgentRequest(BaseModel):
    agent_type: str = "crewai"
    task: str
    context: Optional[Dict[str, Any]] = {}
    model: Optional[str] = "gpt-4o"
    temperature: Optional[float] = 0.7

class AgentResponse(BaseModel):
    success: bool
    result: str
    agent_type: str
    model_used: str
    tokens_used: Optional[int] = None
    duration_ms: Optional[int] = None

class MCPRequest(BaseModel):
    server: str
    tool: str
    params: Optional[Dict[str, Any]] = {}

class HealthStatus(BaseModel):
    status: str
    services: Dict[str, str]
    version: str

# =============================================================================
# Authentication
# =============================================================================

async def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key (simplified - implement proper auth in production)"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    # In production, validate against database
    return x_api_key

# =============================================================================
# Routes
# =============================================================================

@app.get("/", response_model=HealthStatus)
async def root():
    """Health check endpoint"""
    services = {}
    
    # Check LiteLLM
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{LITELLM_URL}/health", timeout=5)
            services["litellm"] = "healthy" if resp.status_code == 200 else "unhealthy"
    except:
        services["litellm"] = "unavailable"
    
    # Check MCP Hub
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{MCP_HUB_URL}/health", timeout=5)
            services["mcp_hub"] = "healthy" if resp.status_code == 200 else "unhealthy"
    except:
        services["mcp_hub"] = "unavailable"
    
    # Check Redis
    services["redis"] = "healthy" if redis_client and redis_client.ping() else "unavailable"
    
    return HealthStatus(
        status="operational" if all(s == "healthy" for s in services.values()) else "degraded",
        services=services,
        version="1.0.0"
    )

@app.post("/v1/agents/run", response_model=AgentResponse)
async def run_agent(
    request: AgentRequest,
    api_key: str = Depends(verify_api_key)
):
    """Run an AI agent with specified configuration"""
    start_time = datetime.now()
    
    try:
        # Route to appropriate agent service
        agent_urls = {
            "crewai": "http://crewai-agent:8000",
            "autogen": "http://autogen-agent:8000",
            "langchain": "http://langchain-agent:8000",
        }
        
        agent_url = agent_urls.get(request.agent_type)
        if not agent_url:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {request.agent_type}")
        
        # Forward request to agent service
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{agent_url}/run",
                json=request.dict(),
                timeout=60
            )
            
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
            
            result = resp.json()
        
        duration = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return AgentResponse(
            success=True,
            result=result.get("output", ""),
            agent_type=request.agent_type,
            model_used=request.model,
            tokens_used=result.get("tokens_used"),
            duration_ms=duration
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/agents/types")
async def list_agent_types(api_key: str = Depends(verify_api_key)):
    """List available agent types"""
    return {
        "agents": [
            {
                "id": "crewai",
                "name": "CrewAI Multi-Agent",
                "description": "Collaborative agents for complex workflows",
                "status": "available"
            },
            {
                "id": "autogen",
                "name": "AutoGen Conversational",
                "description": "Microsoft's conversational agent framework",
                "status": "available"
            },
            {
                "id": "langchain",
                "name": "LangChain Agent",
                "description": "General-purpose LLM agents",
                "status": "available"
            }
        ]
    }

@app.post("/v1/mcp/invoke")
async def invoke_mcp(
    request: MCPRequest,
    api_key: str = Depends(verify_api_key)
):
    """Invoke an MCP server tool"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{MCP_HUB_URL}/invoke",
                json=request.dict(),
                timeout=30
            )
            
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
            
            return resp.json()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/mcp/servers")
async def list_mcp_servers(api_key: str = Depends(verify_api_key)):
    """List available MCP servers"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{MCP_HUB_URL}/servers", timeout=5)
            return resp.json()
    except:
        return {
            "servers": [
                {"id": "context7", "name": "Context7 Docs", "status": "available"},
                {"id": "git", "name": "Git Operations", "status": "available"},
                {"id": "supabase", "name": "Supabase DB", "status": "available"}
            ]
        }

@app.post("/v1/chat/completions")
async def chat_completions(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Proxy to LiteLLM for chat completions"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{LITELLM_URL}/v1/chat/completions",
                json=request,
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=60
            )
            
            return resp.json()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/models")
async def list_models(api_key: str = Depends(verify_api_key)):
    """List available models via LiteLLM"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{LITELLM_URL}/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            
            return resp.json()
            
    except Exception as e:
        # Fallback model list
        return {
            "data": [
                {"id": "gpt-4o", "name": "GPT-4o"},
                {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
                {"id": "claude-3-5-sonnet", "name": "Claude 3.5 Sonnet"},
                {"id": "gemini-pro", "name": "Gemini Pro"}
            ]
        }

@app.get("/v1/stats")
async def get_stats(api_key: str = Depends(verify_api_key)):
    """Get usage statistics"""
    if redis_client:
        # Get stats from Redis
        total_requests = redis_client.get("stats:total_requests") or 0
        total_tokens = redis_client.get("stats:total_tokens") or 0
        
        return {
            "total_requests": int(total_requests),
            "total_tokens": int(total_tokens),
            "active_agents": 3,
            "active_mcp_servers": 5
        }
    
    return {
        "total_requests": 0,
        "total_tokens": 0,
        "active_agents": 3,
        "active_mcp_servers": 5
    }

# =============================================================================
# Error Handlers
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "success": False,
        "error": exc.detail,
        "status_code": exc.status_code
    }

# =============================================================================
# Startup
# =============================================================================

@app.on_event("startup")
async def startup():
    print("AI Agent Starter Kit Gateway starting...")
    print(f"LiteLLM Proxy: {LITELLM_URL}")
    print(f"MCP Hub: {MCP_HUB_URL}")
    print("Ready to serve requests!")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("GATEWAY_PORT", "3000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
