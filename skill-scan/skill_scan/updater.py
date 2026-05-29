from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    requests = None  # type: ignore


class RuleUpdater:
    REMOTE_URL = "https://raw.githubusercontent.com/velvet-sojourner/skill-scan/main/skill_scan/rules/rules.json"

    def __init__(self, rules_dir: Optional[Path] = None) -> None:
        self.rules_dir = rules_dir or Path(__file__).parent / "rules"
        self._manifest_path = self.rules_dir / "rules.json"

    def get_rule_versions(self) -> dict[str, str]:
        local: dict[str, str] = {}
        if not self._manifest_path.exists():
            return local
        try:
            data = json.loads(self._manifest_path.read_text(encoding="utf-8"))
            for rule_name, meta in data.get("rules", {}).items():
                local[rule_name] = meta.get("version", "0.0.0")
        except (json.JSONDecodeError, OSError):
            return local
        return local

    def _fetch_json(self, url: str) -> Optional[dict]:
        if requests is None:
            return None
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, json.JSONDecodeError):
            return None

    def check_for_updates(self) -> bool:
        remote = self._fetch_json(self.REMOTE_URL)
        if remote is None:
            return False
        local_versions = self.get_rule_versions()
        remote_rules = remote.get("rules", {})
        for rule_name, meta in remote_rules.items():
            remote_ver = meta.get("version", "0.0.0")
            local_ver = local_versions.get(rule_name, "0.0.0")
            if remote_ver != local_ver:
                if rule_name not in local_versions:
                    return True
                r_parts = [int(x) for x in remote_ver.split(".")]
                l_parts = [int(x) for x in local_ver.split(".")]
                if r_parts > l_parts:
                    return True
        return False

    def list_available_rules(self) -> list[dict]:
        remote = self._fetch_json(self.REMOTE_URL)
        if remote is None:
            return []
        return list(remote.get("rules", {}).values())

    def update_rules(self, rules_dir: Optional[Path] = None) -> int:
        dest = rules_dir or self.rules_dir
        remote = self._fetch_json(self.REMOTE_URL)
        if remote is None:
            return 0
        local_versions = self.get_rule_versions()
        updated = 0
        remote_rules = remote.get("rules", {})

        for rule_name, meta in remote_rules.items():
            remote_ver = meta.get("version", "0.0.0")
            local_ver = local_versions.get(rule_name, "0.0.0")

            if not self._is_newer(remote_ver, local_ver):
                continue

            file_url = meta.get("download_url", "")
            if not file_url:
                continue

            if requests is None:
                continue
            try:
                resp = requests.get(file_url, timeout=15)
                resp.raise_for_status()
                dest_path = dest / meta.get("file", f"{rule_name}.py")
                dest_path.write_text(resp.text, encoding="utf-8")
                updated += 1
            except (requests.RequestException, OSError):
                continue

        if updated > 0 and remote.get("rules"):
            self._manifest_path.write_text(
                json.dumps(remote, indent=2), encoding="utf-8"
            )

        return updated

    @staticmethod
    def _is_newer(remote_ver: str, local_ver: str) -> bool:
        try:
            r = [int(x) for x in remote_ver.split(".")]
            l = [int(x) for x in local_ver.split(".")]
            return r > l
        except (ValueError, IndexError):
            return False
