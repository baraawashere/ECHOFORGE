"""
Tiny JSON-backed persistence for discovered root-cause clusters.

Without this, the discovered connections between mistakes lived only in
a Python dict in memory — every uvicorn restart silently wiped every
connection ECHOFORGE had ever found, even though the underlying
mistakes stayed safe in ChromaDB.
"""
import json
from pathlib import Path

from app.config import settings

_FILE = Path(settings.clusters_file)


def load_clusters() -> dict[str, list[dict]]:
    if not _FILE.exists():
        return {}
    try:
        return json.loads(_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_clusters(clusters: dict[str, list[dict]]) -> None:
    _FILE.write_text(json.dumps(clusters, indent=2))