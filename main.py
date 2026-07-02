"""
edudoc Phase 0 진입점.

사용법:
  python main.py run <파일_또는_폴더> [--export docx,pdf]
  python main.py watch [감시폴더] [--export docx,pdf]

예:
  python main.py run samples/
  python main.py run samples/report.hwpx
  python main.py run samples/draft.md --export docx,pdf
  python main.py watch
"""
from __future__ import annotations

import sys
from pathlib import Path

from core.pipeline import Pipeline, PipelineConfig


def _parse_export_formats(argv: list[str]) -> tuple[str, ...]:
    """Return explicitly requested output formats, if any."""
    for i, arg in enumerate(argv):
        if arg == "--export" and i + 1 < len(argv):
            return _normalize_export_formats(argv[i + 1])
        if arg.startswith("--export="):
            return _normalize_export_formats(arg.split("=", 1)[1])
    return ()


def _normalize_export_formats(value: str) -> tuple[str, ...]:
    formats = []
    for item in value.split(","):
        item = item.strip().lower()
        if not item:
            continue
        formats.append(item if item.startswith(".") else f".{item}")
    return tuple(formats)


def _print_result(r) -> None:  # noqa: ANN001
    tag = "OK " if r.ok else "FAIL"
    line = f"[{tag}] {r.source.name}"
    if r.ok:
        out = r.meta.get("output", "(미저장)")
        line += f"  ->  {out}"
        if "validation_passed" in r.meta:
            state = "통과" if r.meta["validation_passed"] else "확인 필요"
            line += f"  | 검수: {state}"
        if r.meta.get("exports"):
            exports = r.meta["exports"]
            stable = [e["format"] for e in exports if e.get("ok") and e.get("stabilized")]
            fallback = [e["format"] for e in exports if e.get("ok") and not e.get("stabilized")]
            failed = [e["format"] for e in exports if not e.get("ok")]
            if stable:
                line += f"  | 출력 성공: {', '.join(stable)}"
            if fallback:
                line += f"  | 출력(fallback·실험적): {', '.join(fallback)}"
            if failed:
                line += f"  | 출력 실패: {', '.join(failed)}"
    else:
        line += f"  :: {r.error}"
    print(line)


def cmd_run(target: Path, pipeline: Pipeline) -> int:
    if target.is_dir():
        results = pipeline.process_dir(target)
        if not results:
            print(f"[run] 변환 대상 파일 없음: {target} "
                  f"(지원 확장자: {sorted(pipeline.registry.supported_ext)})")
        for r in results:
            _print_result(r)
        failed = sum(1 for r in results if not r.ok)
        return 1 if failed else 0
    else:
        r = pipeline.process_file(target)
        _print_result(r)
        return 0 if r.ok else 1


def cmd_watch(folder: Path, pipeline: Pipeline) -> int:
    from connectors.folder_watcher import watch

    def on_file(path: Path) -> None:
        if pipeline.registry.find(path):
            _print_result(pipeline.process_file(path))

    watch(folder, on_file)
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2

    command = argv[1]
    export_formats = _parse_export_formats(argv)
    pipeline = Pipeline(config=PipelineConfig(
        output_dir=Path("exports"),
        validate_gongmun=True,
        write_validation_report=True,
        export_formats=export_formats,
    ))

    if command == "run":
        if len(argv) < 3:
            print("run: 대상 경로가 필요합니다.  예) python main.py run samples/")
            return 2
        return cmd_run(Path(argv[2]), pipeline)

    if command == "watch":
        folder = Path(argv[2]) if len(argv) >= 3 else Path("samples")
        return cmd_watch(folder, pipeline)

    print(f"알 수 없는 명령: {command}")
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
