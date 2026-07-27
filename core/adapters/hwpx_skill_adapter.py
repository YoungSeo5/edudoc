"""Safe adapter for the project-local hwpx-skill HWP -> HWPX flow.

The skill's ``scripts/convert_hwp.py`` documents the intended conversion flow,
but it may auto-install packages or clone external repositories. edudoc must not
do hidden setup in the default runtime, so this adapter only uses an already
available ``hwp2hwpx`` engine.
"""
from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Iterable


DEFAULT_SKILL_DIR = Path("skills") / "hwp-skill"
ENV_HWP2HWPX_PATH = "EDUDOC_HWP2HWPX_PATH"

# 이 모듈의 경계:
# 레거시 HWP → 이미 준비된 hwp2hwpx 엔진으로 HWPX 변환
#            → 안전한 후처리와 원본 근거 기반 속성 보정
#            → 실제 HWPX 템플릿 제작 경로에 넘길 변환 결과
# 엔진 설치·저장소 복제·protected skill 수정은 수행하지 않는다.

class HwpToHwpxAdapterError(RuntimeError):
    """Raised when the safe HWP -> HWPX adapter cannot run."""


@dataclass(frozen=True)
class HwpToHwpxResult:
    input_path: Path
    output_path: Path
    engine: str
    skill_dir: Path
    postprocess_steps: list[str] = field(default_factory=list)

    def to_meta(self) -> dict:
        return {
            "hwp_to_hwpx_adapter": "hwpx_skill_adapter",
            "hwp_to_hwpx_engine": self.engine,
            "hwp_to_hwpx_skill_dir": str(self.skill_dir),
            "hwp_to_hwpx_output": str(self.output_path),
            "hwp_to_hwpx_postprocess_steps": list(self.postprocess_steps),
        }


def convert_hwp_to_hwpx(
    input_path: Path | str,
    output_path: Path | str,
    *,
    skill_dir: Path | str = DEFAULT_SKILL_DIR,
    hwp2hwpx_paths: Iterable[Path | str] = (),
    include_installed: bool = True,
    run_skill_postprocessors: bool = True,
    reconcile_cell_valign: bool = True,
    reconcile_char_flags: bool = True,
) -> HwpToHwpxResult:
    """Convert HWP to HWPX using an already available hwp2hwpx engine.

    This function never installs packages, clones repositories, or modifies files
    under ``skills/``. It writes only the requested output file.
    """
    src = Path(input_path)
    dst = Path(output_path)
    skill_path = Path(skill_dir)

    # 흐름 1: protected skill의 참조 스크립트가 존재하는지 확인한 뒤,
    # 설치된 엔진 또는 명시적으로 허용된 로컬 경로에서 hwp2hwpx를 찾는다.
    _validate_skill_reference(skill_path)
    module, engine_source = _load_hwp2hwpx(
        extra_paths=_candidate_engine_paths(skill_path, hwp2hwpx_paths),
        include_installed=include_installed,
    )

    convert_file = getattr(module, "convert_file", None)
    if convert_file is None:
        raise HwpToHwpxAdapterError(
            "hwp2hwpx engine is available but does not expose convert_file()"
        )

    # 흐름 2: 엔진의 공개 convert_file 계약으로 HWP를 HWPX로 변환한다.
    # 엔진이 반환 경로를 생략하면 요청한 출력 경로를 결과로 간주한다.
    dst.parent.mkdir(parents=True, exist_ok=True)
    convert_result = convert_file(str(src), str(dst))
    converted = Path(convert_result) if convert_result is not None else dst
    if not converted.exists():
        raise HwpToHwpxAdapterError(
            f"hwp2hwpx did not create expected output: {converted}"
        )

    # 흐름 3: protected skill이 제공하는 선택적 보정 함수는 변환 성공을
    # 무효화하지 않는 best-effort 단계로 실행한다.
    postprocess_steps: list[str] = []
    if run_skill_postprocessors:
        postprocess_steps = _run_best_effort_postprocessors(skill_path, converted)

    if reconcile_cell_valign:
        # 흐름 4: 원본 HWP에서 확인한 셀 세로 정렬을 변환 HWPX에 복원한다.
        from .hwp_cell_valign import reconcile_hwpx_cell_valign

        reconciled = reconcile_hwpx_cell_valign(src, converted)
        if reconciled.get("applied") and reconciled.get("changed"):
            postprocess_steps.append("reconcile_cell_valign")

    if reconcile_char_flags:
        # 흐름 5: 원본 HWP에서 확인한 기울임·굵기 플래그를 복원한다.
        from .hwp_char_flags import reconcile_hwpx_char_flags

        flags_result = reconcile_hwpx_char_flags(src, converted)
        if flags_result.get("applied") and flags_result.get("changed"):
            postprocess_steps.append("reconcile_char_flags")

    return HwpToHwpxResult(
        input_path=src,
        output_path=converted,
        engine=engine_source,
        skill_dir=skill_path,
        postprocess_steps=postprocess_steps,
    )


