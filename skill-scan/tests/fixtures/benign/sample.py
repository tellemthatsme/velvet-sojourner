"""A benign skill file — no dangerous patterns."""

import os
import json


def greet(name: str) -> str:
    return f"Hello, {name}!"


def load_config(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def safe_list_dir(path: str) -> list[str]:
    return [x for x in os.listdir(path) if not x.startswith(".")]
