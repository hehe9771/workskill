export const meta = {
  name: 'pet-behavior-kb-research',
  description: '多 agent 从 GitHub 搜索宠物行为知识库/文档并对抗核验对比',
  phases: [
    { title: 'Search', detail: '5 个并行 agent 多策略搜索 GitHub（API + WebFetch）' },
    { title: 'DeepDive', detail: '对去重后候选逐个 WebFetch 抓 README 判定是否知识库' },
    { title: 'Verify', detail: '对判定为知识库的项目独立对抗核验真实性与相关性' },
  ],
}

// ---------- schemas ----------
const SEARCH_SCHEMA = {
  type: 'object',
  properties: {
    candidates: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          name: { type: 'string', description: 'owner/repo 形式' },
          url: { type: 'string', description: 'https://github.com/owner/repo' },
          description: { type: 'string' },
          stars: { type: 'number' },
          language: { type: 'string' },
          updated: { type: 'string', description: '最后更新时间 ISO 或文本' },
          why_relevant: { type: 'string', description: '为何与宠物行为相关' },
        },
        required: ['name', 'url', 'why_relevant'],
      },
    },
    sources_fetched: {
      type: 'array',
      description: '必须列出本次真实调用的所有 URL 及状态，防伪装执行',
      items: {
        type: 'object',
        properties: {
          url: { type: 'string' },
          fetch_status: { type: 'string', enum: ['success', 'failed'] },
          notes: { type: 'string' },
        },
        required: ['url', 'fetch_status'],
      },
    },
    search_strategy_used: { type: 'string' },
  },
  required: ['candidates', 'sources_fetched', 'search_strategy_used'],
}

const DEEP_SCHEMA = {
  type: 'object',
  properties: {
    name: { type: 'string' },
    url: { type: 'string' },
    fetch_ok: { type: 'boolean', description: 'repo 主页/README 是否真实可访问' },
    is_pet_behavior_kb: { type: 'boolean', description: '是否为宠物/动物行为知识库或文档（非纯 app/工具）' },
    content_scope: { type: 'string', description: '内容覆盖范围（哪些物种、哪些行为主题）' },
    data_format: { type: 'string', description: 'markdown/json/wiki/pdf/csv 等' },
    stars: { type: 'number' },
    license: { type: 'string' },
    last_updated: { type: 'string' },
    activity_level: { type: 'string', enum: ['active', 'maintained', 'stale', 'archived', 'unknown'] },
    strengths: { type: 'string' },
    weaknesses: { type: 'string' },
    sources_fetched: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          url: { type: 'string' },
          fetch_status: { type: 'string', enum: ['success', 'failed'] },
        },
        required: ['url', 'fetch_status'],
      },
    },
  },
  required: ['name', 'url', 'fetch_ok', 'is_pet_behavior_kb', 'content_scope', 'sources_fetched'],
}

const VERIFY_SCHEMA = {
  type: 'object',
  properties: {
    name: { type: 'string' },
    url: { type: 'string' },
    exists: { type: 'boolean', description: 'URL 真实可访问、非 404' },
    pet_behavior_confirmed: { type: 'boolean' },
    knowledge_base_confirmed: { type: 'boolean', description: '确认是知识库/文档而非纯工具' },
    refutation_attempt: { type: 'string', description: '尝试推翻论断的过程' },
    verdict: { type: 'string', enum: ['confirmed', 'refuted', 'uncertain'] },
    sources_fetched: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          url: { type: 'string' },
          fetch_status: { type: 'string', enum: ['success', 'failed'] },
        },
        required: ['url', 'fetch_status'],
      },
    },
  },
  required: ['name', 'url', 'exists', 'verdict', 'sources_fetched'],
}