# protected skill은 실행 엔진이 아니라 변환 계약의 참조다. 실제 엔진은
# 아래 탐색 순서에 따라 별도로 찾는다.
def _validate_skill_reference(skill_dir: Path) -> None:
    convert_script = skill_dir / "scripts" / "convert_hwp.py"
    if not convert_script.exists():
        raise HwpToHwpxAdapterError(
            f"hwpx-skill convert_hwp.py was not found: {convert_script}"
        )


def _candidate_engine_paths(
    skill_dir: Path,
    explicit_paths: Iterable[Path | str],
) -> list[Path]:
    # 탐색 우선순위: 환경변수 → 호출자가 넘긴 경로 → 프로젝트의 알려진 로컬 경로.
    candidates: list[Path] = []
    env_path = os.environ.get(ENV_HWP2HWPX_PATH)
    if env_path:
        candidates.append(Path(env_path))

    candidates.extend(Path(path) for path in explicit_paths)
    candidates.extend(
        [
            Path("tools") / "hwp2hwpx-python-refactor",
            Path("skills") / "hwp2hwpx-python-refactor",
            skill_dir / "hwp2hwpx-python-refactor",
            skill_dir / ".hwp2hwpx-repo",
        ]
    )
    return candidates


def _load_hwp2hwpx(
    *,
    extra_paths: Iterable[Path],
    include_installed: bool,
) -> tuple[ModuleType, str]:
    # 설치된 패키지를 먼저 허용하고, 없으면 후보 경로를 하나씩 import한다.
    # 어느 경로에서도 찾지 못하면 자동 설치하지 않고 명시적인 오류를 낸다.
    if include_installed:
        try:
            return importlib.import_module("hwp2hwpx"), "installed:hwp2hwpx"
        except ImportError:
            pass

    for candidate in extra_paths:
        full = candidate.resolve()
        package_dir = full / "hwp2hwpx"
        if not package_dir.is_dir():
            continue
        sys.path.insert(0, str(full))
        try:
            importlib.invalidate_caches()
            return importlib.import_module("hwp2hwpx"), f"local:{full}"
        except ImportError:
            if str(full) in sys.path:
                sys.path.remove(str(full))
            continue

    raise HwpToHwpxAdapterError(
        "hwp2hwpx engine is not available. Install it explicitly or set "
        f"{ENV_HWP2HWPX_PATH} to a local hwp2hwpx-python-refactor checkout. "
        "edudoc will not auto-install packages or clone repositories."
    )


def _run_best_effort_postprocessors(skill_dir: Path, hwpx_path: Path) -> list[str]:
    """Run safe postprocessors from the skill script if it imports cleanly."""
    # 참조 스크립트 전체 흐름을 실행하지 않고, 안전하다고 정한 보정 함수만
    # 동적으로 불러 호출한다.
    script_path = skill_dir / "scripts" / "convert_hwp.py"
    spec = importlib.util.spec_from_file_location("edudoc_hwpx_skill_convert", script_path)
    if spec is None or spec.loader is None:
        return []

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception:  # noqa: BLE001 - best-effort optional skill hook
        return []

    steps: list[str] = []
    for name in ("_fix_char_borders", "_fix_text_direction"):
        func = getattr(module, name, None)
        if func is None:
            continue
        try:
            func(str(hwpx_path))
            steps.append(name)
        except Exception:  # noqa: BLE001 - conversion already succeeded
            continue
    return steps
