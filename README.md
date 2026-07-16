# edudoc

edudoc은 **참조 자료를 기반으로 문서를 생성하는 작업 자동화 시스템**입니다.

이 프로젝트의 주목적은 파일 형식 변환이 아닙니다. edudoc이 지향하는 제품 흐름은 다음과 같습니다.

```text
원본 자료 및 참조 자료 + 사용자 의도
-> 작업 목적에 맞는 문서 생성
-> 문서 유형별 검증
-> 필요한 경우 DOCX / HWPX / PDF / PPTX 형식으로 최종 렌더링
```

HWPX, HWP, Markdown 형식의 정규화, 검증 보고서 및 내보내기 기능은 이러한 목표를 지원하는 보조 계층입니다.

## 현재 구현 상태

* HWPX를 기본 구조화 입력 형식으로 사용합니다.
* HWP는 레거시 문서 지원을 위한 호환 입력 경로로 유지합니다.
* Markdown 초안의 정규화와 내보내기를 지원합니다.
* 범용 `main.py run`과 공용 `Pipeline`은 문서 유형별 작성 검증을 실행하지
  않습니다. 입력 확장자와 대상 문서 프로필도 검증기를 선택하지 않습니다.
* 공문 생성기와 공문 규칙 검증기는 전용 호환 경로에 남아 있지만 현재 공용
  Pipeline의 활성 범위에는 포함되지 않습니다.
* DOCX는 현재 가장 안정적으로 구현된 최종 렌더링 형식이지만, 아직 레이아웃이 완벽하게 재현되지는 않습니다.
* PDF 내보내기는 대체 경로 또는 실험적 기능으로 제공됩니다.
* HWPX 내보내기는 실험적 기능입니다.

## 핵심 처리 계층

```text
원본 문서
-> 원본 자료 묶음 구성 및 필터링
-> 문서 내용 이해
-> 문서 생성 요청 구성
-> 문서 구조 설계
-> 문서 생성
-> 문서 검증
-> 템플릿 및 레이아웃 렌더링
-> 파일 내보내기
```

## 핵심 HWPX 템플릿 파이프라인

기본 프로젝트 경로는 `C:\Users\work\edudoc`입니다. HWP 원본에서 재사용 가능한
HWPX 템플릿을 만들고 내용을 채우는 현재 핵심 경로는 다음과 같습니다.

```text
HWP 원본
-> HWPX 변환
-> HWPX 패키지 분해 및 고정 서식/가변 내용 분리
-> skills/templates/에 템플릿 후보 저장 및 명시적 승인
-> 승인된 템플릿 조회
-> 내용 및 표 셀 채우기
-> HWPX 패키지 검증
```

### 1. HWP에서 HWPX로 변환

* 변환 엔진: `tools/hwp2hwpx-python-refactor/hwp2hwpx/`
* edudoc 어댑터: `core/adapters/hwpx_skill_adapter.py`
* 어댑터는 로컬 엔진을 사용하며 패키지 자동 설치나 저장소 자동 복제를 하지 않습니다.

### 2. HWPX 분해 및 템플릿 생성

* 패키지 추출: `core/templates/hwpx_package_extractor.py`
* 고정 서식과 가변 내용 분리: `core/templates/hwpx_content_separator.py`
* 실행 진입점: `scripts/templates/separate_hwpx_template_content.py`

생성 결과는 다음 구조를 사용합니다.

```text
skills/templates/<template-id>/
├─ template.json
├─ content.sample.json
├─ placeholder_map.json
├─ raw/
│  ├─ header.xml
│  └─ section0.xml
└─ template/
   ├─ header.xml
   └─ section0.template.xml
```

템플릿은 `skills/templates/<기관>/<문서 유형>/`에 저장합니다. 현재 저장된 금감원
계열 템플릿은 다음과 같습니다(모두 `approved`).

* 금감원 원장보고 (`fss_director_report`): `skills/templates/금융감독원/금감원 원장보고/`
* 금감원 원장보고 가상자산 이상거래 (`fss_virtual_asset_report`): `skills/templates/금융감독원/금감원 원장보고 가상자산/`
* 금감원 원페이지 (`fss_one_page`): `skills/templates/금융감독원/금감원 원페이지/`

자동 추출 결과는 후보입니다. `template.json`의 상태가 명시적으로 `approved`인
템플릿만 `core/templates/registry.py`의 `TemplateRegistry`가 로드합니다.

### 3. 템플릿 내용과 표 채우기

* HWPX 표 셀 채우기: `core/adapters/hwpx_table_fill_adapter.py`
* 참조 구현: `skills/hwp-skill/scripts/fill_hwpx.py`
* 검증: `tests/test_hwpx_table_fill_adapter.py`

어댑터는 `section`, `table`, `row`, `col`, `value` 좌표로 표 셀을 채운 뒤
HWPX 패키지 검증을 수행합니다. `section*.template.xml`의 일반 텍스트
플레이스홀더를 최종 HWPX에 렌더링하는 범용 경로는 아직 연결되어 있지 않습니다.

참고로 초기 구상에 있던 `core/templates/load.py`, `extract_style.py`,
`extractor.py`의 역할은 현재 각각 `registry.py`, `extractors/`, `pipeline.py`로
분리되어 있습니다.

자세한 내용은 다음 문서를 참고하십시오.

* `docs/product-direction.md`
* `docs/workflows.md`
* `docs/export-status.md`
* `docs/export-quality-criteria.md`

## 실행 방법

```bash
pip install -r requirements.txt
python main.py run samples/
python main.py watch
python tests/test_pipeline.py
python tests/test_hwpx_document_model.py
```

선택적으로 내보내기 형식을 지정할 수 있습니다.

```bash
python main.py run samples/ --export docx,pdf
```

범용 `main.py run`과 공용 `Pipeline`은 정규화 및 내보내기를 담당하며 문서
유형별 작성 validator를 선택하거나 실행하지 않습니다. HWPX 변환이
DocumentModel을 제공할 때는 별도의 무결성 검사만 수행합니다.

기본 작업 흐름에서는 LibreOffice, Microsoft Office, 한컴오피스, LaTeX, Pandoc 또는 Typst 설치를 요구하지 않아야 합니다.

용량이 크거나 별도의 설치가 필요한 실행 파일은 선택적 대체 수단 또는 결과 비교 도구로만 사용할 수 있습니다.

## 개발 환경 및 작업 지침

개발을 시작하기 전에 다음 문서를 먼저 확인하십시오.

* `AGENTS.md`
* `docs/HARNESS.md`
* `MEMORY.md`
* `CLAUDE.md`

프로젝트의 핵심 방향은 다음과 같습니다.

```text
HWPX는 기본 구조화 입력 형식입니다.
HWP는 레거시 문서 지원을 위한 호환 입력 형식입니다.
파일 내보내기는 최종 렌더링 단계이며, 프로젝트 자체의 목적이 아닙니다.
```

향후 개발 과정에서 바이너리 HWP 또는 특정 단일 내보내기 형식이 프로젝트의 기본 방향이라고 해석해서는 안 됩니다.
