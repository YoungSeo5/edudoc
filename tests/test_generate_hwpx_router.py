"""skills/hwp-skill/scripts/generate_hwpx.py: document-type auto-routing to
hwp-skill generators (gonmun/gyeonggi_gonmun/bodojaryo/gyehoek/md2hwpx).

Unit-tests classification (pure Python, no subprocess) for all 5 doc types, then
runs one real end-to-end generation to prove dispatch + validation works. This
test file lives outside skills/ (protected); it only imports/exercises the
router module and never modifies skills/hwp-skill/ itself.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_ROUTER_DIR = Path(__file__).resolve().parent.parent / "skills" / "hwp-skill" / "scripts"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(_ROUTER_DIR))

if not (_ROUTER_DIR / "generate_hwpx.py").exists():
    print("SKIP: skills/hwp-skill/scripts/generate_hwpx.py not present")
    raise SystemExit(0)

from generate_hwpx import RouterError, classify_doc_type, generate  # noqa: E402

FIXTURE_MD = (
    Path(__file__).resolve().parent
    / "fixtures" / "export" / "wide_table_activity_report.md"
)


def _write_json(tmp: Path, name: str, data: dict) -> Path:
    path = tmp / name
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def test_classifies_gonmun() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = _write_json(Path(tmp), "a.json", {
            "수신": "○○○학교장", "발신명의": "교육감", "기안자": "홍길동",
        })
        assert classify_doc_type(path) == "gonmun"


def test_classifies_gyeonggi_gonmun() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = _write_json(Path(tmp), "a.json", {
            "수신": "○○○학교장", "핵심용어": "제출", "학교실행표시": {"사용": True},
        })
        assert classify_doc_type(path) == "gyeonggi_gonmun"


def test_classifies_bodojaryo() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = _write_json(Path(tmp), "a.json", {
            "보도시점": "2026. 6. 24.(수) 09:00 이후", "제목": "보도자료",
        })
        assert classify_doc_type(path) == "bodojaryo"


def test_classifies_markdown_by_extension() -> None:
    assert classify_doc_type(FIXTURE_MD) == "markdown"


def test_gyehoek_requires_explicit_doc_type() -> None:
    # gyehoek has no natural JSON schema of its own; ambiguous keys must error.
    with tempfile.TemporaryDirectory() as tmp:
        path = _write_json(Path(tmp), "a.json", {"제목": "계획서", "목차": True})
        try:
            classify_doc_type(path)
            assert False, "expected RouterError for ambiguous keys"
        except RouterError:
            pass
        assert classify_doc_type(path, explicit="gyehoek") == "gyehoek"


def test_ambiguous_json_raises_router_error() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = _write_json(Path(tmp), "a.json", {"foo": "bar"})
        try:
            classify_doc_type(path)
            assert False, "expected RouterError"
        except RouterError:
            pass


def test_end_to_end_gonmun_generation() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        meta_path = _write_json(tmp_path, "meta.json", {
            "기관명": "테스트기관",
            "수신": "수신자 참조",
            "제목": "테스트 안내",
            "발신명의": "테스트기관장",
            "body": ["안내 사항을 공지합니다."],
            "붙임": ["참고자료 1부."],
        })
        output = tmp_path / "out.hwpx"
        result = generate(meta_path, output)

        if not result["ok"] and "hwp-skill script not found" in (result.get("error") or ""):
            print("SKIP: hwp-skill not present; router dispatch not exercised")
            return

        assert result["ok"], result.get("error")
        assert result["doc_type"] == "gonmun"
        assert output.exists() and output.stat().st_size > 0
        assert result["validation"]["passed"] is True, result["validation"]


if __name__ == "__main__":
    test_classifies_gonmun()
    test_classifies_gyeonggi_gonmun()
    test_classifies_bodojaryo()
    test_classifies_markdown_by_extension()
    test_gyehoek_requires_explicit_doc_type()
    test_ambiguous_json_raises_router_error()
    test_end_to_end_gonmun_generation()
    print("PASS: generate_hwpx router (classification + dispatch)")
