"""Pass-through converter for Markdown drafts."""
from __future__ import annotations

from pathlib import Path

from .converter_base import BaseConverter, ConvertResult


class MarkdownConverter(BaseConverter):
    """Treat an existing Markdown file as the normalized hub format."""

    supported_ext = (".md", ".markdown")

    def convert(self, path: Path) -> ConvertResult:
        try:
            markdown = Path(path).read_text(encoding="utf-8")
            return ConvertResult(
                source=path,
                markdown=markdown,
                ok=True,
                meta={"converter": self.name, "normalized": True},
            )
        except UnicodeDecodeError as e:
            return ConvertResult(
                source=path,
                markdown="",
                ok=False,
                error=f"Markdown file must be UTF-8 encoded: {e}",
                meta={"converter": self.name},
            )
        except Exception as e:  # noqa: BLE001
            return ConvertResult(
                source=path,
                markdown="",
                ok=False,
                error=repr(e),
                meta={"converter": self.name},
            )
