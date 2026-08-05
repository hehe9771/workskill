# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import fitz

pdf_path = r"C:\Users\wuyan\.claude\projects\D--mydoc-workskill\34d7ab85-6f5f-4649-85ba-f8d91dd940b0\tool-results\webfetch-1783306039631-pts1vq.pdf"
doc = fitz.open(pdf_path)
print("PAGES:", doc.page_count)
full = "".join(doc[i].get_text() for i in range(doc.page_count))
print("CHARS:", len(full))
with open(r"D:\mydoc\workskill\doc\kingdee_2020_ar_clean.txt", "w", encoding="utf-8") as f:
    f.write(full)

kws = ["毛利率", "毛利", "五 年", "五年", "淨利潤", "淨虧損", "本公司擁有人應佔",
       "80%", "79%", "78%", "盈利", "虧損", "2017", "2018", "2019", "二零一七",
       "二零一八", "二零一九", "約80", "雲轉型", "雲服務"]
print("\n===== KEYWORD MATCHES =====")
for kw in kws:
    idxs = []; s = 0
    while True:
        p = full.find(kw, s)
        if p == -1: break
        idxs.append(p); s = p + 1
        if len(idxs) > 12: break
    print(f"\n--- '{kw}': {len(idxs)} matches ---")
    for p in idxs[:5]:
        sn = full[max(0,p-100):p+150].replace("\n"," ")
        print(f"  ...{sn}...")
