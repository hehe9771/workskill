# -*- coding: utf-8 -*-
"""提取 docx 正文结构（标题/段落/表格）为 markdown 文本，供后续改写使用。"""
import sys
from docx import Document
from docx.document import Document as _Doc
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

SRC = r"D:\mydoc\workskill\doc\金蝶灵基Lingee(灵基OS)及企业AI应用调研报告 - 副本.docx"
OUT = r"D:\mydoc\workskill\doc\_tmp_report_extract.md"

HEADING_MAP = {"Heading 1": "# ", "Heading 2": "## ", "Heading 3": "### ",
               "Heading 4": "#### ", "Title": "# "}


def iter_block_items(parent):
    """按文档顺序产出段落与表格。"""
    body = parent.element.body if isinstance(parent, _Doc) else parent
    for child in body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def md_table(table):
    lines = []
    rows = [[c.text.replace("\n", " ").strip() for c in row.cells] for row in table.rows]
    if not rows:
        return ""
    lines.append("| " + " | ".join(rows[0]) + " |")
    lines.append("|" + "|".join(["---"] * len(rows[0])) + "|")
    for r in rows[1:]:
        # 对齐列数
        if len(r) < len(rows[0]):
            r = r + [""] * (len(rows[0]) - len(r))
        lines.append("| " + " | ".join(r[:len(rows[0])]) + " |")
    return "\n".join(lines)


def main():
    doc = Document(SRC)
    out = []
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if not text:
                continue
            style = block.style.name if block.style else ""
            prefix = HEADING_MAP.get(style, "")
            if prefix:
                out.append("\n" + prefix + text + "\n")
            elif style.startswith("List") or "List" in style:
                out.append("- " + text)
            else:
                out.append(text + "\n")
        elif isinstance(block, Table):
            md = md_table(block)
            if md:
                out.append("\n" + md + "\n")
    content = "\n".join(out)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK chars={len(content)} lines={content.count(chr(10))}")


if __name__ == "__main__":
    main()
