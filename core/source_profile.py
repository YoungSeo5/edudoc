"""Lightweight source understanding profile.

SourceProfile is an intentionally small extraction layer. It collects reusable
facts from normalized Markdown or DocumentModel objects, but it does not generate
new documents and does not parse heavy reference formats such as PDF.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

from .document_model import DocumentModel, document_model_from_markdown


@dataclass(frozen=True)
class SourceDocumentSummary:
    path: str
    name: str
    format: str
    title: str | None
    paragraph_count: int
    table_count: int
    attachment_count: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class SourceProfile:
    documents: list[SourceDocumentSummary] = field(default_factory=list)
    source_titles: list[str] = field(default_factory=list)
    institutions: list[str] = field(default_factory=list)
    dates: list[str] = field(default_factory=list)
    document_numbers: list[str] = field(default_factory=list)
    tables: list[str] = field(default_factory=list)
    statistics: list[str] = field(default_factory=list)
    budgets: list[str] = field(default_factory=list)
    schedules: list[str] = field(default_factory=list)
    key_actions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    attachments: list[str] = field(default_factory=list)
    extraction_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "documents": [document.to_dict() for document in self.documents],
            "source_titles": list(self.source_titles),
            "institutions": list(self.institutions),
            "dates": list(self.dates),
            "document_numbers": list(self.document_numbers),
            "tables": list(self.tables),
            "statistics": list(self.statistics),
            "budgets": list(self.budgets),
            "schedules": list(self.schedules),
            "key_actions": list(self.key_actions),
            "risks": list(self.risks),
            "attachments": list(self.attachments),
            "extraction_notes": list(self.extraction_notes),
        }


def build_source_profile_from_markdown_documents(
    documents: Iterable[tuple[Path | str, str]],
) -> SourceProfile:
    models = [
        document_model_from_markdown(
            source_path=Path(path),
            file_format=Path(path).suffix.lower().lstrip(".") or "markdown",
            markdown=markdown,
        )
        for path, markdown in documents
    ]
    return build_source_profile_from_document_models(models)


def build_source_profile_from_document_models(
    document_models: Iterable[DocumentModel],
) -> SourceProfile:
    summaries: list[SourceDocumentSummary] = []
    titles: list[str] = []
    institutions: list[str] = []
    dates: list[str] = []
    document_numbers: list[str] = []
    tables: list[str] = []
    statistics: list[str] = []
    budgets: list[str] = []
    schedules: list[str] = []
    key_actions: list[str] = []
    risks: list[str] = []
    attachments: list[str] = []

    for model in document_models:
        summaries.append(_summary(model))
        if model.title:
            titles.append(model.title)

        paragraphs = [paragraph.text for paragraph in model.paragraphs if paragraph.text]
        attachments.extend(attachment.text for attachment in model.attachments)
        attachments.extend(
            paragraph
            for paragraph in paragraphs
            if "붙임" in paragraph or "遺숈엫" in paragraph
        )

        for table in model.tables:
            rows = len(table.rows)
            cols = max((len(row) for row in table.rows), default=0)
            tables.append(f"{Path(model.source_path).name}: table {table.index} ({rows}x{cols})")

        institutions.extend(_extract_institutions(paragraphs))
        dates.extend(_extract_dates(paragraphs))
        document_numbers.extend(_extract_document_numbers(paragraphs))
        statistics.extend(_extract_statistics(paragraphs))
        budgets.extend(_extract_budgets(paragraphs))
        schedules.extend(_extract_schedules(paragraphs))
        key_actions.extend(_extract_key_actions(paragraphs))
        risks.extend(_extract_risks(paragraphs))

    return SourceProfile(
        documents=summaries,
        source_titles=_unique(titles),
        institutions=_unique(institutions),
        dates=_unique(dates),
        document_numbers=_unique(document_numbers),
        tables=_unique(tables),
        statistics=_unique(statistics),
        budgets=_unique(budgets),
        schedules=_unique(schedules),
        key_actions=_unique(key_actions),
        risks=_unique(risks),
        attachments=_unique(attachments),
        extraction_notes=[
            "SourceProfile is heuristic and deterministic.",
            "PDF reference samples are not parsed by this layer.",
            "Unknown or unsupported facts must remain 확인 필요 in later plans.",
        ],
    )


def _summary(model: DocumentModel) -> SourceDocumentSummary:
    return SourceDocumentSummary(
        path=model.source_path,
        name=Path(model.source_path).name,
        format=model.format,
        title=model.title,
        paragraph_count=len(model.paragraphs),
        table_count=len(model.tables),
        attachment_count=len(model.attachments),
    )


def _extract_institutions(paragraphs: list[str]) -> list[str]:
    patterns = ("교육청", "행정안전부", "공공기관", "학교", "지원청", "센터", "부서")
    return [
        line
        for line in paragraphs
        if any(pattern in line for pattern in patterns) and len(line) <= 80
    ]


def _extract_dates(paragraphs: list[str]) -> list[str]:
    values: list[str] = []
    for line in paragraphs:
        values.extend(re.findall(r"\b\d{4}\.\s*\d{1,2}\.\s*\d{1,2}\.?", line))
        values.extend(re.findall(r"\b\d{4}-\d{1,2}-\d{1,2}\b", line))
    return values


def _extract_document_numbers(paragraphs: list[str]) -> list[str]:
    values: list[str] = []
    for line in paragraphs:
        values.extend(re.findall(r"[가-힣A-Za-z]+-\d{2,}", line))
    return values


def _extract_statistics(paragraphs: list[str]) -> list[str]:
    return [
        line
        for line in paragraphs
        if re.search(r"\d+(?:\.\d+)?\s*(?:%|명|건|개|회|부)", line)
    ][:20]


def _extract_budgets(paragraphs: list[str]) -> list[str]:
    return [line for line in paragraphs if re.search(r"\d[\d,]*\s*(?:원|천원|만원|억원)", line)]


def _extract_schedules(paragraphs: list[str]) -> list[str]:
    words = ("일정", "기간", "기한", "추진일정", "제출", "마감")
    return [
        line
        for line in paragraphs
        if any(word in line for word in words) or _extract_dates([line])
    ][:20]


def _extract_key_actions(paragraphs: list[str]) -> list[str]:
    words = ("추진", "운영", "실시", "개최", "지원", "작성", "제출", "검토", "계획")
    return [
        line
        for line in paragraphs
        if any(word in line for word in words) and len(line) <= 180
    ][:30]


def _extract_risks(paragraphs: list[str]) -> list[str]:
    words = ("문제", "위험", "한계", "미흡", "개선", "보완", "유의")
    return [
        line
        for line in paragraphs
        if any(word in line for word in words) and len(line) <= 180
    ][:20]


def _unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        clean = " ".join(str(value).split())
        if not clean or clean in seen:
            continue
        seen.add(clean)
        result.append(clean)
    return result
