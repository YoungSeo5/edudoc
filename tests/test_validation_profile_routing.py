from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

import core.pipeline as pipeline_module
import main as main_cli
from core.adapters.hwpx_template_renderer import fill_template_sections
from core.converter_base import BaseConverter, ConvertResult
from core.generators.gongmun_generator import generate_and_validate
from core.pipeline import Pipeline, PipelineConfig
from core.registry import ConverterRegistry
from validators.gongmun_rules import validate as validate_gongmun


class GeneralDocumentConverter(BaseConverter):
    supported_ext = (".hwp", ".hwpx", ".md")

    def convert(self, path: Path) -> ConvertResult:
        return ConvertResult(
            source=path,
            markdown="# 일반 보고서\n\n공문이 아닌 일반 문서입니다.\n",
            ok=True,
            meta={"converter": self.name},
        )


def _pipeline(tmp_path: Path) -> Pipeline:
    registry = ConverterRegistry()
    registry.register(GeneralDocumentConverter())
    return Pipeline(
        registry=registry,
        config=PipelineConfig(
            output_dir=tmp_path / "out",
            write_validation_report=True,
        ),
    )


@pytest.mark.parametrize("suffix", (".hwp", ".hwpx", ".md"))
def test_public_pipeline_has_no_gongmun_validation_for_supported_inputs(
    tmp_path: Path,
    suffix: str,
) -> None:
    source = tmp_path / f"general{suffix}"
    source.write_text("source", encoding="utf-8")

    result = _pipeline(tmp_path).process_file(source)

    assert result.ok
    assert not hasattr(pipeline_module, "validate_gongmun")
    for key in (
        "validation",
        "validation_passed",
        "validation_summary",
        "validation_report",
    ):
        assert key not in result.meta
    assert not (tmp_path / "out" / "general.validation.txt").exists()
    assert (tmp_path / "out" / "general.md").is_file()


@pytest.mark.parametrize(
    "legacy_config",
    (
        {"validation_profile": "gongmun"},
        {"validate_gongmun": True},
        {"target_document_profile": "standard_gongmun"},
    ),
)
def test_pipeline_config_rejects_removed_gongmun_routing(legacy_config) -> None:
    with pytest.raises(TypeError):
        PipelineConfig(**legacy_config)


def test_fss_template_path_never_uses_gongmun_as_fallback_validator() -> None:
    root = Path(__file__).resolve().parent.parent
    template_dir = root / "templates" / "institutions" / "금융감독원" / "금감원 원페이지"

    with patch("validators.gongmun_rules.validate") as validator:
        sections, result = fill_template_sections(
            template_dir,
            {"document_title_01": "금감원 일반 보고"},
        )

    validator.assert_not_called()
    assert "Contents/section0.xml" in sections
    assert "document_title_01" in result.filled_fields


def test_gongmun_brief_generator_still_runs_gongmun_validation(tmp_path: Path) -> None:
    brief = tmp_path / "brief.md"
    brief.write_text("내용: 연수 참가 신청\n", encoding="utf-8")

    with patch(
        "core.generators.gongmun_generator.validate",
        wraps=validate_gongmun,
    ) as validator:
        result = generate_and_validate(brief)

    validator.assert_called_once()
    assert result.validation_report is not None


def test_main_constructs_pipeline_without_gongmun_routing() -> None:
    captured_configs: list[PipelineConfig] = []

    class ProbePipeline:
        def __init__(self, *, config: PipelineConfig) -> None:
            captured_configs.append(config)

        def process_file(self, path: Path) -> ConvertResult:
            return ConvertResult(source=path, markdown="", ok=True)

    with patch.object(main_cli, "Pipeline", ProbePipeline):
        assert main_cli.main(["main.py", "run", "general.md"]) == 0

    assert len(captured_configs) == 1
    config = captured_configs[0]
    assert not hasattr(config, "validation_profile")
    assert not hasattr(config, "validate_gongmun")
    assert not hasattr(config, "target_document_profile")


def test_main_help_does_not_advertise_gongmun_validation(capsys) -> None:
    assert main_cli.main(["main.py", "--help"]) == 0

    output = capsys.readouterr().out
    assert "--validation-profile" not in output
    assert "gongmun" not in output.lower()


@pytest.mark.parametrize(
    ("command", "arguments"),
    (
        ("run", ("--validation-profile", "gongmun")),
        ("run", ("--validation-profile=standard_gongmun",)),
        ("watch", ("--validation-profile", "gongmun")),
        ("watch", ("--validation-profile=standard_gongmun",)),
    ),
)
def test_main_rejects_removed_validation_profile_option(command, arguments, capsys) -> None:
    with patch.object(main_cli, "Pipeline") as pipeline:
        assert main_cli.main(["main.py", command, "general.md", *arguments]) == 2

    pipeline.assert_not_called()
    assert "지원하지 않는 옵션" in capsys.readouterr().err
