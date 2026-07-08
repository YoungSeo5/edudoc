"""CLI flow: samples -> SourceProfile -> DocumentPlan -> public-plan Markdown."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.public_plan.generate_from_samples import main  # noqa: E402


SAMPLE_MARKDOWN = """# AI 교육 운영 계획

경기도교육청 미래교육과는 2026. 7. 15. AI 교육 운영 계획을 추진한다.

1. 추진 배경: 학교 현장의 AI 활용 수업 지원 필요
2. 주요 내용: 교원 연수 3회, 학생 캠프 120명 운영
3. 추진일정: 2026. 7. 15.부터 2026. 9. 30.까지
4. 예산: 12,000,000원
5. 개선 필요: 신청 절차 보완

| 구분 | 내용 | 인원 |
| --- | --- | --- |
| 연수 | 교원 대상 | 80명 |
| 캠프 | 학생 대상 | 120명 |

붙임  세부 추진 일정 1부.
"""


def test_public_plan_cli_generates_markdown_and_plan_files() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        samples = root / "samples"
        out_dir = root / "out"
        repo_root = root / "repo"
        reference_dir = repo_root / "references" / "document-types" / "public-plan" / "samples"
        samples.mkdir()
        reference_dir.mkdir(parents=True)

        (samples / "ai_plan.md").write_text(SAMPLE_MARKDOWN, encoding="utf-8")
        (samples / "README.md").write_text("# ignored\n", encoding="utf-8")
        (reference_dir / "public_plan_reference.pdf").write_bytes(b"%PDF-1.7\n")

        exit_code = main([
            str(samples),
            "--out",
            str(out_dir),
            "--repo-root",
            str(repo_root),
        ])

        assert exit_code == 0
        markdown_path = out_dir / "public_plan.generated.md"
        plan_path = out_dir / "public_plan.document_plan.json"
        source_profile_path = out_dir / "public_plan.source_profile.json"

        assert markdown_path.exists()
        assert plan_path.exists()
        assert source_profile_path.exists()

        markdown = markdown_path.read_text(encoding="utf-8")
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        source_profile = json.loads(source_profile_path.read_text(encoding="utf-8"))

        assert "# AI 교육 운영 계획" in markdown
        assert "## 1. 추진 배경" in markdown
        assert "## 기준 참고 문서" in markdown
        assert "public_plan_reference.pdf" in markdown
        assert "확인 필요" in markdown
        assert plan["target_profile_id"] == "public_institution_plan"
        assert source_profile["documents"][0]["name"] == "ai_plan.md"


def test_public_plan_cli_can_export_docx() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        samples = root / "samples"
        out_dir = root / "out"
        repo_root = root / "repo"
        reference_dir = repo_root / "references" / "document-types" / "public-plan" / "samples"
        samples.mkdir()
        reference_dir.mkdir(parents=True)

        (samples / "ai_plan.md").write_text(SAMPLE_MARKDOWN, encoding="utf-8")
        (reference_dir / "public_plan_reference.pdf").write_bytes(b"%PDF-1.7\n")

        exit_code = main([
            str(samples),
            "--out",
            str(out_dir),
            "--repo-root",
            str(repo_root),
            "--export",
            "docx",
        ])

        docx_path = out_dir / "public_plan.docx"
        export_meta_path = out_dir / "public_plan.export.docx.json"

        assert exit_code == 0
        assert docx_path.exists()
        assert docx_path.stat().st_size > 0
        assert export_meta_path.exists()
        export_meta = json.loads(export_meta_path.read_text(encoding="utf-8"))
        assert export_meta["ok"] is True
        assert export_meta["meta"]["exporter"] == "DocxExporter"


def test_public_plan_cli_can_render_hwpx_with_hwp_skill() -> None:
    skill_script = (
        Path(__file__).resolve().parent.parent
        / "skills" / "hwp-skill" / "scripts" / "gyehoek.py"
    )
    if not skill_script.exists():
        print("SKIP: hwp-skill gyehoek.py not present")
        return

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        samples = root / "samples"
        out_dir = root / "out"
        repo_root = root / "repo"
        reference_dir = repo_root / "references" / "document-types" / "public-plan" / "samples"
        samples.mkdir()
        reference_dir.mkdir(parents=True)

        (samples / "ai_plan.md").write_text(SAMPLE_MARKDOWN, encoding="utf-8")
        (reference_dir / "public_plan_reference.pdf").write_bytes(b"%PDF-1.7\n")

        exit_code = main([
            str(samples),
            "--out",
            str(out_dir),
            "--repo-root",
            str(repo_root),
            "--export",
            "hwpx",
        ])

        hwpx_path = out_dir / "public_plan.hwpx"
        contract_path = out_dir / "public_plan.hwpskill.input.json"
        export_meta_path = out_dir / "public_plan.export.hwpx.json"

        assert exit_code == 0
        assert hwpx_path.exists()
        assert hwpx_path.stat().st_size > 0
        assert hwpx_path.read_bytes()[:2] == b"PK"
        assert contract_path.exists()
        assert export_meta_path.exists()

        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        export_meta = json.loads(export_meta_path.read_text(encoding="utf-8"))
        assert contract["target_profile_id"] == "public_institution_plan"
        assert contract["include_title_page"] is True
        assert contract["include_table_of_contents"] is True
        assert export_meta["ok"] is True
        assert export_meta["meta"]["engine"] == "hwp-skill/gyehoek.py"
        assert export_meta["meta"]["validation"]["passed"] is True


def test_public_plan_cli_reports_when_no_sources_convert() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        samples = root / "samples"
        out_dir = root / "out"
        samples.mkdir()
        (samples / "raw.csv").write_text("a,b\n1,2\n", encoding="utf-8")

        exit_code = main([str(samples), "--out", str(out_dir)])

        assert exit_code == 2
        assert (out_dir / "public_plan.failures.json").exists()


if __name__ == "__main__":
    test_public_plan_cli_generates_markdown_and_plan_files()
    test_public_plan_cli_can_export_docx()
    test_public_plan_cli_can_render_hwpx_with_hwp_skill()
    test_public_plan_cli_reports_when_no_sources_convert()
    print("PASS: public plan CLI")
