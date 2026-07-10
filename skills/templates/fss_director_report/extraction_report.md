# HWPX Template Extraction Report

- Input file: `금감원 원장보고.hwpx`
- Template ID: `fss_director_report`
- Template name: `금감원 원장보고`
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

### `section0.xml` — paragraphs: 32, tables: 4

- Table 1: rowCnt=`2`, colCnt=`3`
- Table 2: rowCnt=`1`, colCnt=`1`
- Table 3: rowCnt=`1`, colCnt=`1`
- Table 4: rowCnt=`1`, colCnt=`3`

#### Visible `<hp:t>` Text

1. `현안(이슈)보고`
2. `(2026. 7. 9.)`
3. `◎◎◎◎ 진행현황`
4. `□ 현안검토 □ 언론보도 □ 국회 등 □ 금융위·증선위 ☑ 기타(현황파악)`
5. `☑ 요약 또는 배경`
6. `1. 추진 배경(HY헤드라인M 16)`
7. `□ 본문 (휴먼명조 15, 장평 100%, 줄간격 150)`
8. `◦ 본문 (한칸 들여쓰기)`
9. `* 세부통계 등 (맑은 고딕 12, 장평 100%, 줄간격 130)`
10. `† 맑은고딕 11pt`
11. `⇨`
12. `○○○○○○국`
13. `국장 ○○○(☎1111)`
14. `팀장 ☆☆☆(☎2222)`
15. `※ 1페이지 하단에 보고자 및 연락처 등 표시`

## Candidate Placeholders (Not Applied)

- `report_title` · `현안(이슈)보고` (section0.xml #0: 보고·계획 제목 가능성)
- `date` · `(2026. 7. 9.)` (section0.xml #1: 날짜 형식)
- `placeholder_symbol` · `◎◎◎◎ 진행현황` (section0.xml #2: 자리표시 기호 포함)
- `common_report_section` · `◎◎◎◎ 진행현황` (section0.xml #2: 공통 보고서 섹션명)
- `checkbox` · `□ 현안검토 □ 언론보도 □ 국회 등 □ 금융위·증선위 ☑ 기타(현황파악)` (section0.xml #3: 체크박스 기호 포함)
- `checkbox` · `☑ 요약 또는 배경` (section0.xml #4: 체크박스 기호 포함)
- `common_report_section` · `☑ 요약 또는 배경` (section0.xml #4: 공통 보고서 섹션명)
- `common_report_section` · `1. 추진 배경(HY헤드라인M 16)` (section0.xml #5: 공통 보고서 섹션명)
- `checkbox` · `□ 본문 (휴먼명조 15, 장평 100%, 줄간격 150)` (section0.xml #6: 체크박스 기호 포함)
- `placeholder_symbol` · `○○○○○○국` (section0.xml #11: 자리표시 기호 포함)
- `phone_number` · `국장 ○○○(☎1111)` (section0.xml #12: 전화번호 형식)
- `placeholder_symbol` · `국장 ○○○(☎1111)` (section0.xml #12: 자리표시 기호 포함)
- `phone_number` · `팀장 ☆☆☆(☎2222)` (section0.xml #13: 전화번호 형식)
- `placeholder_symbol` · `팀장 ☆☆☆(☎2222)` (section0.xml #13: 자리표시 기호 포함)

## Style Summary

- Source: `extracted_from_hwpx`
- Font family: `맑은 고딕`
- Body size: `15.0`
- Line spacing: `160%`
- Page margins: `{'top': 10.0, 'bottom': 10.0, 'left': 20.0, 'right': 20.0}`
- Confidence: `high`
- Header font faces: `['맑은 고딕', '함초롬돋움', '함초롬바탕', 'HY헤드라인M', '휴먼명조', 'HCI Poppy', '한양신명조', '명조']`
- Header char properties: `22`
- Header paragraph properties: `28`

## Rendering Preservation Rules

- `preserve_header_xml`: `True`
- `replace_only_hp_t_text`: `True`
- `preserve_table_structure`: `True`
- `preserve_linesegarray`: `True`
- `do_not_modify_style_ids`: `True`

## Fixture Comparison

- No external extracted fixture directory supplied.

## Unsupported or Unprocessed Entries

- `mimetype`
- `version.xml`
- `Preview/PrvText.txt`
- `Preview/PrvImage.png`

## Warnings and Parse Errors

- Unselected package entries were preserved only in the source HWPX and are listed in the report.
