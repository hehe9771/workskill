# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import fitz

pdf_path = r"C:\Users\wuyan\.claude\projects\D--mydoc-workskill\34d7ab85-6f5f-4649-85ba-f8d91dd940b0\tool-results\webfetch-1783305699979-oh75zn.pdf"
doc = fitz.open(pdf_path)
print("PAGES:", doc.page_count)

# Extract all text with PyMuPDF
full = ""
for i in range(doc.page_count):
    full += doc[i].get_text()
print("CHARS:", len(full))

# Save clean text
with open(r"D:\mydoc\workskill\doc\kingdee_2023_ar_clean.txt", "w", encoding="utf-8") as f:
    f.write(full)

# Search key terms (Chinese now readable)
kws = ["毛利率", "毛利", "大企业", "苍穹", "星瀚", "云服务收入", "9.81", "64.2", "净亏损",
       "净利", "云转型", "亏损", "40.9%", "48.7%", "ARR"]
print("\n===== CLEAN CJK KEYWORD MATCHES =====")
for kw in kws:
    idxs = []
    s = 0
    while True:
        p = full.find(kw, s)
        if p == -1: break
        idxs.append(p)
        s = p + 1
        if len(idxs) > 10: break
    print(f"\n--- '{kw}': {len(idxs)} matches ---")
    for p in idxs[:5]:
        sn = full[max(0,p-90):p+130].replace("\n"," ")
        print(f"  ...{sn}...")
