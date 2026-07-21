"""Safe hwpx-skill adapter behavior."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import core.adapters.hwpx_skill_adapter as adapter_module
from core.adapters.hwpx_skill_adapter import (
    HwpToHwpxAdapterError,
    convert_hwp_to_hwpx,
)
from core.hwp_converter import HwpSkillConverter


def test_adapter_uses_local_hwp2hwpx_without_install_or_clone() -> None:
    sys.modules.pop("hwp2hwpx", None)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        skill_dir = root / "hwpx-skill-main"
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(parents=True)
        (scripts_dir / "convert_hwp.py").write_text("# reference script\n", encoding="utf-8")

        engine_root = root / "hwp2hwpx-python-refactor"
        package = engine_root / "hwp2hwpx"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text(
            "from pathlib import Path\n"
            "def convert_file(input_path, output_path=None):\n"
            "    out = Path(output_path or Path(input_path).with_suffix('.hwpx'))\n"
            "    out.write_text('fake hwpx', encoding='utf-8')\n"
            "    return str(out)\n",
            encoding="utf-8",
        )

        source = root / "sample.hwp"
        output = root / "sample.hwpx"
        source.write_bytes(b"fake hwp")

        result = convert_hwp_to_hwpx(
            source,
            output,
            skill_dir=skill_dir,
            hwp2hwpx_paths=[engine_root],
            include_installed=False,
            run_skill_postprocessors=False,
        )

        assert result.output_path == output
        assert output.read_text(encoding="utf-8") == "fake hwpx"
        assert result.engine.startswith("local:")
        assert result.to_meta()["hwp_to_hwpx_adapter"] == "hwpx_skill_adapter"
    sys.modules.pop("hwp2hwpx", None)


def test_adapter_returns_clear_error_when_engine_is_missing(monkeypatch) -> None:
    monkeypatch.delitem(sys.modules, "hwp2hwpx", raising=False)
    monkeypatch.setattr(adapter_module, "_candidate_engine_paths", lambda *_: ())
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        skill_dir = root / "hwpx-skill-main"
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(parents=True)
        (scripts_dir / "convert_hwp.py").write_text("# reference script\n", encoding="utf-8")
        source = root / "sample.hwp"
        source.write_bytes(b"fake hwp")

        try:
            convert_hwp_to_hwpx(
                source,
                root / "sample.hwpx",
                skill_dir=skill_dir,
                include_installed=False,
                run_skill_postprocessors=False,
            )
        except HwpToHwpxAdapterError as exc:
            message = str(exc)
            assert "will not auto-install" in message
            assert "clone" in message
        else:
            raise AssertionError("missing hwp2hwpx engine should fail clearly")


def test_adapter_accepts_engine_without_return_value() -> None:
    sys.modules.pop("hwp2hwpx", None)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        skill_dir = root / "hwpx-skill-main"
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(parents=True)
        (scripts_dir / "convert_hwp.py").write_text("# reference script\n", encoding="utf-8")

        engine_root = root / "hwp2hwpx-python-refactor"
        package = engine_root / "hwp2hwpx"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text(
            "from pathlib import Path\n"
            "def convert_file(input_path, output_path=None):\n"
            "    Path(output_path).write_text('fake hwpx', encoding='utf-8')\n",
            encoding="utf-8",
        )

        source = root / "sample.hwp"
        output = root / "sample.hwpx"
        source.write_bytes(b"fake hwp")

        result = convert_hwp_to_hwpx(
            source,
            output,
            skill_dir=skill_dir,
            hwp2hwpx_paths=[engine_root],
            include_installed=False,
            run_skill_postprocessors=False,
        )

        assert result.output_path == output
        assert output.read_text(encoding="utf-8") == "fake hwpx"
    sys.modules.pop("hwp2hwpx", None)


def test_hwp_converter_keeps_pyhwp_fallback_when_adapter_unavailable() -> None:
    converter = HwpSkillConverter()

    def fail_adapter(path: Path):  # noqa: ANN001
        raise HwpToHwpxAdapterError("adapter unavailable")

    converter._convert_hwp_via_hwpx_adapter = fail_adapter  # type: ignore[method-assign]
    converter._convert_hwp_legacy = lambda path: "# legacy\n\nbody\n"  # type: ignore[method-assign]

    result = converter.convert(Path("sample.hwp"))

    assert result.ok
    assert result.markdown == "# legacy\n\nbody\n"
    assert result.document_model is None
    assert result.meta["input_conversion_strategy"] == "pyhwp_html_markdown_fallback"
    assert result.meta["hwp_to_hwpx_available"] is False
    assert "adapter unavailable" in result.meta["hwp_to_hwpx_error"]


def test_hwp_converter_prefers_hwp_to_hwpx_adapter_path() -> None:
    converter = HwpSkillConverter()

    def fake_adapter(path: Path):  # noqa: ANN001
        return (
            "# from hwpx\n\nbody\n",
            {
                "input_conversion_strategy": "hwp_to_hwpx_then_markdown",
                "intermediate_format": "hwpx",
            },
            None,
        )

    converter._convert_hwp_via_hwpx_adapter = fake_adapter  # type: ignore[method-assign]
    converter._convert_hwp_legacy = lambda path: "should not be used"  # type: ignore[method-assign]

    result = converter.convert(Path("sample.hwp"))

    assert result.ok
    assert result.markdown.startswith("# from hwpx")
    assert result.meta["input_conversion_strategy"] == "hwp_to_hwpx_then_markdown"
    assert result.meta["intermediate_format"] == "hwpx"


if __name__ == "__main__":
    test_adapter_uses_local_hwp2hwpx_without_install_or_clone()
    test_adapter_accepts_engine_without_return_value()
    test_hwp_converter_keeps_pyhwp_fallback_when_adapter_unavailable()
    test_hwp_converter_prefers_hwp_to_hwpx_adapter_path()
    print("PASS: hwpx skill adapter")
