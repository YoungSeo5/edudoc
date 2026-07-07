"""Source bundle intake model and builder.

A SourceBundle is a filtered manifest of source/reference documents. It does not
convert files, generate documents, export final formats, or write outputs.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

from .input_filter import input_filter_reason
from .registry import ConverterRegistry, default_registry


@dataclass(frozen=True)
class SourceDocument:
    path: str
    name: str
    suffix: str
    relative_path: str
    processable: bool
    reason: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class IgnoredSourceFile:
    path: str
    name: str
    suffix: str
    relative_path: str
    reason: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class SourceBundle:
    root_paths: list[str]
    documents: list[SourceDocument] = field(default_factory=list)
    ignored_files: list[IgnoredSourceFile] = field(default_factory=list)
    unsupported_files: list[SourceDocument] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "root_paths": self.root_paths,
            "documents": [document.to_dict() for document in self.documents],
            "ignored_files": [ignored.to_dict() for ignored in self.ignored_files],
            "unsupported_files": [
                unsupported.to_dict() for unsupported in self.unsupported_files
            ],
            "summary": dict(self.summary),
        }


def build_source_bundle(
    paths: Iterable[Path | str],
    registry: ConverterRegistry | None = None,
) -> SourceBundle:
    """Build a filtered source-document manifest from files and directories.

    Directory traversal follows the current pipeline behavior: recursive scan
    with repository/control files and generated artifacts filtered out.
    """
    reg = registry or default_registry()
    roots = [Path(path) for path in paths]
    root_paths = [str(root) for root in roots]

    documents: list[SourceDocument] = []
    ignored_files: list[IgnoredSourceFile] = []
    unsupported_files: list[SourceDocument] = []

    for root in roots:
        for candidate, relative_path in _iter_candidates(root):
            if not candidate.exists():
                ignored_files.append(_ignored(candidate, relative_path, "missing_path"))
                continue
            if not candidate.is_file():
                continue

            reason = input_filter_reason(candidate)
            if reason is not None:
                ignored_files.append(_ignored(candidate, relative_path, reason))
                continue

            processable = reg.find(candidate) is not None
            document = _document(
                candidate,
                relative_path,
                processable=processable,
                reason="supported_input" if processable else "unsupported_input_type",
            )
            if processable:
                documents.append(document)
            else:
                unsupported_files.append(document)

    summary = {
        "root_count": len(roots),
        "document_count": len(documents),
        "ignored_count": len(ignored_files),
        "unsupported_count": len(unsupported_files),
        "total_file_count": len(documents) + len(ignored_files) + len(unsupported_files),
    }
    return SourceBundle(
        root_paths=root_paths,
        documents=documents,
        ignored_files=ignored_files,
        unsupported_files=unsupported_files,
        summary=summary,
    )


def _iter_candidates(root: Path) -> list[tuple[Path, str]]:
    if root.is_dir():
        return [
            (path, _relative_to(path, root))
            for path in sorted(root.rglob("*"))
            if path.is_file()
        ]
    return [(root, root.name)]


def _relative_to(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def _document(
    path: Path,
    relative_path: str,
    *,
    processable: bool,
    reason: str,
) -> SourceDocument:
    return SourceDocument(
        path=str(path),
        name=path.name,
        suffix=path.suffix.lower(),
        relative_path=relative_path,
        processable=processable,
        reason=reason,
    )


def _ignored(path: Path, relative_path: str, reason: str) -> IgnoredSourceFile:
    return IgnoredSourceFile(
        path=str(path),
        name=path.name,
        suffix=path.suffix.lower(),
        relative_path=relative_path,
        reason=reason,
    )
