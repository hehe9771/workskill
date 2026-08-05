"""从 workflow 转录中提取所有 agent 的 StructuredOutput 结构化结果,分类汇总。
用于在 synthesis agent 失败(内容过滤)后,主线程直接基于数据综合报告。"""
import json, os, glob, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = r'C:/Users/wuyan/.claude/projects/D--mydoc-workskill/914cb53d-54b0-439b-bed0-15b11e0217c6/subagents/workflows/wf_07193a03-fed'
OUT = r'D:/mydoc/workskill/doc/dog_kb_extracted.json'


def extract_last_structured(path):
    """返回该 agent 最后一次 StructuredOutput 的 input,以及首条 user prompt 前 200 字(判断角色)。"""
    last_so = None
    first_prompt = ''
    with open(path, encoding='utf-8') as f:
        for line in f:
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get('type') == 'user' and not first_prompt:
                m = d.get('message') or {}
                content = m.get('content')
                if isinstance(content, str):
                    first_prompt = content[:200]
                elif isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get('type') == 'text':
                            first_prompt = c.get('text', '')[:200]
                            break
            if d.get('type') == 'assistant':
                m = d.get('message') or {}
                for c in (m.get('content') or []):
                    if isinstance(c, dict) and c.get('type') == 'tool_use' and c.get('name') == 'StructuredOutput':
                        inp = c.get('input') or {}
                        if isinstance(inp, dict):
                            last_so = inp
    return last_so, first_prompt


def classify(so):
    if not so:
        return 'none'
    if 'verdict' in so and 'is_real_dog_kb' in so:
        return 'verify'
    if 'is_real_dog_kb' in so and 'content_scope' in so:
        return 'deepdive'
    if 'candidates' in so:
        return 'search_or_gapfill'
    if 'gaps' in so:
        return 'critic'
    return 'other'


def main():
    files = sorted(glob.glob(os.path.join(BASE, 'agent-*.jsonl')))
    print(f'扫描 {len(files)} 个 agent 转录文件')
    buckets = {'search_or_gapfill': [], 'deepdive': [], 'verify': [], 'critic': [], 'other': [], 'none': []}
    for fp in files:
        so, prompt = extract_last_structured(fp)
        cat = classify(so)
        aid = os.path.basename(fp).replace('agent-', '').replace('.jsonl', '')
        rec = {'agent_id': aid, 'data': so, 'prompt_head': prompt}
        buckets[cat].append(rec)

    for cat, lst in buckets.items():
        print(f'  {cat}: {len(lst)}')

    # 去重合并 search/gapfill 候选
    seen = set()
    all_candidates = []
    for rec in buckets['search_or_gapfill']:
        for c in (rec['data'] or {}).get('candidates') or []:
            if not c or not c.get('url'):
                continue
            k = c['url'].lower().replace('https://', '').replace('http://', '').replace('www.', '').rstrip('/')
            k = k.replace('/refs/heads/', '/').replace('/head/', '/')
            if k in seen:
                continue
            seen.add(k)
            all_candidates.append(c)

    # deepdive 按 url 去重(取后出现的为准)
    dd_seen = set()
    deepdive = []
    for rec in buckets['deepdive']:
        d = rec['data']
        if not d or not d.get('url'):
            continue
        k = d['url'].lower().replace('https://', '').replace('http://', '').replace('www.', '').rstrip('/')
        if k in dd_seen:
            # 覆盖更新(后出现的可能是重试更完整的)
            for i, x in enumerate(deepdive):
                if x['url'].lower().rstrip('/').endswith(k.split('/')[-1]):
                    deepdive[i] = d
                    break
            continue
        dd_seen.add(k)
        deepdive.append(d)

    # verify 去重
    v_seen = set()
    verifies = []
    for rec in buckets['verify']:
        d = rec['data']
        if not d or not d.get('url'):
            continue
        k = d['url'].lower()
        if k in v_seen:
            continue
        v_seen.add(k)
        verifies.append(d)

    critic = [rec['data'] for rec in buckets['critic'] if rec['data']]

    result = {
        'counts': {cat: len(lst) for cat, lst in buckets.items()},
        'total_candidates_dedup': len(all_candidates),
        'total_deepdive_dedup': len(deepdive),
        'total_verify_dedup': len(verifies),
        'candidates': all_candidates,
        'deepdive': deepdive,
        'verifies': verifies,
        'critic': critic,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f'\n输出: {OUT}')
    print(f'去重候选 {len(all_candidates)} / 深采 {len(deepdive)} / 核验 {len(verifies)} / critic {len(critic)}')

    # 真 dog kb 统计
    real = [d for d in deepdive if d.get('is_real_dog_kb') in ('yes', 'partial')]
    print(f'真狗知识库(yes+partial): {len(real)}')
    by_sub = {}
    for d in real:
        s = d.get('subdomain') or 'unknown'
        by_sub[s] = by_sub.get(s, 0) + 1
    print('按子领域:', by_sub)


if __name__ == '__main__':
    main()
