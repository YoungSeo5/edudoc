"""
스켈레톤 자체 검증.

실제 hwp 스킬 없이도 파이프라인/레지스트리/저장 흐름이 도는지 확인한다.
- FakeConverter: .txt를 받아 간단한 md로 변환 (실 변환기 자리에 끼워 넣는 스텁)
- 이 테스트가 통과하면 '변환기만 채우면 완성'인 상태라는 뜻.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.converter_base import BaseConverter, ConvertResult
from core.registry import ConverterRegistry
from core.pipeline import Pipeline, PipelineConfig


class FakeConverter(BaseConverter):
    supported_ext = (".txt",)

    def convert(self, path: Path) -> ConvertResult:
        text = path.read_text(encoding="utf-8")
        md = f"# {path.stem}\n\n{text.strip()}\n"
        return ConvertResult(source=path, markdown=md, ok=True,
                             meta={"converter": self.name})


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        src = tmp / "in"
        out = tmp / "out"
        src.mkdir()

        (src / "hello.txt").write_text("첫 줄\n둘째 줄", encoding="utf-8")
        (src / "note.txt").write_text("메모 내용", encoding="utf-8")
        (src / "skip.bin").write_text("무시될 파일", encoding="utf-8")

        reg = ConverterRegistry()
        reg.register(FakeConverter())
        pipe = Pipeline(registry=reg,
                        config=PipelineConfig(output_dir=out, write_files=True))

        results = pipe.process_dir(src)

        assert len(results) == 2, f"txt 2개만 처리돼야 함, 실제 {len(results)}"
        assert all(r.ok for r in results), "모든 변환 성공해야 함"

        made = sorted(p.name for p in out.glob("*.md"))
        assert made == ["hello.md", "note.md"], f"출력 파일 불일치: {made}"

        content = (out / "hello.md").read_text(encoding="utf-8")
        assert content.startswith("# hello"), "md 헤더 생성 확인"

        # 미지원 확장자 방어
        bad = pipe.process_file(src / "skip.bin")
        assert not bad.ok and "지원하지 않는" in (bad.error or "")

        print("PASS: 파이프라인 왕복(입력->md->저장) 정상")
        print("  처리:", [r.source.name for r in results])
        print("  출력:", made)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
