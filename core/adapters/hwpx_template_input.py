from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from .hwpx_alias_map import (
    AliasMap,
    FitConstraint,
    JsonValue,
    MetadataContract,
    RepeatBlock,
    flatten,
    load_alias_map,
)
from .hwpx_fss_director_report import (
    FSS_TEMPLATE_ID,
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
class ResolvedMetadata:
    title: str
    subject: str
    description: str
    report_date: str
    keywords: str


@dataclass(frozen=True, slots=True)
class ResolvedRenderPlan:
    field_values: dict[str, JsonValue]
    repeat_values: dict[str, list[JsonValue]]
    repeat_blocks: dict[str, RepeatBlock]
    fit_constraints: dict[str, FitConstraint]
    title_field_id: str | None


@dataclass(frozen=True, slots=True)
class ResolvedTemplateContent:
    template_id: str | None
    placeholder_map: Mapping[str, JsonValue]
    render_plan: ResolvedRenderPlan
    unknown_keys: tuple[str, ...]
    metadata: ResolvedMetadata | None


@dataclass(frozen=True, slots=True)
class PreparedRenderContent:
    template_id: str | None
    placeholder_map: Mapping[str, JsonValue]
    render_plan: ResolvedRenderPlan
    unknown_keys: tuple[str, ...]
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


def _resolve_metadata(
    content: Mapping[str, JsonValue],
    alias_map: AliasMap,
    contract: MetadataContract,
    repeat_values: Mapping[str, list[JsonValue]],
) -> ResolvedMetadata:
    flattened = flatten(content)

    def read_field(alias: str, *, required: bool = False) -> str:
        value = flattened.get(alias)
        if value is None and alias not in alias_map.choices:
            value = content.get(alias_map.aliases[alias])
        if value is None and not required:
            return ""
        if not isinstance(value, str) or (required and not value.strip()):
            requirement = "a non-empty string" if required else "a string"
            raise HwpxTemplateInputError(
                f"metadata field {alias!r} must be {requirement}"
            )
        return value

    title_alias = next(
        alias
        for alias, field_id in alias_map.aliases.items()
        if field_id == alias_map.title_field_id
    )
    subject_block = alias_map.blocks[contract.subject_block]
    subject_values = [
        item[1]
        for item in repeat_values.get(subject_block.anchor, [])
        if item[0] == contract.subject_level and item[1]
    ]
    department = read_field(contract.keyword_department_field)
    keyword_values = [
        read_field(contract.keyword_report_type_field),
        department + contract.keyword_department_suffix if department else "",
        *subject_values,
    ]
    return ResolvedMetadata(
        title=read_field(title_alias, required=True),
        subject=contract.subject_separator.join(subject_values),
        description=read_field(contract.description_field),
        report_date=read_field(
            contract.report_date_field,
            required=True,
        ),
        keywords=contract.keyword_separator.join(
            value for value in keyword_values if value
        ),
    )


def resolve_hwpx_template_input(
    template_dir: Path | str,
    content: Mapping[str, JsonValue],
) -> ResolvedTemplateContent:
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
        return ResolvedTemplateContent(
            template_id=template_id,
            placeholder_map=placeholder_map,
            render_plan=ResolvedRenderPlan(
                field_values=dict(content),
                repeat_values={},
                repeat_blocks={},
                fit_constraints={},
                title_field_id=None,
            ),
            unknown_keys=(),
            metadata=None,
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

    metadata = (
        _resolve_metadata(
            content,
            alias_map,
            alias_map.metadata,
            repeat_values,
        )
        if alias_map.metadata is not None
        else None
    )
    return ResolvedTemplateContent(
        template_id=template_id,
        placeholder_map=placeholder_map,
        render_plan=ResolvedRenderPlan(
            field_values=field_values,
            repeat_values=repeat_values,
            repeat_blocks={
                block.anchor: block for block in alias_map.blocks.values()
            },
            fit_constraints=alias_map.fit_constraints,
            title_field_id=alias_map.title_field_id,
        ),
        unknown_keys=tuple(unknown_keys),
        metadata=metadata,
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
        if resolved.metadata is None:
            raise HwpxTemplateInputError(
                "fss_director_report requires resolved metadata"
            )
        package_metadata = build_fss_package_metadata(
            resolved.metadata,
            requester_name=execution_context.requester_name,
            requested_at=execution_context.requested_at,
        )

    return PreparedRenderContent(
        template_id=resolved.template_id,
        placeholder_map=resolved.placeholder_map,
        render_plan=resolved.render_plan,
        unknown_keys=resolved.unknown_keys,
        package_metadata=package_metadata,
    )
