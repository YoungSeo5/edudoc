"""
Markdown -> 공통 블록 구조 파서 (모든 pip-native exporter가 공유).

markdown-it-py로 Markdown을 한 번 파싱해, exporter들이 형식에 상관없이
그대로 쓸 수 있는 단순한 블록/런(run) 구조로 바꾼다.
지원 블록: 제목(heading), 문단(paragraph), 목록(list), 표(table).
인라인: 굵게(bold)/기울임(italic).

공문서 초안이 쓰는 구조(제목·항목 번호·붙임·표)를 담기에 충분한 최소 집합이다.
그 밖의 블록(인용문, 코드펜스, 수평선 등)은 이 단계에선 건너뛴다.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode


@dataclass
class Run:
    """인라인 텍스트 조각과 서식."""
    text: str
    bold: bool = False
    italic: bool = False


@dataclass
class Heading:
    level: int              # 1~6
    runs: list[Run] = field(default_factory=list)


@dataclass
class Paragraph:
    runs: list[Run] = field(default_factory=list)


@dataclass
class ListBlock:
    ordered: bool
    items: list[list[Run]] = field(default_factory=list)   # 항목마다 run 목록


@dataclass
class Table:
    header: list[list[Run]] = field(default_factory=list)          # 셀마다 run 목록
    rows: list[list[list[Run]]] = field(default_factory=list)      # 행 -> 셀 -> run 목록


Block = Heading | Paragraph | ListBlock | Table


def parse_markdown(text: str) -> list[Block]:
    """Markdown 문자열을 블록 목록으로 변환한다."""
    md = MarkdownIt("commonmark").enable("table")
    tree = SyntaxTreeNode(md.parse(text))

    blocks: list[Block] = []
    for node in tree.children:
        if node.type == "heading":
            blocks.append(Heading(level=int(node.tag[1]), runs=_inline_runs(node)))
        elif node.type == "paragraph":
            blocks.append(Paragraph(runs=_inline_runs(node)))
        elif node.type in ("bullet_list", "ordered_list"):
            blocks.append(_parse_list(node))
        elif node.type == "table":
            blocks.append(_parse_table(node))
        # 그 외 블록은 이 단계에선 무시
    return blocks


def _inline_runs(node: SyntaxTreeNode) -> list[Run]:
    """heading/paragraph/th/td 등 'inline' 자식을 가진 노드에서 run 목록을 뽑는다."""
    for child in node.children:
        if child.type == "inline":
            return _runs(child)
    return []


def _runs(node: SyntaxTreeNode, bold: bool = False, italic: bool = False) -> list[Run]:
    out: list[Run] = []
    for ch in node.children:
        if ch.type == "text":
            if ch.content:
                out.append(Run(ch.content, bold, italic))
        elif ch.type == "code_inline":
            if ch.content:
                out.append(Run(ch.content, bold, italic))
        elif ch.type == "strong":
            out.extend(_runs(ch, True, italic))
        elif ch.type == "em":
            out.extend(_runs(ch, bold, True))
        elif ch.type in ("softbreak", "hardbreak"):
            out.append(Run(" ", bold, italic))
        else:
            # 링크 등 중첩 노드는 텍스트만 평탄화
            out.extend(_runs(ch, bold, italic))
    return out


def _parse_list(node: SyntaxTreeNode) -> ListBlock:
    items: list[list[Run]] = []
    for li in node.children:            # list_item
        runs: list[Run] = []
        for ch in li.children:          # 보통 paragraph 하나
            if ch.type == "paragraph":
                runs.extend(_inline_runs(ch))
        items.append(runs)
    return ListBlock(ordered=(node.type == "ordered_list"), items=items)


def _parse_table(node: SyntaxTreeNode) -> Table:
    header: list[list[Run]] = []
    rows: list[list[list[Run]]] = []
    for section in node.children:       # thead / tbody
        if section.type == "thead":
            for tr in section.children:
                header = [_inline_runs(cell) for cell in tr.children]
        elif section.type == "tbody":
            for tr in section.children:
                rows.append([_inline_runs(cell) for cell in tr.children])
    return Table(header=header, rows=rows)
