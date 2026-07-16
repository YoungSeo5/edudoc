"""Snapshot the HWPX converter output *before* the locator change.

Run this only to (re)generate the baseline. The regression test
(tests/test_document_model_locator.py) compares the current converter against
these snapshots to prove the existing Markdown and the existing DocumentModel
fields did not change when native locators were added.

    python tests/fixtures/converter_baseline/make_baseline.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from core.hwp_converter import HwpSkillConverter  # noqa: E402

# Both inputs are tracked in this repository. Template assets are read only.
SOURCES = {
    "sample_business_plan": "samples/참가신청서 및 사업계획서 양식_기창 (1).hwpx",
    "fss_one_page_source": "skills/templates/금융감독원/금감원 원페이지/source.hwpx",
}

OUT_DIR = Path(__file__).resolve().parent


def snapshot(relative_path: str) -> dict:
    result = HwpSkillConverter().convert(ROOT / relative_path)
    if not result.ok or result.document_model is None:
        raise SystemExit(f"conversion failed for {relative_path}: {result.error}")

    model = result.document_model.to_dict()
    # absolute path is machine-specific; the rest must stay byte-identical
    model["source_path"] = Path(relative_path).name
    return {
        "source": relative_path,
        "markdown": result.markdown,
        "document_model": model,
    }


def main() -> int:
    for name, relative_path in SOURCES.items():
        data = snapshot(relative_path)
        out = OUT_DIR / f"{name}.json"
        out.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        model = data["document_model"]
        print(
            f"{out.name}: markdown={len(data['markdown'])} chars, "
            f"paragraphs={len(model['paragraphs'])}, tables={len(model['tables'])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
