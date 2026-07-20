"""Agent-authored document composition (glue between agent writing and rendering).

The agent fills a `ComposedReport` (structured content); this module renders it to
clean Markdown and validates it. Layout is owned here (sections -> headings, body ->
□/○/― paragraphs, tables only for real tabular data), so the agent supplies content
only. No LLM API is called here — the writing is done by the agent in-session.
"""
from .report import (
    AttachmentPolicy,
    Block,
    ComposedReport,
    GONGMUN_ATTACHMENT_POLICY,
    NEUTRAL_ATTACHMENT_POLICY,
    Section,
    Table,
    attachment_policy_for_family,
    validate_report,
)

__all__ = [
    "AttachmentPolicy",
    "Block",
    "ComposedReport",
    "GONGMUN_ATTACHMENT_POLICY",
    "NEUTRAL_ATTACHMENT_POLICY",
    "Section",
    "Table",
    "attachment_policy_for_family",
    "validate_report",
]
