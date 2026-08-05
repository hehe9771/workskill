# -*- coding: utf-8 -*-
"""提取金蝶港股年报/董事名单/业绩新闻稿 PDF 文本，定位关键章节。"""
import os
import sys
import fitz  # pymupdf

TOOL_DIR = r"C:\Users\wuyan\.claude\projects\D--mydoc-workskill\34d7ab85-6f5f-4649-85ba-f8d91dd940b0\tool-results"

PDFS = {
    "annual_report_2025": os.path.join(TOOL_DIR, "webfetch-1783306824540-lbp1l4.pdf"),
    "directors_list": os.path.join(TOOL_DIR, "webfetch-1783306879455-fsrd6n.pdf"),
    "fy25_press_release": os.path.join(TOOL_DIR, "webfetch-1783306882280-10cjbq.pdf"),
}

KEYWORDS = ["董事", "管理层", "分部", "员工", "薪酬", "AI EBC", "苍穹",
            "产品管理", "研发中心", "首席", "总裁", "总经理", "EBC"]

OUT_DIR = r"D:\mydoc\workskill\code\hkex-ar-extract\out"
os.makedirs(OUT_DIR, exist_ok=True)


def extract(name, path):
    if not os.path.exists(path):
        print(f"[{name}] FILE NOT FOUND: {path}")
        return ""
    doc = fitz.open(path)
    n = doc.page_count
    print(f"\n===== {name} | pages={n} | {os.path.getsize(path)} bytes =====")
    full_text = []
    for i in range(n):
        t = doc.load_page(i).get_text("text")
        full_text.append(f"\n----- PAGE {i+1} -----\n{t}")
    doc.close()
    text = "".join(full_text)
    out_path = os.path.join(OUT_DIR, f"{name}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"saved -> {out_path} | chars={len(text)}")
    # 关键词命中（带页码上下文）
    pages = text.split("\n----- PAGE ")
    for kw in KEYWORDS:
        hits = []
        for idx, pg in enumerate(pages, start=1):
            if kw in pg:
                # 取命中行
                for line in pg.split("\n"):
                    if kw in line:
                        hits.append(f"p{idx}: {line.strip()[:120]}")
        if hits:
            print(f"[{kw}] {len(hits)} hits")
            for h in hits[:8]:
                print(f"   {h}")
    return text


def main():
    for name, path in PDFS.items():
        extract(name, path)


if __name__ == "__main__":
    main()
