"""Unified failure-record writer shared by the CLI entry points.

Each failure is written as one JSON file under a failures directory (default
``exports/failures/``). This is diagnostic/operational data only: per root
``AGENTS.md``, files under ``exports/`` must never be cited as implementation
evidence for architecture or bug claims — use canonical source + a real
run/test for that instead.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_FAILURES_DIR = Path("exports") / "failures"

_SLUG_RE = re.compile(r"[^A-Za-z0-9_-]+")
_SLUG_MAX_LEN = 60


@dataclass(frozen=True, slots=True)
class FailureRecord:
    """One failure event. ``timestamp`` is assigned by ``record_failure``."""

    entry_point: str   # "pipeline" | "gongmun_cli" | "public_plan_cli" | "compose_cli"
    stage: str          # "convert" | "export" | "gongmun_generate" | "gongmun_validate" | "render"
    error_code: str
    source: str          # failed input/output path or identifier
    error: str
    meta: dict = field(default_factory=dict)

    @property
    def fingerprint(self) -> str:
        return failure_fingerprint(self.entry_point, self.stage, self.error_code)

    def to_dict(self, timestamp: str) -> dict:
        return {
            "timestamp": timestamp,
            "entry_point": self.entry_point,
            "stage": self.stage,
            "error_code": self.error_code,
            "fingerprint": self.fingerprint,
            "source": self.source,
            "error": self.error,
            "meta": dict(self.meta),
        }


@dataclass(frozen=True, slots=True)
class FailureSummary:
    fingerprint: str
    occurrence_count: int
    first_seen: str
    last_seen: str
    error_code: str
    entry_point: str
    stage: str

    def to_dict(self) -> dict:
        return {
            "fingerprint": self.fingerprint,
            "occurrence_count": self.occurrence_count,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "error_code": self.error_code,
            "entry_point": self.entry_point,
            "stage": self.stage,
        }


def failure_fingerprint(entry_point: str, stage: str, error_code: str) -> str:
    """Return a stable identity hash that excludes per-run details."""
    identity = json.dumps(
        {
            "entry_point": entry_point,
            "stage": stage,
            "error_code": error_code,
        },
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def record_failure(
    failures_dir: Path,
    record: FailureRecord,
) -> Path | None:
    """Best-effort write of one event without changing the caller outcome.

    Filenames are ``<timestamp>-<stage>-<slug(source)>.json``; the timestamp
    prefix uses UTC microseconds, so lexicographic order equals chronological
    order and concurrent failures never collide on the same filename.
    """
    failures_dir = Path(failures_dir)
    try:
        failures_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc)
        filename = (
            f"{now.strftime('%Y%m%dT%H%M%S%f')}-"
            f"{record.stage}-{_slug(record.source)}.json"
        )
        out_path = failures_dir / filename
        out_path.write_text(
            json.dumps(record.to_dict(now.isoformat()), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except (OSError, TypeError, ValueError):
        return None
    return out_path


def summarize_failures(failures_dir: Path) -> list[FailureSummary]:
    """Group valid failure records by stable fingerprint."""
    summaries: dict[str, FailureSummary] = {}
    for path in sorted(Path(failures_dir).glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            entry_point = data["entry_point"]
            stage = data["stage"]
            error_code = data["error_code"]
            timestamp = data["timestamp"]
            stored_fingerprint = data["fingerprint"]
            if not all(
                isinstance(value, str)
                for value in (
                    entry_point,
                    stage,
                    error_code,
                    timestamp,
                    stored_fingerprint,
                )
            ):
                continue
            fingerprint = failure_fingerprint(entry_point, stage, error_code)
            if stored_fingerprint != fingerprint:
                continue
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            continue

        current = summaries.get(fingerprint)
        if current is None:
            summaries[fingerprint] = FailureSummary(
                fingerprint=fingerprint,
                occurrence_count=1,
                first_seen=timestamp,
                last_seen=timestamp,
                error_code=error_code,
                entry_point=entry_point,
                stage=stage,
            )
            continue
        summaries[fingerprint] = FailureSummary(
            fingerprint=fingerprint,
            occurrence_count=current.occurrence_count + 1,
            first_seen=min(current.first_seen, timestamp),
            last_seen=max(current.last_seen, timestamp),
            error_code=error_code,
            entry_point=entry_point,
            stage=stage,
        )
    return sorted(summaries.values(), key=lambda item: item.fingerprint)


def _slug(value: str) -> str:
    cleaned = _SLUG_RE.sub("_", value).strip("_")
    return cleaned[:_SLUG_MAX_LEN] or "unknown"


__all__ = [
    "DEFAULT_FAILURES_DIR",
    "FailureRecord",
    "FailureSummary",
    "failure_fingerprint",
    "record_failure",
    "summarize_failures",
]
