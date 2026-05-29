from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import webbrowser

from src.api.routes import router as api_router

app_dir = Path(__file__).parent

app = FastAPI(title="ChatGPT Export Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory=str(app_dir / "templates"))
app.mount("/static", StaticFiles(directory=str(app_dir / "static")), name="static")
app.include_router(api_router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


def serve(host="0.0.0.0", port=8766):
    import uvicorn
    webbrowser.open(f"http://localhost:{port}")
    print(f"Dashboard: http://localhost:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")
