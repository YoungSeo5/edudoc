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
from core.generators.public_plan_generator import generate_public_plan_markdown  # noqa: E402
from core.registry import default_registry  # noqa: E402
from core.source_bundle import build_source_bundle  # noqa: E402
from core.source_profile import build_source_profile_from_document_models  # noqa: E402


def main(argv: list[str] | None = None) -> int:
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
        choices=("docx",),
        action="append",
        default=[],
        help="Optional final export format. Currently supports docx.",
    )
    args = parser.parse_args(argv)

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
                "error": "no converter found",
            })
            continue

        result = converter.convert(path)
        if not result.ok:
            failures.append({
                "path": str(path),
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
        _write_json(out_dir / "public_plan.failures.json", {
            "failures": failures,
            "bundle": bundle.to_dict(),
        })
        print("ERROR: no source documents could be converted", file=sys.stderr)
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
        export_result = DocxExporter().export(markdown_path, docx_path)
        _write_json(out_dir / "public_plan.export.docx.json", {
            "ok": export_result.ok,
            "error": export_result.error,
            "meta": export_result.meta,
            "output": str(export_result.output),
        })
        if not export_result.ok:
            print(f"ERROR: DOCX export failed: {export_result.error}", file=sys.stderr)
            return 1
        export_paths.append(docx_path)

    print(f"source_profile: {source_profile_path}")
    print(f"document_plan: {plan_path}")
    print(f"generated_markdown: {markdown_path}")
    for path in export_paths:
        print(f"export: {path}")
    if failures:
        failure_path = out_dir / "public_plan.failures.json"
        _write_json(failure_path, {"failures": failures})
        print(f"conversion_failures: {failure_path}")
    return 0


def _write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    raise SystemExit(main())
