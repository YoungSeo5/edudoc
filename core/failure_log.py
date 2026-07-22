"""Unified failure-record writer shared by the CLI entry points.

Each failure is written as one JSON file under a failures directory (default
``exports/failures/``). This is diagnostic/operational data only: per root
``AGENTS.md``, files under ``exports/`` must never be cited as implementation
evidence for architecture or bug claims — use canonical source + a real
run/test for that instead.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_FAILURES_DIR = Path("exports") / "failures"
DEFAULT_RETENTION_LIMIT = 500

_SLUG_RE = re.compile(r"[^A-Za-z0-9_-]+")
_SLUG_MAX_LEN = 60


@dataclass(frozen=True)
class FailureRecord:
    """One failure event. ``timestamp`` is assigned by ``record_failure``."""

    entry_point: str   # "pipeline" | "gongmun_cli" | "public_plan_cli" | "compose_cli"
    stage: str          # "convert" | "export" | "gongmun_generate" | "gongmun_validate" | "render"
    source: str          # failed input/output path or identifier
    error: str
    meta: dict = field(default_factory=dict)

    def to_dict(self, timestamp: str) -> dict:
        return {
            "timestamp": timestamp,
            "entry_point": self.entry_point,
            "stage": self.stage,
            "source": self.source,
            "error": self.error,
            "meta": dict(self.meta),
        }


def record_failure(
    failures_dir: Path,
    record: FailureRecord,
    *,
    retention_limit: int = DEFAULT_RETENTION_LIMIT,
) -> Path:
    """Write one failure as one JSON file, then prune beyond ``retention_limit``.

    Filenames are ``<timestamp>-<stage>-<slug(source)>.json``; the timestamp
    prefix uses UTC microseconds, so lexicographic order equals chronological
    order and concurrent failures never collide on the same filename.
    """
    failures_dir = Path(failures_dir)
    failures_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    filename = f"{now.strftime('%Y%m%dT%H%M%S%f')}-{record.stage}-{_slug(record.source)}.json"
    out_path = failures_dir / filename
    out_path.write_text(
        json.dumps(record.to_dict(now.isoformat()), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    _prune(failures_dir, retention_limit)
    return out_path


def _prune(failures_dir: Path, retention_limit: int) -> None:
    """Keep only the newest ``retention_limit`` records; delete older ones."""
    if retention_limit <= 0:
        return
    files = sorted(p for p in failures_dir.glob("*.json") if p.is_file())
    excess = len(files) - retention_limit
    if excess <= 0:
        return
    for path in files[:excess]:
        path.unlink(missing_ok=True)


def _slug(value: str) -> str:
    cleaned = _SLUG_RE.sub("_", value).strip("_")
    return cleaned[:_SLUG_MAX_LEN] or "unknown"


__all__ = [
    "DEFAULT_FAILURES_DIR",
    "DEFAULT_RETENTION_LIMIT",
    "FailureRecord",
    "record_failure",
]
