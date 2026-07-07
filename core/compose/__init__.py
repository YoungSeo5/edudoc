"""Agent-authored document composition (glue between agent writing and rendering).

The agent fills a `ComposedReport` (structured content); this module renders it to
clean Markdown and validates it. Layout is owned here (sections -> headings, body ->
□/○/― paragraphs, tables only for real tabular data), so the agent supplies content
only. No LLM API is called here — the writing is done by the agent in-session.
"""
from .report import Block, ComposedReport, Section, Table, validate_report

__all__ = ["Block", "ComposedReport", "Section", "Table", "validate_report"]
