# HWPX Template Extraction Report

- Input file: `금감원 원페이지.hwpx`
- Template ID: `fss_one_page`
- Template name: `금감원 원페이지`
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

### `section0.xml` — paragraphs: 60, tables: 8

- Table 1: rowCnt=`1`, colCnt=`1`
- Table 2: rowCnt=`1`, colCnt=`1`
- Table 3: rowCnt=`1`, colCnt=`3`
- Table 4: rowCnt=`1`, colCnt=`3`
- Table 5: rowCnt=`3`, colCnt=`3`
- Table 6: rowCnt=`1`, colCnt=`1`
- Table 7: rowCnt=`1`, colCnt=`1`
- Table 8: rowCnt=`1`, colCnt=`3`

#### Visible `<hp:t>` Text

1. `◆◆◆◆◆ 진행상황 및 대응방안`
2. `(◎◎◎◎◎◎국 ◇◇◇◇팀, ’26.7.9.)`
3. `Ⅰ.`
4. `◆◆◆◆◆ 진행상황`
5. `가`
6. `개요`
7. `□`
8. `(맑은고딕 15pt)`
9. `휴먼명조 15pt`
10. `◦휴먼명조 15pt`
11. `(휴먼명조 13pt)`
12. `나`
13. `진행상황`
14. `□`
15. `(맑은고딕 15pt)`
16. `휴먼명조 15pt`
17. `◦휴먼명조 15pt`
18. `(휴먼명조 13pt)`
19. `*맑은 고딕 12pt`
20. `†맑은 고딕 11pt`
21. `〈◈◈◈◈ 관련 현황〉`
22. `※ 맑은고딕 13pt`
23. `◦ 맑은고딕 13pt`
24. `* 맑은고딕 11pt`
25. `Ⅱ.`
26. `대응계획`
27. `󰊱`
28. `(맑은고딕 15pt)`
29. `휴먼명조 15pt`
30. `◦휴먼명조 15pt`
31. `(휴먼명조 13pt)`
32. `󰊲`
33. `(맑은고딕 15pt)`
34. `휴먼명조 15pt`
35. `◦휴먼명조 15pt`
36. `(휴먼명조 13pt)`
37. `⇨ 휴먼명조 15pt`
38. `참고`
39. `HY헤드라인M 15pt`

## Candidate Placeholders (Not Applied)

- `placeholder_symbol` · `(◎◎◎◎◎◎국 ◇◇◇◇팀, ’26.7.9.)` (section0.xml #1: 자리표시 기호 포함)
- `checkbox` · `□` (section0.xml #6: 체크박스 기호 포함)
- `report_title` · `대응계획` (section0.xml #25: 보고·계획 제목 가능성)

## Style Summary

- Source: `extracted_from_hwpx`
- Font family: `휴먼명조`
- Body size: `15.0`
- Line spacing: `160%`
- Page margins: `{'top': 8.0, 'bottom': 8.0, 'left': 20.0, 'right': 20.0}`
- Confidence: `high`
- Header font faces: `['맑은 고딕', '함초롬돋움', '함초롬바탕', '휴먼명조', 'HY견명조', 'HY헤드라인M', 'HCI Poppy', '한양신명조', '명조']`
- Header char properties: `38`
- Header paragraph properties: `29`

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
