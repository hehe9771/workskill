"""将提取的结构化数据生成干净的 UTF-8 摘要 markdown,供主线程基于此写最终报告。"""
import json, io

SRC = r'D:/mydoc/workskill/doc/dog_kb_extracted.json'
OUT = r'D:/mydoc/workskill/doc/dog_kb_summary.md'

d = json.load(open(SRC, encoding='utf-8'))
deepdive = d['deepdive']
verifies = d['verifies']

# verify 按 url 索引
vmap = {}
for v in verifies:
    k = (v.get('url') or '').lower().rstrip('/')
    vmap.setdefault(k, []).append(v)

real = [x for x in deepdive if x.get('is_real_dog_kb') in ('yes', 'partial')]
notdog = [x for x in deepdive if x.get('is_real_dog_kb') == 'no']
unc = [x for x in deepdive if x.get('is_real_dog_kb') == 'uncertain']

# 核验统计
v_stat = {'confirmed': 0, 'refuted': 0, 'uncertain': 0}
for v in verifies:
    t = (v.get('verdict') or '').lower()
    if t in v_stat:
        v_stat[t] += 1

refuted = [v for v in verifies if (v.get('verdict') or '').lower() == 'refuted']

# 类型分组
def tgroup(items):
    g = {}
    for x in items:
        t = (x.get('type') or 'unknown').split('(')[0].strip().lower()
        g.setdefault(t, []).append(x)
    return g

lines = []
lines.append('# 狗知识库开源项目调研 - 数据摘要\n')
lines.append(f'（从 workflow 转录提取，synthesis agent 失败后主线程综合用）\n')
lines.append(f'- 深采项目总数(去重): {len(deepdive)}')
lines.append(f'- 真 dog kb (yes+partial): {len(real)}')
lines.append(f'- 非 dog kb (no): {len(notdog)}')
lines.append(f'- 不确定 (uncertain): {len(unc)}')
lines.append(f'- 核验总数(去重): {len(verifies)}  -> confirmed={v_stat["confirmed"]} / refuted={v_stat["refuted"]} / uncertain={v_stat["uncertain"]}')
lines.append('')

# 按 is_real 程度排：yes 优先
real_yes = [x for x in real if x.get('is_real_dog_kb') == 'yes']
real_par = [x for x in real if x.get('is_real_dog_kb') == 'partial']

lines.append('## 一、真狗知识库 — is_real=yes（专题狗知识库/数据集/工具）\n')
lines.append(f'共 {len(real_yes)} 个\n')
g = tgroup(real_yes)
for t in sorted(g.keys(), key=lambda k: -len(g[k])):
    lines.append(f'\n### 类型: {t} ({len(g[t])})\n')
    lines.append('| 名称 | URL | 子领域 | license | 活跃度 | star | 最后更新 | 核验 |')
    lines.append('|---|---|---|---|---|---|---|---|')
    for x in g[t]:
        name = (x.get('name') or '')[:45]
        url = x.get('url') or ''
        sub = (x.get('subdomain') or '')[:35]
        lic = (x.get('license') or '')[:25]
        act = (x.get('activity') or '')[:15]
        star = (x.get('star') or '')[:15]
        upd = (x.get('last_update') or '')[:12]
        k = url.lower().rstrip('/')
        vs = vmap.get(k, [])
        vstr = ','.join(set([(v.get('verdict') or '') for v in vs])) if vs else '-'
        lines.append(f'| {name} | {url} | {sub} | {lic} | {act} | {star} | {upd} | {vstr} |')

lines.append(f'\n## 二、部分相关狗知识库 — is_real=partial（含狗的通用/边缘项目）\n')
lines.append(f'共 {len(real_par)} 个\n')
g = tgroup(real_par)
for t in sorted(g.keys(), key=lambda k: -len(g[k])):
    lines.append(f'\n### 类型: {t} ({len(g[t])})\n')
    lines.append('| 名称 | URL | 子领域 | license | 活跃度 | star | 核验 |')
    lines.append('|---|---|---|---|---|---|---|')
    for x in g[t]:
        name = (x.get('name') or '')[:45]
        url = x.get('url') or ''
        sub = (x.get('subdomain') or '')[:35]
        lic = (x.get('license') or '')[:25]
        act = (x.get('activity') or '')[:15]
        star = (x.get('star') or '')[:15]
        k = url.lower().rstrip('/')
        vs = vmap.get(k, [])
        vstr = ','.join(set([(v.get('verdict') or '') for v in vs])) if vs else '-'
        lines.append(f'| {name} | {url} | {sub} | {lic} | {act} | {star} | {vstr} |')

lines.append(f'\n## 三、证伪项目（核验 verdict=refuted）\n')
lines.append(f'共 {len(refuted)} 个\n')
if refuted:
    lines.append('| 名称 | URL | 核验结论 | is_real | 证据 |')
    lines.append('|---|---|---|---|---|')
    for v in refuted:
        name = (v.get('name') or '')[:40]
        url = v.get('url') or ''
        findings = (v.get('findings') or '')[:120].replace('|', '/')
        lines.append(f'| {name} | {url} | {v.get("verdict")} | {v.get("is_real_dog_kb")} | {findings} |')
else:
    lines.append('（无证伪）')

lines.append('\n## 四、核验全部明细（confirmed/refuted/uncertain）\n')
lines.append(f'共 {len(verifies)} 个\n')
lines.append('| 名称 | URL | verdict | is_real | 证据摘要 |')
lines.append('|---|---|---|---|---|')
for v in verifies:
    name = (v.get('name') or '')[:40]
    url = v.get('url') or ''
    findings = (v.get('findings') or '')[:100].replace('|', '/')
    lines.append(f'| {name} | {url} | {v.get("verdict")} | {v.get("is_real_dog_kb")} | {findings} |')

# 详细 content_scope 清单（用于报告分组详解）
lines.append('\n## 五、真狗知识库内容范围详情（content_scope 全文）\n')
for x in real_yes + real_par:
    lines.append(f'\n### {x.get("name","")} \n- URL: {x.get("url","")}')
    lines.append(f'- 类型: {x.get("type","")} | 子领域: {x.get("subdomain","")} | is_real: {x.get("is_real_dog_kb","")}')
    lines.append(f'- license: {x.get("license","")} | 活跃: {x.get("activity","")} | star: {x.get("star","")} | 更新: {x.get("last_update","")}')
    cs = x.get('content_scope') or ''
    if cs:
        lines.append(f'- 内容范围: {cs}')
    if x.get('notes'):
        lines.append(f'- 备注: {(x.get("notes") or "")[:300]}')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'写入 {OUT}')
print(f'真dog kb: {len(real)} (yes={len(real_yes)}, partial={len(real_par)})')
print(f'核验: {len(verifies)} (confirmed={v_stat["confirmed"]}, refuted={v_stat["refuted"]}, uncertain={v_stat["uncertain"]})')
print(f'证伪: {len(refuted)}')
