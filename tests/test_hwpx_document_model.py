"""HWPX -> Markdown + DocumentModel smoke test."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.pipeline import Pipeline, PipelineConfig


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    sample = root / "samples" / "참가신청서 및 사업계획서 양식_기창 (1).hwpx"
    assert sample.exists(), f"HWPX sample not found: {sample}"

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "exports"
        pipe = Pipeline(config=PipelineConfig(
            output_dir=out,
            write_files=True,
            validate_gongmun=True,
            write_validation_report=True,
        ))

        result = pipe.process_file(sample)

        assert result.ok, f"HWPX conversion failed: {result.error}"
        assert result.markdown.strip(), "Markdown output is empty"

        md_path = out / f"{sample.stem}.md"
        model_path = out / f"{sample.stem}.document.json"
        report_path = out / f"{sample.stem}.validation.txt"

        assert md_path.exists(), "Markdown output file missing"
        assert model_path.exists(), "DocumentModel JSON file missing"
        assert report_path.exists(), "validation report missing"

        model = json.loads(model_path.read_text(encoding="utf-8"))
        assert model["source_path"].endswith(sample.name)
        assert model["format"] == "hwpx"
        assert isinstance(model["paragraphs"], list)
        assert isinstance(model["tables"], list)
        assert isinstance(model["attachments"], list)
        assert isinstance(model["raw_meta"], dict)
        assert model["raw_meta"].get("structure_source") in {
            "markdown_fallback",
            "hwpx_package_metadata_plus_markdown_fallback",
            "hwpx_xml_metadata_plus_markdown_fallback",
        }
        assert model["raw_meta"].get("hwpx_package_detected") is True
        assert model["raw_meta"].get("native_metadata_available") is True
        assert model["raw_meta"].get("native_metadata_source") == "zip_package"
        assert model["raw_meta"].get("xml_file_count", 0) > 0
        assert model["raw_meta"].get("section_file_count", 0) > 0
        assert "package_entries" in model["raw_meta"]
        assert model["raw_meta"].get("content_hpf_present") is True
        assert model["raw_meta"].get("manifest_present") is True
        assert model["raw_meta"].get("header_xml_present") is True
        assert model["raw_meta"].get("xml_metadata_available") is True
        assert isinstance(model["raw_meta"].get("section_files"), list)
        assert model["raw_meta"].get("manifest_item_count", 0) > 0
        assert model["raw_meta"].get("extracted_xml_fields")
        assert model["paragraphs"] or model["tables"], "DocumentModel has no structure"

        print("PASS: HWPX -> Markdown + DocumentModel")
        print("  markdown:", md_path.name)
        print("  document:", model_path.name)
        print("  paragraphs:", len(model["paragraphs"]))
        print("  tables:", len(model["tables"]))
        print("  xml files:", model["raw_meta"].get("xml_file_count"))
        print("  title:", model["raw_meta"].get("document_title_candidate"))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
