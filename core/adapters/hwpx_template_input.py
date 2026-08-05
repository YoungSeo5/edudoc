from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from .hwpx_alias_map import AliasMap, JsonValue, load_alias_map
from .hwpx_fss_director_report import (
    FSS_TEMPLATE_ID,
    FssDirectorReportInputError,
    FssPackageMetadata,
    build_fss_package_metadata,
)


class HwpxTemplateRenderError(RuntimeError):
    """Raised when a template cannot be rendered."""


class HwpxTemplateInputError(HwpxTemplateRenderError):
    pass


@dataclass(frozen=True, slots=True)
class RenderExecutionContext:
    requester_name: str
    requested_at: datetime

    def __post_init__(self) -> None:
        if not self.requester_name.strip():
            raise HwpxTemplateRenderError(
                "execution context requires requester_name"
            )
        if self.requested_at.utcoffset() != timedelta(0):
            raise HwpxTemplateRenderError(
                "execution context requested_at must be a UTC datetime"
            )


@dataclass(frozen=True, slots=True)
class ResolvedRenderContent:
    template_id: str | None
    placeholder_map: Mapping[str, JsonValue]
    alias_map: AliasMap | None
    field_values: dict[str, JsonValue]
    repeat_values: dict[str, list[JsonValue]]
    unknown_keys: tuple[str, ...]
    title_field_id: str | None


@dataclass(frozen=True, slots=True)
class PreparedRenderContent(ResolvedRenderContent):
    package_metadata: FssPackageMetadata | None


def load_placeholder_map(template_dir: Path | str) -> Mapping[str, JsonValue]:
    path = Path(template_dir) / "placeholder_map.json"
    if not path.is_file():
        raise HwpxTemplateInputError(
            f"placeholder_map.json not found in {template_dir}"
        )
    raw: JsonValue = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise HwpxTemplateInputError(
            f"placeholder_map.json root must be an object: {path}"
        )
    return raw


def resolve_hwpx_template_input(
    template_dir: Path | str,
    content: Mapping[str, JsonValue],
) -> ResolvedRenderContent:
    """Resolve human input into field IDs and separately held repeat values."""
    placeholder_map = load_placeholder_map(template_dir)
    template_id_raw = placeholder_map.get("template_id")
    template_id = template_id_raw if isinstance(template_id_raw, str) else None
    fields_raw = placeholder_map.get("fields", [])
    field_ids = frozenset(
        entry["field_id"]
        for entry in fields_raw
        if isinstance(entry, dict) and isinstance(entry.get("field_id"), str)
    )
    alias_map = load_alias_map(
        template_dir,
        field_ids=field_ids,
        template_id=template_id,
    )
    if alias_map is None:
        return ResolvedRenderContent(
            template_id=template_id,
            placeholder_map=placeholder_map,
            alias_map=None,
            field_values=dict(content),
            repeat_values={},
            unknown_keys=(),
            title_field_id=None,
        )

    field_values, unknown_keys = alias_map.resolve(content, field_ids)
    repeat_values: dict[str, list[JsonValue]] = {}
    for block in alias_map.blocks.values():
        value = field_values.pop(block.anchor, None)
        if value is None:
            continue
        if isinstance(value, list):
            repeat_values[block.anchor] = value
        else:
            field_values[block.anchor] = value

    return ResolvedRenderContent(
        template_id=template_id,
        placeholder_map=placeholder_map,
        alias_map=alias_map,
        field_values=field_values,
        repeat_values=repeat_values,
        unknown_keys=tuple(unknown_keys),
        title_field_id=alias_map.title_field_id,
    )


def prepare_hwpx_template_input(
    template_dir: Path | str,
    content: Mapping[str, JsonValue],
    *,
    execution_context: RenderExecutionContext | None = None,
) -> PreparedRenderContent:
    """Finish input interpretation before visible HWPX rendering starts."""
    resolved = resolve_hwpx_template_input(template_dir, content)
    package_metadata: FssPackageMetadata | None = None
    if resolved.template_id == FSS_TEMPLATE_ID:
        if execution_context is None:
            raise HwpxTemplateInputError(
                "fss_director_report requires execution_context"
            )
        try:
            package_metadata = build_fss_package_metadata(
                content,
                requester_name=execution_context.requester_name,
                requested_at=execution_context.requested_at,
            )
        except FssDirectorReportInputError as exc:
            raise HwpxTemplateInputError(str(exc)) from exc

    return PreparedRenderContent(
        template_id=resolved.template_id,
        placeholder_map=resolved.placeholder_map,
        alias_map=resolved.alias_map,
        field_values=resolved.field_values,
        repeat_values=resolved.repeat_values,
        unknown_keys=resolved.unknown_keys,
        title_field_id=resolved.title_field_id,
        package_metadata=package_metadata,
    )
