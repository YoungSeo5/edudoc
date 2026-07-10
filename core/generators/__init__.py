"""Generation helpers for Markdown-first workflows."""

from .public_plan_generator import (
    PublicPlanGenerationResult,
    generate_public_plan_from_source_profile,
    generate_public_plan_markdown,
    write_public_plan_markdown,
)
from .one_page_report_generator import build_draft as build_one_page_report_draft
from .one_page_report_generator import build_skeleton as build_one_page_report_skeleton

__all__ = [
    "PublicPlanGenerationResult",
    "build_one_page_report_draft",
    "build_one_page_report_skeleton",
    "generate_public_plan_from_source_profile",
    "generate_public_plan_markdown",
    "write_public_plan_markdown",
]
