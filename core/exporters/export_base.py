"""Common interface for Markdown output exporters."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExportResult:
    """Result object returned by output exporters."""

    source: Path
    output: Path
    ok: bool = True
    error: str | None = None
    meta: dict = field(default_factory=dict)


class BaseExporter(ABC):
    """Markdown file -> deliverable exporter interface."""

    supported_ext: tuple[str, ...] = ()

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def can_export(self, output_path: Path) -> bool:
        return output_path.suffix.lower() in self.supported_ext

    @abstractmethod
    def export(self, markdown_path: Path, output_path: Path) -> ExportResult:
        """Export a Markdown file to the requested output path."""
        raise NotImplementedError
