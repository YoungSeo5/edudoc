# CLAUDE.md

edudoc 프로젝트에서 Claude(및 코딩 에이전트)가 따르는 작업 규칙.
하네스 엔지니어링(harness engineering)의 기반 자료로 사용한다.

## 대화 방식
- 불필요한 인사말 없이 바로 답한다.
- 확실하지 않은 사실, 날짜, 수치, 출처는 먼저 불확실하다고 말한다.
- 간단한 질문은 짧게, 복잡한 작업은 충분히 자세히 답한다.

## 현재-HEAD 근거 원칙 (구현 상태 판정 시)
- `exports/`, `sandbox/`, `.omo/`, 캐시(`.pytest_cache/` 등), `*.log` 같은 생성물·임시 산출물을 현재 구현의 근거로 사용하지 않는다.
- 구현됨·미구현·버그 주장은 모두 현재 Git `HEAD`의 canonical source 파일과 현재 실행 또는 테스트 결과로 입증한다.
- 주장마다 확인한 canonical 파일 경로와 그 근거를 재현하는 정확한 명령을 함께 제시한다.
- 과거 기록·생성물·임시 파일은 맥락은 될 수 있어도 현재 동작을 증명하지 못한다. 현재 소스와 실행으로 확정되지 않으면 추론하지 말고 미검증으로 표기한다.

## 변경 통제
- 사용자가 요청하지 않은 파일, 문단, 구조는 바꾸지 않는다.
- 큰 변경, 삭제, 덮어쓰기, 외부 전송은 먼저 무엇을 바꿀지 설명하고 확인을 받는다.
- 작업이 끝나면 변경한 내용과 확인이 필요한 점을 짧게 정리한다.

## 사용자와 프로젝트 맥락
- 대상 사용자: 문서 변환·자동화 파이프라인을 만드는 개발자.
  공문서(교육청) 형식 규칙과 HWP/HWPX 처리에 익숙하지 않을 수 있음.
- 프로젝트 목표: 입력·출력 형식을 가리지 않는 범용 문서 변환·생성 엔진.
  Phase 0은 로컬 문서로 변환 흐름을 검증하는 데 집중.
- 핵심 원칙:
  - HWPX-first: 현재 MVP의 기본 입력은 `.hwpx`이며, `.hwp`는 레거시/호환용 fallback으로만 본다.
  - 사용자 편의 최우선: 최종 사용자가 별도 설치·설정 없이 바로 쓸 수 있어야 하며,
    필요한 것은 `pip install -r requirements.txt` 한 번으로 끝나야 한다.
  - 프로젝트 경량 유지: pip 네이티브 의존성을 기본 엔진으로 삼고,
    무거운 바이너리(Pandoc/LaTeX/번들 exe)는 기본 워크플로가 요구하지 않는 옵션 fallback으로 둔다.
  - 외부 도구(hwp 스킬 / hwpx-skill / hwp2md / md-to-office)는 소스를 복사하지 않고
    pip 의존성 또는 빌드된 바이너리로만 참조한다.
  - 변환기는 인터페이스로 추상화한다(교체·병행이 코드 수정 없이 되도록).
  - 공문서는 '생성-검증 루프'로 만든다(검사 가능한 규칙은 코드로 강제).
- 선호 톤: 친절하고 차분하지만 장황하지 않게.
- 피할 것: 검증되지 않은 수치, 과장된 표현, 불필요한 전문용어.
  특히 공문서 세부 규칙은 대상 기관 최신 지침 확인 전까지 단정하지 않는다.

## 기억과 연속성
- 중요한 결정은 `MEMORY.md`에 남긴다.
- 세션을 끝낼 때 완료한 일, 진행 중인 일, 다음 할 일을 요약한다.

## 개발 작업 안전
- 현재 요청과 직접 관련된 파일과 코드만 수정한다.
- 기술 스택
  - 주 언어: Python (core, validators, connectors, main).
  - 보조: Rust (hwp2md는 cargo 빌드 후 CLI로 호출).
  - 의존성은 `requirements.txt`로 관리. 외부 도구 소스는 저장소에 넣지 않는다.
- 테스트 명령
  - 파이프라인 검증: `python tests/test_pipeline.py`
  - 실행: `python main.py run samples/` / `python main.py watch`
- 변환기 확장 시: `core/converter_base.py` 인터페이스를 구현하고
  `core/registry.py`에 등록만 한다. 기존 변환기 파일은 수정하지 않는다.
- 새로운 구조·테스트·하네스 판단은 HWPX-first 방향을 기준으로 한다.
  HWP fallback 구현은 보존하되 기본 MVP 경로로 승격하지 않는다.

## 핵심 HWPX 템플릿 파이프라인

프로젝트 루트는 `C:\Users\work\edudoc`이다. HWP/HWPX 템플릿 작업에서는
다음 경로와 경계를 기준으로 한다.

1. HWP → HWPX 변환
   - 로컬 엔진: `tools/hwp2hwpx-python-refactor/hwp2hwpx/`
   - 호출 어댑터: `core/adapters/hwpx_skill_adapter.py`
   - 자동 설치·자동 복제 없이 이미 준비된 로컬 엔진만 사용한다.
2. HWPX 분해 및 템플릿 후보 생성
   - 패키지 추출: `core/templates/hwpx_package_extractor.py`
   - 고정 서식/가변 내용 분리: `core/templates/hwpx_content_separator.py`
   - CLI: `scripts/templates/separate_hwpx_template_content.py`
   - 결과 XML: `skills/templates/<template-id>/template/header.xml` 및
     `section*.template.xml`
3. 템플릿 저장 및 조회
   - 저장 위치: `skills/templates/`
   - 현재 금감원 후보: `fss_director_report/`, `fss_virtual_asset_report/`
   - 조회: `core/templates/registry.py`
   - 자동 생성물은 후보로 유지하고, `status: approved`인 `template.json`만 로드한다.
4. 내용 및 표 채우기
   - 표 셀 어댑터: `core/adapters/hwpx_table_fill_adapter.py`
   - 참조 스킬: `skills/hwp-skill/scripts/fill_hwpx.py`
   - 검증: `tests/test_hwpx_table_fill_adapter.py`
   - `section`, `table`, `row`, `col`, `value` 계약을 유지하고 결과 HWPX를 검증한다.

`skills/hwp-skill/`은 참조 전용이므로 직접 수정하지 않는다. 필요한 동작은
`core/adapters/`의 edudoc 소유 어댑터에서 연결한다. 현재 범용 텍스트
플레이스홀더 렌더러는 연결되어 있지 않으므로 표 셀 채우기 기능을 전체 템플릿
렌더링 기능으로 과장하지 않는다.

초기 구상의 `core/templates/load.py`, `extract_style.py`, `extractor.py`는 현재
실제 파일명이 아니다. 대응 기능은 `registry.py`, `extractors/`, `pipeline.py`에
분리되어 있으므로 새 작업 전에 실제 구현을 확인한다.

## 고위험 행동 차단
- 배포, DB 변경, 외부 전송, 삭제처럼 되돌리기 어려운 행동은 먼저 확인을 받는다.
- 서버 접속정보 등 민감정보는 코드·설정·문서에 넣지 않고 `.env`/시크릿으로 분리한다.
- `exports/`, `samples/` 외 폴더의 대량 파일 생성·삭제는 사전 확인한다.
