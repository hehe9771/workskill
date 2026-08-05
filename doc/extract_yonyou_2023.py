# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import fitz

pdf_path = r"C:\Users\wuyan\.claude\projects\D--mydoc-workskill\34d7ab85-6f5f-4649-85ba-f8d91dd940b0\tool-results\webfetch-1783306241107-kcsrdh.pdf"
doc = fitz.open(pdf_path)
print("PAGES:", doc.page_count)
full = "".join(doc[i].get_text() for i in range(doc.page_count))
print("CHARS:", len(full))
with open(r"D:\mydoc\workskill\doc\yonyou_2023_ar_clean.txt", "w", encoding="utf-8") as f:
    f.write(full)

kws = ["大型企业", "中型企业", "小微企业", "云服务业务收入", "云服务收入", "65.2", "65.27",
       "6527", "6,527", "652,7", "分客户类型", "分行业", "主营业务", "云平台",
       "BIP", "总收入", "营业收入"]
print("\n===== KEYWORD MATCHES =====")
for kw in kws:
    idxs = []; s = 0
    while True:
        p = full.find(kw, s)
        if p == -1: break
        idxs.append(p); s = p + 1
        if len(idxs) > 15: break
    print(f"\n--- '{kw}': {len(idxs)} matches ---")
    for p in idxs[:6]:
        sn = full[max(0,p-90):p+160].replace("\n"," ")
        print(f"  ...{sn}...")
