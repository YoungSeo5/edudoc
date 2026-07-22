"""Generate a public-plan Markdown draft from source samples."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.document_model import document_model_from_markdown  # noqa: E402
from core.document_plan import create_document_plan  # noqa: E402
from core.exporters.docx_exporter import DocxExporter  # noqa: E402
from core.exporters.style_profile import DEFAULT_PUBLIC_DOCUMENT_STYLE_PROFILE  # noqa: E402
from core.failure_log import DEFAULT_FAILURES_DIR, FailureRecord, record_failure  # noqa: E402
from core.generators.public_plan_generator import generate_public_plan_markdown  # noqa: E402
from core.renderers.hwp_skill_renderer import HwpSkillRenderer  # noqa: E402
from core.registry import default_registry  # noqa: E402
from core.source_bundle import build_source_bundle  # noqa: E402
from core.source_profile import build_source_profile_from_document_models  # noqa: E402


def main(argv: list[str] | None = None, *, failures_dir: Path | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a public-institution plan Markdown draft from source samples."
        ),
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Input files or directories such as samples/.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("exports") / "public-plan",
        help="Output directory.",
    )
    parser.add_argument(
        "--title",
        help="Optional generated plan title.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="Repository root used to locate reference document samples.",
    )
    parser.add_argument(
        "--export",
        choices=("docx", "hwpx"),
        action="append",
        default=[],
        help="Optional final export format. Supports docx and public-plan hwpx.",
    )
    args = parser.parse_args(argv)
    failures_dir = DEFAULT_FAILURES_DIR if failures_dir is None else failures_dir

    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    registry = default_registry()
    bundle = build_source_bundle(args.paths, registry=registry)
    models = []
    failures: list[dict] = []

    for document in bundle.documents:
        path = Path(document.path)
        converter = registry.find(path)
        if converter is None:
            failures.append({
                "path": str(path),
                "error_code": "converter_not_found",
                "error": "no converter found",
            })
            continue

        result = converter.convert(path)
        if not result.ok:
            failures.append({
                "path": str(path),
                "error_code": result.error_code or "conversion_failed",
                "error": result.error or "conversion failed",
            })
            continue

        if result.document_model is not None:
            models.append(result.document_model)
        else:
            models.append(
                document_model_from_markdown(
                    source_path=path,
                    file_format=path.suffix.lower().lstrip(".") or "markdown",
                    markdown=result.markdown,
                    raw_meta={
                        "converter": result.meta.get("converter"),
                        "structure_source": "markdown_fallback",
                    },
                )
            )

    if not models:
        for failure in failures:
            record_failure(
                failures_dir,
                FailureRecord(
                    entry_point="public_plan_cli",
                    stage="convert",
                    error_code=failure["error_code"],
                    source=failure["path"],
                    error=failure["error"],
                ),
            )
        if not failures:
            # every input was filtered out before conversion was attempted
            # (e.g. an unsupported file type) -- record that explicitly so
            # "no models" is never silent.
            record_failure(
                failures_dir,
                FailureRecord(
                    entry_point="public_plan_cli",
                    stage="convert",
                    error_code="no_processable_source",
                    source=", ".join(str(path) for path in args.paths),
                    error="no processable source documents found",
                    meta={"bundle_summary": dict(bundle.summary)},
                ),
            )
        print("ERROR: no source documents could be converted", file=sys.stderr)
        print(f"conversion_failures: {failures_dir}")
        return 2

    source_profile = build_source_profile_from_document_models(models)
    plan = create_document_plan(
        source_profile,
        "public_institution_plan",
        repo_root=args.repo_root,
        title=args.title,
    )
    markdown = generate_public_plan_markdown(plan)

    source_profile_path = out_dir / "public_plan.source_profile.json"
    plan_path = out_dir / "public_plan.document_plan.json"
    markdown_path = out_dir / "public_plan.generated.md"

    _write_json(source_profile_path, source_profile.to_dict())
    _write_json(plan_path, plan.to_dict())
    markdown_path.write_text(markdown, encoding="utf-8")

    export_paths: list[Path] = []
    if "docx" in args.export:
        docx_path = out_dir / "public_plan.docx"
        export_result = DocxExporter(
            style_profile=DEFAULT_PUBLIC_DOCUMENT_STYLE_PROFILE
        ).export(markdown_path, docx_path)
        if export_result.ok:
            _write_json(out_dir / "public_plan.export.docx.json", {
                "ok": export_result.ok,
                "error": export_result.error,
                "meta": export_result.meta,
                "output": str(export_result.output),
            })
        else:
            record_failure(
                failures_dir,
                FailureRecord(
                    entry_point="public_plan_cli",
                    stage="export",
                    error_code=export_result.error_code or "export_failed",
                    source=str(docx_path),
                    error=export_result.error or "export failed",
                    meta={"exporter": export_result.meta.get("exporter"), "format": "docx"},
                ),
            )
            print(f"ERROR: DOCX export failed: {export_result.error}", file=sys.stderr)
            return 1
        export_paths.append(docx_path)

    if "hwpx" in args.export:
        hwpx_path = out_dir / "public_plan.hwpx"
        render_result = HwpSkillRenderer(repo_root=ROOT).render_public_plan(
            plan,
            hwpx_path,
            contract_path=out_dir / "public_plan.hwpskill.input.json",
            include_title_page=True,
            include_table_of_contents=True,
        )
        if render_result.ok:
            _write_json(out_dir / "public_plan.export.hwpx.json", {
                "ok": render_result.ok,
                "error": render_result.error,
                "meta": render_result.meta,
                "output": str(render_result.output),
            })
        else:
            record_failure(
                failures_dir,
                FailureRecord(
                    entry_point="public_plan_cli",
                    stage="export",
                    error_code=render_result.error_code or "render_failed",
                    source=str(hwpx_path),
                    error=render_result.error or "export failed",
                    meta={"exporter": render_result.meta.get("engine"), "format": "hwpx"},
                ),
            )
            print(f"ERROR: HWPX render failed: {render_result.error}", file=sys.stderr)
            return 1
        export_paths.append(hwpx_path)

    print(f"source_profile: {source_profile_path}")
    print(f"document_plan: {plan_path}")
    print(f"generated_markdown: {markdown_path}")
    for path in export_paths:
        print(f"export: {path}")
    if failures:
        for failure in failures:
            record_failure(
                failures_dir,
                FailureRecord(
                    entry_point="public_plan_cli",
                    stage="convert",
                    error_code=failure["error_code"],
                    source=failure["path"],
                    error=failure["error"],
                ),
            )
        print(f"conversion_failures: {failures_dir}")
    return 0


def _write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    raise SystemExit(main())
