import sys, os
sys.path.insert(0, r"C:\temp\velvet-sojourner\deployment-platform\deployer")
os.chdir(r"C:\temp\velvet-sojourner\deployment-platform\deployer")

from main import app
import uvicorn

print("Starting AgentForge API server...")
print("Open http://localhost:8000 in your browser")
print("Press Ctrl+C to stop")

uvicorn.run(app, host="127.0.0.1", port=8000)
