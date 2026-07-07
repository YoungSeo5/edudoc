"""SourceBundle intake should build a filtered manifest without exporting."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.input_filter import is_processable_input
from core.source_bundle import SourceBundle, build_source_bundle


def test_source_bundle_filters_control_generated_and_unsupported_files() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source_dir = root / "incoming"
        source_dir.mkdir()

        real_md = source_dir / "activity_report.md"
        real_hwpx = source_dir / "official_report.hwpx"
        unsupported = source_dir / "raw_data.csv"
        generated_hwpx = source_dir / "generated.hwpx"

        real_md.write_text("# Activity report\n\nBody\n", encoding="utf-8")
        real_hwpx.write_bytes(b"fake hwpx source")
        unsupported.write_text("a,b\n1,2\n", encoding="utf-8")
        generated_hwpx.write_bytes(b"generated hwpx")
        (source_dir / "generated.document.json").write_text("{}", encoding="utf-8")

        ignored_names = [
            "README.md",
            "README.txt",
            "AGENTS.md",
            "AGENT.md",
            "CLAUDE.md",
            ".gitkeep",
            "activity_report.validation.txt",
            "activity_report.document.validation.txt",
            "activity_report.document.json",
            "activity_report.docx",
            "activity_report.pdf",
            "activity_report.pptx",
        ]
        for name in ignored_names:
            (source_dir / name).write_text("ignored", encoding="utf-8")

        bundle = build_source_bundle([source_dir])

        assert isinstance(bundle, SourceBundle)
        assert [doc.name for doc in bundle.documents] == [
            "activity_report.md",
            "official_report.hwpx",
        ]
        assert all(doc.processable for doc in bundle.documents)
        assert {doc.reason for doc in bundle.documents} == {"supported_input"}

        assert [doc.name for doc in bundle.unsupported_files] == ["raw_data.csv"]
        assert bundle.unsupported_files[0].reason == "unsupported_input_type"

        ignored_by_name = {item.name: item.reason for item in bundle.ignored_files}
        assert ignored_by_name["README.md"] == "repository_control_file"
        assert ignored_by_name["README.txt"] == "repository_control_file"
        assert ignored_by_name["AGENTS.md"] == "repository_control_file"
        assert ignored_by_name["AGENT.md"] == "repository_control_file"
        assert ignored_by_name["CLAUDE.md"] == "repository_control_file"
        assert ignored_by_name[".gitkeep"] == "repository_control_file"
        assert ignored_by_name["activity_report.validation.txt"] == "generated_validation_report"
        assert (
            ignored_by_name["activity_report.document.validation.txt"]
            == "generated_document_validation_report"
        )
        assert ignored_by_name["activity_report.document.json"] == "generated_document_model"
        assert ignored_by_name["activity_report.docx"] == "generated_office_output"
        assert ignored_by_name["activity_report.pdf"] == "generated_office_output"
        assert ignored_by_name["activity_report.pptx"] == "generated_office_output"
        assert ignored_by_name["generated.hwpx"] == "generated_hwpx_artifact"
        assert ignored_by_name["generated.document.json"] == "generated_document_model"

        assert bundle.summary == {
            "root_count": 1,
            "document_count": 2,
            "ignored_count": 14,
            "unsupported_count": 1,
            "total_file_count": 17,
        }


def test_source_bundle_accepts_single_file_and_multiple_roots() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        first = root / "first.md"
        second_dir = root / "second"
        second_dir.mkdir()
        second = second_dir / "second.hwp"
        control = second_dir / "README.md"

        first.write_text("# First\n", encoding="utf-8")
        second.write_bytes(b"fake hwp")
        control.write_text("# Control\n", encoding="utf-8")

        bundle = build_source_bundle([first, second_dir])

        assert [doc.relative_path for doc in bundle.documents] == [
            "first.md",
            "second.hwp",
        ]
        assert [ignored.relative_path for ignored in bundle.ignored_files] == ["README.md"]


def test_source_bundle_serializes_to_json_and_writes_no_outputs_to_input() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        source_dir = Path(tmp)
        (source_dir / "brief.md").write_text("# Brief\n", encoding="utf-8")

        before = {path.name for path in source_dir.iterdir()}
        bundle = build_source_bundle([source_dir])
        encoded = json.dumps(bundle.to_dict(), ensure_ascii=False, indent=2)
        decoded = json.loads(encoded)
        after = {path.name for path in source_dir.iterdir()}

        assert decoded["documents"][0]["name"] == "brief.md"
        assert decoded["summary"]["document_count"] == 1
        assert before == after


def test_existing_sample_input_filtering_behavior_is_preserved() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        generated_hwpx = root / "generated.hwpx"
        generated_hwpx.write_bytes(b"not a real hwpx")
        (root / "generated.validation.txt").write_text("report", encoding="utf-8")

        assert not is_processable_input(root / "README.md")
        assert not is_processable_input(root / "AGENTS.md")
        assert not is_processable_input(root / "sample.validation.txt")
        assert not is_processable_input(root / "sample.document.validation.txt")
        assert not is_processable_input(root / "sample.document.json")
        assert not is_processable_input(root / "sample.docx")
        assert not is_processable_input(root / "sample.pdf")
        assert not is_processable_input(root / "sample.pptx")
        assert not is_processable_input(generated_hwpx)

        assert is_processable_input(root / "actual_sample.md")
        assert is_processable_input(root / "actual_sample.hwp")
        assert is_processable_input(root / "actual_sample.hwpx")


if __name__ == "__main__":
    test_source_bundle_filters_control_generated_and_unsupported_files()
    test_source_bundle_accepts_single_file_and_multiple_roots()
    test_source_bundle_serializes_to_json_and_writes_no_outputs_to_input()
    test_existing_sample_input_filtering_behavior_is_preserved()
    print("PASS: source bundle")
