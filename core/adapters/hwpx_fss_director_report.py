from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime

from .hwpx_alias_map import JsonValue, flatten

FSS_TEMPLATE_ID = "fss_director_report"
FSS_META_NAMES = (
    "creator",
    "subject",
    "description",
    "lastsaveby",
    "date",
    "keyword",
    "CreatedDate",
    "ModifiedDate",
)


class FssDirectorReportInputError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class FssPackageMetadata:
    title: str
    creator: str
    subject: str
    description: str
    lastsaveby: str
    report_date: str
    keywords: str
    requested_at: datetime


def _input_string(
    flattened: Mapping[str, JsonValue],
    paths: tuple[str, ...],
    *,
    required: bool,
) -> str:
    path = next(
        (candidate for candidate in paths if candidate in flattened),
        paths[0],
    )
    value = flattened.get(path)
    if value is None and not required:
        return ""
    if not isinstance(value, str) or (required and not value.strip()):
        requirement = "a non-empty string" if required else "a string"
        raise FssDirectorReportInputError(
            f"fss metadata input {path!r} must be {requirement}"
        )
    return value


def build_fss_package_metadata(
    source_content: Mapping[str, JsonValue],
    *,
    requester_name: str,
    requested_at: datetime,
) -> FssPackageMetadata:
    flattened = flatten(source_content)
    body = source_content.get("본문", source_content.get("content_01"))
    if "본문" in source_content and not isinstance(body, list):
        raise FssDirectorReportInputError(
            "fss metadata input '본문' must be an array"
        )

    level_zero_titles: list[str] = []
    if isinstance(body, list):
        for index, item in enumerate(body):
            if not isinstance(item, list) or len(item) != 2:
                raise FssDirectorReportInputError(
                    f"fss metadata input '본문[{index}]' must be [level, text]"
                )
            if item[0] != 0:
                continue
            text = item[1]
            if not isinstance(text, str):
                raise FssDirectorReportInputError(
                    f"fss metadata input '본문[{index}]' text must be a string"
                )
            level_zero_titles.append(text)

    report_type = _input_string(
        flattened,
        ("보고구분",),
        required=False,
    )
    department = _input_string(
        flattened,
        ("담당.국", "department_name_01"),
        required=False,
    )
    department_label = f"{department}국" if department else ""
    keywords = ", ".join(
        value
        for value in (report_type, department_label, *level_zero_titles)
        if value
    )
    return FssPackageMetadata(
        title=_input_string(
            flattened,
            ("제목", "document_title_01"),
            required=True,
        ),
        creator=requester_name,
        subject=", ".join(level_zero_titles),
        description=_input_string(
            flattened,
            ("결론", "conclusion_01"),
            required=False,
        ),
        lastsaveby=requester_name,
        report_date=_input_string(
            flattened,
            ("보고일", "date_01"),
            required=True,
        ),
        keywords=keywords,
        requested_at=requested_at,
    )