// ---------- search tasks ----------
const SEARCH_TASKS = [
  {
    label: 'search:api-pet-behavior',
    prompt: `你是 GitHub 调研 agent。任务：用 GitHub Search API（REST，未认证）搜索"宠物行为"相关英文仓库。

执行步骤（必须真实调用，禁止凭记忆编造）：
1. 用 Bash 工具执行 curl 调用 GitHub Search API：
   curl -s -H "Accept: application/vnd.github+json" -H "User-Agent: pet-research-agent" "https://api.github.com/search/repositories?q=pet+behavior&sort=stars&order=desc&per_page=10"
   （Windows Git Bash 自带 curl；若 curl 不可用，改用 PowerShell：Invoke-RestMethod -Uri "https://api.github.com/search/repositories?q=pet+behavior&sort=stars&order=desc&per_page=10" -Headers @{Accept='application/vnd.github+json'; 'User-Agent'='pet-research-agent'}）
2. 解析返回 JSON 的 items 数组，提取每个仓库的 full_name、html_url、description、stargazers_count、language、updated_at、license.spdx_id、archived
3. 若 API 限速（403/429），在 sources_fetched 标 failed 并减少 candidates，禁止编造

返回 candidates（最多 8 个）+ sources_fetched（含本次 API URL 与 fetch_status）+ search_strategy_used。
每个 candidate 的 why_relevant 写一句为何与宠物行为相关。`,
  },
  {
    label: 'search:api-dog-cat-behavior',
    prompt: `你是 GitHub 调研 agent。任务：用 GitHub Search API 搜索犬猫行为相关仓库。

执行步骤（必须真实调用）：
1. Bash curl 调用：
   curl -s -H "Accept: application/vnd.github+json" -H "User-Agent: pet-research-agent" "https://api.github.com/search/repositories?q=dog+behavior+OR+canine+behavior+OR+cat+behavior+OR+feline+behavior&sort=stars&order=desc&per_page=10"
   （或 PowerShell Invoke-RestMethod 等效命令）
2. 解析 items，提取 full_name/html_url/description/stargazers_count/language/updated_at
3. 优先选与"行为知识/训练数据/行为学文档"相关的，排除纯商业 app

返回 candidates（最多 8）+ sources_fetched（含 API URL 与状态）+ search_strategy_used。禁止编造。`,
  },
  {
    label: 'search:api-training-dataset',
    prompt: `你是 GitHub 调研 agent。任务：用 GitHub Search API 搜索宠物训练/行为数据集与知识库类仓库（含中文关键词）。

执行步骤（必须真实调用）：
1. Bash curl 调用（中文需 URL 编码）：
   curl -s -H "Accept: application/vnd.github+json" -H "User-Agent: pet-research-agent" "https://api.github.com/search/repositories?q=animal+behavior+dataset+OR+pet+training+knowledge+OR+%E5%AE%A0%E7%89%A9%E8%A1%8C%E4%B8%BA+OR+%E7%8A%AC%E8%A1%8C%E4%B8%BA&sort=stars&order=desc&per_page=10"
   （PowerShell 等效：Invoke-RestMethod -Uri 'https://api.github.com/search/repositories?q=animal+behavior+dataset+OR+pet+training+knowledge+OR+宠物行为+OR+犬行为&sort=stars&order=desc&per_page=10' -Headers @{Accept='application/vnd.github+json'; 'User-Agent'='pet-research-agent'}）
2. 解析 items 提取字段
3. 侧重知识库/数据集/文档类仓库

返回 candidates（最多 8）+ sources_fetched + search_strategy_used。禁止编造。`,
  },
  {
    label: 'search:webfetch-topics-awesome',
    prompt: `你是 GitHub 调研 agent。任务：用 WebFetch 抓取 GitHub topic 页面与 awesome 列表，发现宠物/动物行为知识库类仓库（WebFetch 不耗 API 配额）。

执行步骤（必须真实调用 WebFetch，禁止编造）：
1. WebFetch 抓 https://github.com/topics/animal-behavior —— prompt: "List all repository names (owner/repo), their URLs, descriptions, and star counts shown on this topic page."
2. WebFetch 抓 https://github.com/topics/pet —— prompt: "List repository names, URLs, descriptions, stars related to pet behavior, training, or knowledge bases."
3. WebFetch 抓 https://github.com/topics/dog-training —— 同样 prompt
4. 若某 topic 页 404 或重定向，在 sources_fetched 标 failed，继续下一个

返回 candidates（最多 8，每个带 name/url/description/stars/why_relevant）+ sources_fetched（每个 WebFetch URL 带 fetch_status）+ search_strategy_used。`,
  },
  {
    label: 'search:webfetch-ddg-wiki',
    prompt: `你是 GitHub 调研 agent。任务：用 WebFetch 打 DuckDuckGo HTML 搜索 + 抓 GitHub wiki/awesome 列表，补充发现 star 不高但内容优质的宠物行为知识库（WebFetch 不耗 API 配额）。

执行步骤（必须真实调用，禁止编造）：
1. WebFetch 抓 https://html.duckduckgo.com/html/?q=github+pet+behavior+knowledge+base+repository —— prompt: "List all search result titles and their URLs (only github.com URLs). Format: Title - URL"
2. WebFetch 抓 https://html.duckduckgo.com/html/?q=github+animal+behavior+wiki+or+awesome+list —— 同样 prompt
3. 对结果里 2-3 个最相关的 github.com URL，逐个 WebFetch 抓取 repo 主页，确认是否知识库/文档
4. 403/失败如实标 failed 丢弃，不编造

返回 candidates（最多 8，每个带 name/url/description/stars/why_relevant）+ sources_fetched（每条带 fetch_status）+ search_strategy_used。`,
  },
]

