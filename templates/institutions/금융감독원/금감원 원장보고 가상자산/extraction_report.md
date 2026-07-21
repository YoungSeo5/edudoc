# HWPX Template Extraction Report

- Input file: `금감원_원장보고_가상자산 관련 이상거래.hwpx`
- Template ID: `fss_virtual_asset_report`
- Template name: `금감원 원장보고 가상자산 이상거래`
- Status: `candidate`
- `Contents/header.xml`: `True`
- `Contents/content.hpf`: `True`
- `BinData/`: `False`

## Detected Internal HWPX Files

- `mimetype`
- `version.xml`
- `Contents/header.xml`
- `Contents/section0.xml`
- `Preview/PrvText.txt`
- `Scripts/headerScripts.js`
- `Scripts/sourceScripts.js`
- `settings.xml`
- `Preview/PrvImage.png`
- `META-INF/container.rdf`
- `Contents/content.hpf`
- `META-INF/container.xml`
- `META-INF/manifest.xml`

## Detected Sections

### `section0.xml` — paragraphs: 31, tables: 4

- Table 1: rowCnt=`2`, colCnt=`3`
- Table 2: rowCnt=`1`, colCnt=`1`
- Table 3: rowCnt=`1`, colCnt=`1`
- Table 4: rowCnt=`1`, colCnt=`3`

#### Visible `<hp:t>` Text

1. `현안(이슈)보고`
2. `(2026. 7. 9.)`
3. `가상자산 관련 이상거래 현황파악 진행현황`
4. `□ 현안검토 □ 언론보도 □ 국회 등 □ 금융위·증선위 ☑ 기타(현황파악)`
5. `☑ 요약 또는 배경`
6. `1. 추진 배경`
7. `□ 최근 가상자산 시장에서 통상적인 거래 패턴과 상이한 이상매매 정황이 다수 포착됨에 따라, 관련 동향을 파악하고 대응방안을 마련하고자 함`
8. `◦ 시장 모니터링시스템(FDS) 및 거래소 제보를 통해 특정 종목에서 단기간 거래량이 급증하는 사례가 다수 확인되었으며, 관련 계좌의 자금흐름을 점검 중`
9. `* 최근 1개월간 이상매매 의심 신고 : 000건(전월 대비 00% 증가)`
10. `† 세부 수치는 관계기관 확인 후 익일 중 업데이트 예정`
11. `⇨ 향후 조사 진행상황을 지속 모니터링하고, 이상거래 혐의가 확인될 경우 즉시 조사에 착수하여 결과를 보고할 예정`
12. `가상자산감독국`
13. `국장 김도윤(☎02-3145-5501)`
14. `팀장 박서연(☎02-3145-5502)`
15. `끝.`

## Candidate Placeholders (Not Applied)

- `report_title` · `현안(이슈)보고` (section0.xml #0: 보고·계획 제목 가능성)
- `date` · `(2026. 7. 9.)` (section0.xml #1: 날짜 형식)
- `common_report_section` · `가상자산 관련 이상거래 현황파악 진행현황` (section0.xml #2: 공통 보고서 섹션명)
- `checkbox` · `□ 현안검토 □ 언론보도 □ 국회 등 □ 금융위·증선위 ☑ 기타(현황파악)` (section0.xml #3: 체크박스 기호 포함)
- `checkbox` · `☑ 요약 또는 배경` (section0.xml #4: 체크박스 기호 포함)
- `common_report_section` · `☑ 요약 또는 배경` (section0.xml #4: 공통 보고서 섹션명)
- `common_report_section` · `1. 추진 배경` (section0.xml #5: 공통 보고서 섹션명)
- `checkbox` · `□ 최근 가상자산 시장에서 통상적인 거래 패턴과 상이한 이상매매 정황이 다수 포착됨에 따라, 관련 동향을 파악하고 대응방안을 마련하고자 함` (section0.xml #6: 체크박스 기호 포함)
- `department_name` · `가상자산감독국` (section0.xml #11: 부서·기관명 형태)
- `phone_number` · `국장 김도윤(☎02-3145-5501)` (section0.xml #12: 전화번호 형식)
- `phone_number` · `팀장 박서연(☎02-3145-5502)` (section0.xml #13: 전화번호 형식)

## Style Summary

- Source: `extracted_from_hwpx`
- Font family: `맑은 고딕`
- Body size: `11.0`
- Line spacing: `160%`
- Page margins: `{'top': 10.0, 'bottom': 10.0, 'left': 20.0, 'right': 20.0}`
- Confidence: `high`
- Header font faces: `['맑은 고딕', '함초롬돋움', '함초롬바탕', '휴먼명조', 'HY헤드라인M', 'HCI Poppy', '한양신명조', '명조']`
- Header char properties: `22`
- Header paragraph properties: `28`

## Rendering Preservation Rules

- `preserve_header_xml`: `True`
- `replace_only_hp_t_text`: `True`
- `preserve_table_structure`: `True`
- `preserve_linesegarray`: `False`
- `do_not_modify_style_ids`: `True`
- Source/template XML keeps extracted `linesegarray` caches.
- Rendering removes `linesegarray` caches from changed sections and retains them in unchanged sections.

## Fixture Comparison

- No external extracted fixture directory supplied.

## Unsupported or Unprocessed Entries

- `mimetype`
- `version.xml`
- `Preview/PrvText.txt`
- `Preview/PrvImage.png`

## Warnings and Parse Errors

- Unselected package entries were preserved only in the source HWPX and are listed in the report.
