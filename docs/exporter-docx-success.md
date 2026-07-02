# DOCX Exporter 성공 기준

`core/exporters/docx_exporter.py` (Markdown -> DOCX, python-docx) 의 검증 기준.
`tests/test_docx_exporter.py` 가 이 항목들을 코드로 확인한다.
새 exporter(pdf/hwpx/pptx)를 루프로 팬아웃할 때 이 문서를 템플릿으로 복제한다.

## 필수 (테스트가 강제)

1. **파일 생성**: 출력 `.docx` 가 존재하고 크기가 0보다 크며, 유효한 docx(zip, 매직 `PK`)다.
2. **제목 보존**: Markdown 제목(`#`, `##`)이 `Heading N` 스타일 문단으로 남는다.
3. **목록 보존**: 순서 목록/불릿 목록이 각각 `List Number`/`List Bullet` 스타일로 남고 항목 수가 일치한다.
4. **표 보존**: Markdown 표가 DOCX 표로 남고 행/열 수와 셀 텍스트가 일치한다.
5. **서식 보존**: `**굵게**`/`*기울임*` 이 해당 run 의 bold/italic 으로 남는다.
6. **한글 무결**: 한글 텍스트가 손상 없이 그대로 들어간다(왕복 텍스트 일치).

## 권장 (품질)

- Normal 스타일에 한글 폰트(기본 `Malgun Gothic`)를 지정해 한글이 정상 렌더된다.
- 표는 `Table Grid` 스타일로 테두리가 보인다.

## 비목표 (이 단계에서 다루지 않음)

- 병합 셀(colspan/rowspan), 이미지, 각주, 페이지 레이아웃 정밀 제어.
- 복잡한 원본 폼 문서의 고충실도 재현 — 필요 시 Pandoc/typst fallback 사용.