// ---------- helpers ----------
function deepDivePrompt(c) {
  return `你是 GitHub 深度调研 agent。对单个项目做深度调研，判定其是否为"宠物行为知识库/文档"。

项目：${c.name}
URL：${c.url}
搜索阶段描述：${c.description || '(无)'}
搜索阶段 star：${c.stars ?? '(未知)'}

执行步骤（必须真实 WebFetch，禁止凭记忆编造）：
1. WebFetch 抓 ${c.url} —— prompt: "Summarize this GitHub repo: What is it about? Is it a knowledge base / documentation / dataset about pet or animal behavior? What species and behavior topics does it cover? What format (markdown/json/wiki/pdf)? Stars, license, last commit date, activity level. Quote README headings if any."
2. 若 README 仅在 repo 页摘要，额外 WebFetch 抓 ${c.url}/blob/main/README.md 或 ${c.url}/blob/master/README.md（先试 main 再试 master），任一成功即可
3. 若 404/重定向/私有，fetch_ok=false，is_pet_behavior_kb=false，如实标注

判定标准：is_pet_behavior_kb=true 当且仅当仓库实质包含宠物/动物行为的知识、文档、数据集（而非只是训练 app 的源码、与行为无关的宠物商店项目等）。

返回结构化结果，content_scope 写清覆盖的物种与行为主题，data_format 写清格式，sources_fetched 列所有抓取的 URL 与状态。`
}

function verifyPrompt(deep, c) {
  return `你是独立对抗核验 agent。任务是尝试推翻"以下项目是宠物行为知识库/文档"的论断。默认怀疑，证据不足即判 uncertain/refuted。

项目：${c.name}
URL：${c.url}
前一 agent 结论：is_pet_behavior_kb=${deep?.is_pet_behavior_kb}, content_scope=${deep?.content_scope || '(无)'}

执行步骤（必须真实 WebFetch，禁止编造）：
1. 独立 WebFetch 抓 ${c.url} —— prompt: "Does this GitHub repo exist and is it accessible? Is it really about pet/animal BEHAVIOR knowledge or documentation (not just a pet-related app, shop, or unrelated project)? Summarize evidence from README."
2. 若需佐证，WebFetch 抓 ${c.url}/blob/main/README.md 或 master 分支
3. 尝试推翻：项目是否其实不是知识库？是否其实与宠物行为无关？URL 是否 404？

返回 exists（URL 真实可访问）、pet_behavior_confirmed、knowledge_base_confirmed、refutation_attempt（推翻尝试过程）、verdict（confirmed/refuted/uncertain）、sources_fetched。`
}

