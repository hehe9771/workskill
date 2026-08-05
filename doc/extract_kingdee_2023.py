# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pypdf import PdfReader

pdf_path = r"C:\Users\wuyan\.claude\projects\D--mydoc-workskill\34d7ab85-6f5f-4649-85ba-f8d91dd940b0\tool-results\webfetch-1783305699979-oh75zn.pdf"

reader = PdfReader(pdf_path)
print("TOTAL PAGES:", len(reader.pages))

# Extract all text
all_text = []
for i, page in enumerate(reader.pages):
    try:
        t = page.extract_text() or ""
    except Exception as e:
        t = f"[EXTRACT ERROR p{i}: {e}]"
    all_text.append(t)

full = "\n".join(all_text)
print("TOTAL CHARS:", len(full))

# Search for key terms
keywords = ["毛利率", "毛利", "gross profit", "gross margin", "大企业", "苍穹", "星瀚",
            "云服务收入", "云收入", "亏损", "净亏损", "净利", "9.81", "64.2", "80%"]

print("\n===== KEYWORD MATCHES =====")
for kw in keywords:
    idxs = []
    start = 0
    while True:
        pos = full.find(kw, start)
        if pos == -1:
            break
        idxs.append(pos)
        start = pos + 1
        if len(idxs) > 15:
            break
    print(f"\n--- '{kw}' : {len(idxs)} matches ---")
    for p in idxs[:6]:
        snippet = full[max(0,p-80):p+120].replace("\n", " ")
        print(f"  [pos {p}] ...{snippet}...")

# Save full text for inspection
with open(r"D:\mydoc\workskill\doc\kingdee_2023_ar_text.txt", "w", encoding="utf-8") as f:
    f.write(full)
print("\nFULL TEXT SAVED to doc/kingdee_2023_ar_text.txt")
