# -*- coding: utf-8 -*-
"""独立校验三份改写产物：正文 AI 味词残留、破折号、关键事实保留情况。"""
import re

FILES = {
    "avoid-ai-writing": r"D:\mydoc\workskill\doc\金蝶灵基Lingee调研报告-avoid-ai-writing版.md",
    "stop-slop": r"D:\mydoc\workskill\doc\金蝶灵基Lingee调研报告-stop-slop版.md",
    "humanize": r"D:\mydoc\workskill\doc\金蝶灵基Lingee调研报告-humanize版.md",
}

AI_WORDS = ["赋能", "闭环", "底座", "抓手", "对齐", "颗粒度", "沉淀", "拉通", "链路",
            "打通", "全域", "全链路", "护城河", "底层逻辑", "弯道超车", "至关重要",
            "真正意义上", "全方位", "极强", "综上所述", "拭目以待", "未来可期", "前景广阔"]

FACTS = ["glm-5.2", "MCP", "CLI", "L1", "L6", "Token", "EAS V8.5", "总账", "合并报表",
         "电子档案", "2027", "70%", "trea", "workbuddy", "本体数据库", "苍穹", "沙箱"]

for name, path in FILES.items():
    with open(path, encoding="utf-8") as f:
        text = f.read()
    body = re.split(r"^##\s*附录", text, maxsplit=1, flags=re.M)[0]
    chars = len(re.sub(r"\s", "", body))
    hits = {w: body.count(w) for w in AI_WORDS if w in body}
    dashes = body.count("——") + body.count("—")
    missing = [fct for fct in FACTS if fct not in body]
    print(f"=== {name} ===")
    print(f"正文字符数(不含空白): {chars}")
    print(f"正文 AI 味词残留: {hits if hits else '无'}")
    print(f"正文破折号(—/——)数: {dashes}")
    print(f"关键事实缺失: {missing if missing else '无'}")
    print()
