"""
AgentForge Deployer Python SDK
Client library for the Deployer REST API.

Usage:
    from sdk import AgentForge
    af = AgentForge("http://localhost:8000")
    repos = af.list_repos(category="trading", deployable_only=True)
    deploy = af.deploy("my-repo", env_vars={"KEY": "value"})
"""
import json
from typing import Optional, Dict, List, Any
from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote


class AgentForgeError(Exception):
    pass


class AgentForge:
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, path: str, data: dict = None) -> Any:
        url = self.base_url + path
        headers = {"Accept": "application/json"}
        body = None
        if data is not None:
            body = json.dumps(data).encode()
            headers["Content-Type"] = "application/json"
        req = Request(url, data=body, headers=headers, method=method)
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            raise AgentForgeError(str(e))

    def list_repos(
        self,
        search: str = None,
        category: str = None,
        language: str = None,
        deployable_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        params = {"limit": limit, "offset": offset}
        if search:
            params["search"] = search
        if category:
            params["category"] = category
        if language:
            params["language"] = language
        if deployable_only:
            params["deployable_only"] = "true"
        qs = urlencode(params)
        return self._request("GET", "/api/repos?" + qs)

    def get_repo(self, name: str) -> dict:
        return self._request("GET", "/api/repos/" + quote(name, safe=""))

    def get_categories(self) -> dict:
        return self._request("GET", "/api/categories")

    def get_stats(self) -> dict:
        return self._request("GET", "/api/stats")

    def deploy(self, repo_name: str, env_vars: dict = None, port_mapping: dict = None) -> dict:
        return self._request("POST", "/api/deploy/" + quote(repo_name, safe=""), {
            "repo_name": repo_name,
            "env_vars": env_vars or {},
            "port_mapping": port_mapping or {},
        })

    def list_deployments(self) -> List[dict]:
        return self._request("GET", "/api/deployments")

    def rescan(self) -> dict:
        return self._request("POST", "/api/scan")

    def search(self, query: str, limit: int = 50) -> List[dict]:
        result = self.list_repos(search=query, limit=limit)
        return result.get("repos", [])

    def deployable(self, category: str = None) -> List[dict]:
        result = self.list_repos(deployable_only=True, category=category, limit=500)
        return result.get("repos", [])
