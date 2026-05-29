import pytest
import sys
import os


def test_web_app_imports():
    from src.web.app import app, serve
    assert app.title == "ChatGPT Export Dashboard"


def test_web_routes_registered():
    from src.web.app import app
    paths = [r.path for r in app.routes]
    assert "/api/stats" in paths
    assert "/api/trends" in paths
    assert "/api/costs" in paths
    assert "/api/topics" in paths
    assert "/api/costs/monthly" in paths
    assert "/api/search" in paths
    assert "/api/conversations" in paths
    assert "/api/export/csv" in paths
    assert "/api/export/report" in paths
    assert "/api/export/data" in paths
    assert "/" in paths


def test_dashboard_template_exists():
    from src.web.app import app_dir
    template_path = app_dir / "templates" / "dashboard.html"
    assert template_path.exists()


def test_static_files_exist():
    from src.web.app import app_dir
    assert (app_dir / "static" / "style.css").exists()
    assert (app_dir / "static" / "chart.js").exists()


def test_client_routes():
    try:
        from fastapi.testclient import TestClient
    except ImportError:
        pytest.skip("httpx not installed for TestClient")
    from src.web.app import app
    from src.api.routes import init
    init([])
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    resp = client.get("/api/trends")
    assert resp.status_code == 200
    resp = client.get("/api/costs")
    assert resp.status_code == 200
    resp = client.get("/api/topics")
    assert resp.status_code == 200
    resp = client.get("/api/conversations")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "total_pages" in data
