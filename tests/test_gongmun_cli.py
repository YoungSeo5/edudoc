"""Smoke test for the Gongmun brief generation CLI."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def test_gongmun_cli_writes_draft_and_validation_report() -> None:
    root = Path(__file__).resolve().parent.parent
    script = root / "scripts" / "gongmun" / "generate_from_brief.py"
    brief = root / "skills" / "gongmun_writer" / "examples" / "input_brief.md"

    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "gongmun"
        completed = subprocess.run(
            [
                sys.executable,
                str(script),
                str(brief),
                "--out",
                str(out_dir),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        assert completed.returncode == 0, completed.stderr or completed.stdout

        generated_path = out_dir / "input_brief.generated.md"
        report_path = out_dir / "input_brief.validation.txt"

        assert generated_path.exists(), "generated Markdown file missing"
        assert report_path.exists(), "validation report file missing"

        draft = generated_path.read_text(encoding="utf-8")
        report = report_path.read_text(encoding="utf-8")

        assert draft.startswith("# "), "Generated draft should start with a Markdown title"
        assert "수신: 관내 초·중·고등학교장" in draft
        assert "담당: 교육지원과 홍길동" in draft
        assert "관련: 2026년 교원 역량 강화 연수 운영 계획" in draft
        assert "1. 대상: 희망 교원" in draft
        assert "2. 내용: 디지털 수업 설계 연수 참가 신청" in draft
        assert "붙임  참가 신청서 1부.  끝." in draft
        assert "끝." in draft
        assert "2026. 7. 15." in draft
        assert "검수 결과" in report


if __name__ == "__main__":
    test_gongmun_cli_writes_draft_and_validation_report()
    print("PASS: Gongmun CLI")
