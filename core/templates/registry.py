"""Load explicitly approved institution templates."""
from __future__ import annotations

from pathlib import Path

from .models import TemplateCandidate
from .serialization import load_candidate


class TemplateRegistry:
    def __init__(self, root: Path | str = "templates/institutions") -> None:
        self.root = Path(root)

    def template_path(self, institution: str, document_type: str) -> Path:
        return self.root / _slug(institution) / _slug(document_type) / "template.json"

    def find(self, institution: str, document_type: str) -> TemplateCandidate | None:
        path = self.template_path(institution, document_type)
        if not path.is_file():
            return None
        candidate = load_candidate(path)
        return candidate if candidate.status == "approved" else None


def _slug(value: str) -> str:
    clean = value.strip().replace("\\", "_").replace("/", "_")
    if not clean or clean in {".", ".."}:
        raise ValueError("institution and document_type must be non-empty safe names")
    return clean