// ---------- workflow body ----------
phase('Search')
log('启动 5 个并行搜索 agent（API + WebFetch 多策略）')
const searchResults = await parallel(SEARCH_TASKS.map(t => () =>
  agent(t.prompt, { label: t.label, phase: 'Search', schema: SEARCH_SCHEMA, agentType: 'general-purpose', effort: 'medium' })
))

const allCandidates = searchResults.filter(Boolean).flatMap(r => (r.candidates || []).map(c => ({ ...c, _via: r.search_strategy_used })))
const seen = new Set()
const deduped = []
for (const c of allCandidates) {
  const key = (c.name || c.url || '').toLowerCase().replace(/\/+$/, '')
  if (key && !seen.has(key)) { seen.add(key); deduped.push(c) }
}
log(`搜索原始候选 ${allCandidates.length} 个，去重后 ${deduped.length} 个`)

deduped.sort((a, b) => (b.stars || 0) - (a.stars || 0))
const candidates = deduped.slice(0, 12)
log(`选取 top ${candidates.length} 个进入深度调研（按 star 降序，最多 12 个）`)

phase('DeepDive')
const investigated = await pipeline(
  candidates,
  c => agent(deepDivePrompt(c), { label: `deep:${c.name}`, phase: 'DeepDive', schema: DEEP_SCHEMA, agentType: 'general-purpose', effort: 'medium' }),
  (deep, c) => {
    if (!deep || !deep.is_pet_behavior_kb) {
      return Promise.resolve({ candidate: c, deep, verify: null, skipped_verify: true })
    }
    return agent(verifyPrompt(deep, c), { label: `verify:${c.name}`, phase: 'Verify', schema: VERIFY_SCHEMA, agentType: 'general-purpose', effort: 'high' })
      .then(v => ({ candidate: c, deep, verify: v, skipped_verify: false }))
  }
)

const valid = investigated.filter(Boolean)
const confirmed = valid.filter(x => x.deep?.is_pet_behavior_kb && (x.verify ? x.verify.verdict === 'confirmed' : false))
const rejected = valid.filter(x => !x.deep?.is_pet_behavior_kb || (x.verify && x.verify.verdict !== 'confirmed'))
log(`深度调研 ${valid.length} 个，确认 ${confirmed.length} 个，驳回/存疑 ${rejected.length} 个`)

return {
  search_phase: {
    strategies: searchResults.filter(Boolean).map(r => ({ strategy: r.search_strategy_used, sources: r.sources_fetched, candidate_count: (r.candidates || []).length })),
    total_raw: allCandidates.length,
    deduped: deduped.length,
    investigated: candidates.length,
  },
  confirmed_projects: confirmed.map(x => ({
    name: x.candidate.name,
    url: x.candidate.url,
    description: x.candidate.description,
    stars: x.deep?.stars ?? x.candidate.stars,
    content_scope: x.deep?.content_scope,
    data_format: x.deep?.data_format,
    license: x.deep?.license,
    last_updated: x.deep?.last_updated ?? x.candidate.updated,
    activity_level: x.deep?.activity_level,
    strengths: x.deep?.strengths,
    weaknesses: x.deep?.weaknesses,
    verify_verdict: x.verify?.verdict,
    verify_refutation: x.verify?.refutation_attempt,
    sources: [...(x.deep?.sources_fetched || []), ...(x.verify?.sources_fetched || [])],
  })),
  rejected_projects: rejected.map(x => ({
    name: x.candidate.name,
    url: x.candidate.url,
    reason: !x.deep?.is_pet_behavior_kb ? 'not a pet behavior knowledge base' : (x.verify ? `verify verdict: ${x.verify.verdict}` : 'verify skipped'),
    deep_is_kb: x.deep?.is_pet_behavior_kb,
  })),
}
