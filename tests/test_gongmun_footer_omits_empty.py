"""Regression guard: 결문(footer) omits empty fields for both gonmun generators.

Records the footer-cleanup revision applied to skills/hwp-skill/scripts/gonmun.py
and gyeonggi_gonmun.py: empty 시행/접수/우편번호/전화 등 must NOT render as
label+blank-spacing lines. Non-empty footer fields must still render exactly.

This test is edudoc-owned (outside skills/) and imports the protected generators
as modules without modifying them. It skips gracefully if hwp-skill is absent.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SKILL_SCRIPTS = (
    Path(__file__).resolve().parent.parent / "skills" / "hwp-skill" / "scripts"
)


def _load(module_name: str):
    """Import a generator module by file path (skills dir isn't a package)."""
    path = _SKILL_SCRIPTS / f"{module_name}.py"
    if not path.exists():
        return None
    if str(_SKILL_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(_SKILL_SCRIPTS))
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _footer_lines(section_xml: str) -> list[str]:
    import re
    texts = [t for t in re.findall(r"<hp:t>(.*?)</hp:t>", section_xml) if t.strip()]
    out, hit = [], False
    for t in texts:
        if "─" in t:
            hit = True
        if hit:
            out.append(t)
    return out


def _check(build_section, base_meta: dict) -> None:
    # 1) empty footer fields -> only separator + 기안자/검토자/결재권자 line
    empty = dict(base_meta)
    for k in ("시행", "접수", "우편번호", "주소", "홈페이지", "전화", "전송", "이메일", "공개구분"):
        empty[k] = ""
    lines = _footer_lines(build_section(empty))
    assert len(lines) == 2, f"empty footer should be 2 lines, got {lines}"
    joined = "\n".join(lines)
    assert "시행" not in joined and "접수" not in joined, joined
    assert "전화" not in joined and "우 " not in joined, joined

    # 2) filled footer fields still render
    filled = dict(base_meta)
    filled.update({"시행": "○○과-1 (2026. 1. 2.)", "전화": "02-000-0000", "공개구분": "공개"})
    joined2 = "\n".join(_footer_lines(build_section(filled)))
    assert "시행 ○○과-1 (2026. 1. 2.)" in joined2, joined2
    assert "전화 02-000-0000" in joined2, joined2


def test_gonmun_footer_omits_empty_fields() -> int:
    mod = _load("gonmun")
    if mod is None:
        print("SKIP: hwp-skill gonmun.py not present")
        return 0
    _check(mod.build_section, {
        "기관명": "테스트기관", "수신": "수신자", "제목": "테스트",
        "발신명의": "테스트기관장", "기안자": "홍길동", "검토자": "김철수", "결재권자": "이영희",
        "body": ["안내합니다."],
    })
    print("PASS: gonmun footer omits empty fields")
    return 0


def test_gyeonggi_gonmun_footer_omits_empty_fields() -> int:
    mod = _load("gyeonggi_gonmun")
    if mod is None:
        print("SKIP: hwp-skill gyeonggi_gonmun.py not present")
        return 0
    _check(mod.build_section, {
        "기관명": "테스트기관", "수신": "수신자", "제목": "테스트",
        "발신명의": "테스트기관장", "기안자": "홍길동", "검토자": "김철수", "결재권자": "이영희",
        "본문": ["안내합니다."],
    })
    print("PASS: gyeonggi_gonmun footer omits empty fields")
    return 0


if __name__ == "__main__":
    test_gonmun_footer_omits_empty_fields()
    test_gyeonggi_gonmun_footer_omits_empty_fields()
    print("PASS: 결문 empty-field omission (both generators)")
