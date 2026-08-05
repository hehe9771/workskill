// 狗文档与知识库开源项目调研 - Dynamic Workflow
// 5 路并行 WebFetch 检索 → 去重 → 逐项目 GitHub API 对抗核验 → 综合报告
// 防伪装：所有 agent 强制返回 sources_fetched（URL + fetch_status），可一眼识别真抓取

export const meta = {
  name: 'dog-doc-kb-research',
  description: '多 agent 全网检索狗文档/知识库开源项目，对抗核验后对比',
  phases: [
    { title: 'Search', detail: '5 路并行 WebFetch 检索（DuckDuckGo/Bing/GitHub topic HTML，不耗 API 配额）' },
    { title: 'Verify', detail: '逐项目 GitHub API 核验 + 对抗推翻' },
    { title: 'Synthesize', detail: '去重对比生成报告' },
  ],
}

const SEARCH_SCHEMA = {
  type: 'object',
  properties: {
    sources_fetched: {
      type: 'array',
      description: '实际抓取的 URL 列表，防伪装校验用',
      items: {
        type: 'object',
        properties: {
          url: { type: 'string' },
          fetch_status: { type: 'string', enum: ['success', 'failed'] },
          snippet: { type: 'string', description: '抓取到的关键内容片段' }
        },
        required: ['url', 'fetch_status']
      }
    },
    candidates: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          repoUrl: { type: 'string', description: 'https://github.com/owner/repo，必须来自实际搜索结果' },
          description: { type: 'string' },
          whyIncluded: { type: 'string' }
        },
        required: ['name', 'repoUrl', 'description']
      }
    },
    searchSummary: { type: 'string' }
  },
  required: ['sources_fetched', 'candidates', 'searchSummary']
}

const VERIFY_SCHEMA = {
  type: 'object',
  properties: {
    sources_fetched: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          url: { type: 'string' },
          fetch_status: { type: 'string', enum: ['success', 'failed'] },
          snippet: { type: 'string' }
        },
        required: ['url', 'fetch_status']
      }
    },
    exists: { type: 'boolean' },
    repoFullName: { type: 'string' },
    description: { type: 'string' },
    stars: { type: 'string' },
    language: { type: 'string' },
    license: { type: 'string' },
    lastUpdate: { type: 'string' },
    topics: { type: 'string' },
    isDogDocOrKb: { type: 'boolean' },
    category: { type: 'string', description: 'dog-doc/dog-kb/dog-breed-db/dog-care/dog-training/dog-health/dog-behavior/dog-nutrition/other' },
    verdict: { type: 'string', enum: ['confirmed', 'refuted', 'uncertain'] },
    refutationAngles: { type: 'string', description: '尝试推翻的角度与结果' },
    evidence: { type: 'string' }
  },
  required: ['sources_fetched', 'exists', 'isDogDocOrKb', 'verdict', 'evidence']
}

const SEARCH_STRATEGIES = [
  {
    key: 'en-broad',
    focus: '英文广泛：狗知识库/文档/wiki/百科',
    queries: [
      'site:github.com dog knowledge base',
      'site:github.com canine knowledge base',
      'site:github.com dog documentation open source',
      'site:github.com dog wiki encyclopedia'
    ]
  },
  {
    key: 'en-breed-care-health',
    focus: '英文：品种数据库/护理指南/健康文档',
    queries: [
      'site:github.com dog breed database',
      'site:github.com dog care guide',
      'site:github.com dog health documentation',
      'site:github.com canine breed information'
    ]
  },
  {
    key: 'zh-chinese',
    focus: '中文：狗知识库/犬类知识库/狗狗百科',
    queries: [
      'site:github.com 狗知识库',
      'site:github.com 犬类知识库',
      'site:github.com 狗狗百科',
      'github 狗文档 开源 知识库'
    ]
  },
  {
    key: 'training-behavior-medical',
    focus: '训练/行为/兽医/营养知识',
    queries: [
      'site:github.com dog training knowledge base',
      'site:github.com veterinary knowledge base',
      'site:github.com dog behavior documentation',
      'site:github.com dog nutrition guide',
      'site:github.com canine medical knowledge'
    ]
  }
]

const GH_TOPIC_URLS = [
  'https://github.com/topics/dog',
  'https://github.com/topics/dogs',
  'https://github.com/topics/dog-training',
  'https://github.com/topics/canine',
  'https://github.com/topics/veterinary',
  'https://github.com/topics/dog-care',
  'https://github.com/topics/pet-care'
]

function buildQueryPrompt(s) {
  const queryLines = s.queries.map((q, i) => `${i + 1}. ${q}`).join('\n')
  return `你是 GitHub 项目检索 agent。任务：用 WebFetch 真实抓取搜索引擎结果页，找"狗文档/狗知识库"开源项目。

【硬性要求 - 防伪装执行】
- 必须实际调用 WebFetch 工具抓取搜索引擎结果页，禁止凭记忆编造项目名
- 每个候选 repoUrl 必须来自你实际 fetch 到的搜索结果页面内容
- 在 sources_fetched 中记录每个实际抓取的 URL + fetch_status(success/failed) + 内容片段
- 若 WebFetch 工具未直接加载，先用 ToolSearch(query="select:WebFetch") 加载其 schema 再调用

【搜索关键词】
${queryLines}

【URL 构造方式】
- DuckDuckGo HTML：https://html.duckduckgo.com/html/?q=<关键词 URL 编码，空格用+>
- Bing：https://www.bing.com/search?q=<关键词 URL 编码，空格用+>
对每个关键词至少抓一个 DuckDuckGo HTML 页；中文关键词可补抓 Bing 页。

【筛选标准】
- 项目主题是狗（dog/canine）相关
- 形态为文档或知识库（documentation/knowledge base/wiki/encyclopedia/glossary/dataset/guide/课程数据/术语词典）
- 排除：纯 ML 训练代码、app 源码、游戏、商店（除非内含可观狗知识内容）
- 也收录：狗品种数据库、狗护理指南、狗训练文档、狗健康/兽医知识、狗行为知识库、狗营养

【返回】sources_fetched + candidates（每个含 name/repoUrl/description/whyIncluded）+ searchSummary。`
}

function buildTopicPrompt() {
  const topicLines = GH_TOPIC_URLS.map((u, i) => `${i + 1}. ${u}`).join('\n')
  return `你是 GitHub 项目检索 agent。任务：用 WebFetch 真实抓取 GitHub topic 页面，找"狗文档/狗知识库"开源项目。

【硬性要求 - 防伪装执行】
- 必须实际调用 WebFetch 工具抓取下列 URL，禁止凭记忆编造项目名
- 每个候选 repoUrl 必须来自你实际 fetch 到的页面内容
- 在 sources_fetched 中记录每个实际抓取的 URL + fetch_status(success/failed) + 内容片段
- 若 WebFetch 工具未直接加载，先用 ToolSearch(query="select:WebFetch") 加载其 schema 再调用

【抓取目标 URL（逐个 WebFetch）】
${topicLines}

【筛选标准】
- 项目主题是狗（dog/canine）相关（veterinary/pet-care topic 下也挑狗相关的）
- 形态为文档或知识库（documentation/knowledge base/wiki/encyclopedia/glossary/dataset/guide/课程数据/术语词典）
- 排除：纯 ML 训练代码、app 源码、游戏、商店（除非内含可观狗知识内容）
- 也收录：狗品种数据库、狗护理指南、狗训练文档、狗健康/兽医知识、狗行为知识库、狗营养

【返回】sources_fetched + candidates（每个含 name/repoUrl/description/whyIncluded）+ searchSummary。`
}

function buildVerifyPrompt(c) {
  return `你是项目核验 agent。任务：用 WebFetch/Bash 真实抓取 GitHub API，对抗式核验候选项目是否为"狗文档/狗知识库"。

【候选项目】
- name: ${c.name}
- repoUrl: ${c.repoUrl}
- 搜索阶段描述: ${c.description || ''}

【硬性要求 - 防伪装执行】
- 必须实际调用 WebFetch 或 Bash(curl) 抓取，禁止凭记忆填充字段
- 在 sources_fetched 中记录实际抓取的 URL + fetch_status + 内容片段
- 若 WebFetch 工具未直接加载，先用 ToolSearch(query="select:WebFetch") 加载

【Step 1 - 抓取 GitHub API 获取结构化数据】
从 repoUrl 提取 owner/repo，调用：
  WebFetch: https://api.github.com/repos/<owner>/<repo>
  或 Bash: curl -s "https://api.github.com/repos/<owner>/<repo>"
解析 JSON：full_name, description, stargazers_count, language, license.spdx_id, pushed_at, topics 等。
若 API 返回 403（限速），改用 WebFetch 抓 https://github.com/<owner>/<repo> 网页，从 HTML 提取 star/描述/最近更新。
若 404，尝试默认分支为 master（raw README 抓 master 而非 main）。

【Step 2 - 对抗式推翻（默认怀疑）】
逐角度尝试推翻：
① URL 是否 404 或不存在？
② 是否其实不是文档/知识库（是 app/游戏/商店/纯工具/纯 ML 代码）？
③ 是否与狗无关（猫/其他动物/无关项目误命中）？
④ 是否只是无关项目误命中关键词？
只有所有角度都推翻失败才判 confirmed；证据不足判 uncertain；明显不符判 refuted。

【返回】sources_fetched + exists + repoFullName + description + stars + language + license + lastUpdate + topics + isDogDocOrKb + category(从 dog-doc/dog-kb/dog-breed-db/dog-care/dog-training/dog-health/dog-behavior/dog-nutrition/other 中选) + verdict(confirmed/refuted/uncertain) + refutationAngles + evidence。`
}

// ===== Phase 1: Search =====
phase('Search')
log('5 路并行检索启动：4 路搜索引擎 + 1 路 GitHub topic 页')

const searchTasks = SEARCH_STRATEGIES.map(s => () =>
  agent(buildQueryPrompt(s), { label: `search:${s.key}`, phase: 'Search', schema: SEARCH_SCHEMA, agentType: 'general-purpose' })
    .then(r => ({ strategy: s.key, focus: s.focus, ...(r || { sources_fetched: [], candidates: [], searchSummary: 'agent returned null' }) }))
)
searchTasks.push(() =>
  agent(buildTopicPrompt(), { label: 'search:gh-topics', phase: 'Search', schema: SEARCH_SCHEMA, agentType: 'general-purpose' })
    .then(r => ({ strategy: 'gh-topics', focus: 'GitHub topic 页', ...(r || { sources_fetched: [], candidates: [], searchSummary: 'agent returned null' }) }))
)

const searchResults = (await parallel(searchTasks)).filter(Boolean)
log(`检索完成：${searchResults.length} 路 agent 返回`)

// 汇总候选
const allCandidates = []
searchResults.forEach(r => {
  (r.candidates || []).forEach(c => allCandidates.push({ ...c, fromStrategy: r.strategy }))
})
log(`候选总数（去重前）：${allCandidates.length}`)

// 去重（按 repoUrl 归一化）
function normRepo(url) {
  if (!url) return ''
  let u = String(url).trim().replace(/\/+$/, '')
  u = u.replace(/^https?:\/\/github\.com\//i, 'https://github.com/')
  u = u.replace(/\.(git|svg)$/, '')
  return u.toLowerCase()
}
const seen = new Set()
const deduped = []
allCandidates.forEach(c => {
  const k = normRepo(c.repoUrl)
  if (!k || seen.has(k)) return
  seen.add(k)
  deduped.push(c)
})
log(`去重后候选：${deduped.length} 个，进入对抗核验`)

// ===== Phase 2: Verify =====
phase('Verify')
const verified = (await parallel(deduped.map(c => () =>
  agent(buildVerifyPrompt(c), { label: `verify:${c.name}`, phase: 'Verify', schema: VERIFY_SCHEMA, agentType: 'general-purpose', effort: 'high' })
    .then(v => ({ candidate: c, verdict: v }))
    .catch(() => null)
))).filter(Boolean)

const confirmed = verified.filter(v => v.verdict && v.verdict.verdict === 'confirmed')
const refuted = verified.filter(v => v.verdict && v.verdict.verdict === 'refuted')
const uncertain = verified.filter(v => v.verdict && v.verdict.verdict === 'uncertain')
log(`核验完成：confirmed ${confirmed.length} / refuted ${refuted.length} / uncertain ${uncertain.length}`)

// ===== Phase 3: Synthesize =====
phase('Synthesize')
const confirmedPayload = JSON.stringify(confirmed.map(v => ({
  name: v.candidate.name,
  repoUrl: v.candidate.repoUrl,
  searchDesc: v.candidate.description,
  verify: v.verdict
})), null, 2)
const refutedPayload = JSON.stringify(refuted.map(v => ({
  name: v.candidate.name,
  repoUrl: v.candidate.repoUrl,
  verdict: v.verdict.verdict,
  refutationAngles: v.verdict.refutationAngles,
  evidence: v.verdict.evidence
})), null, 2)

const synthPrompt = `你是综合分析 agent。基于以下对抗核验结果，生成中文 Markdown 调研报告。

【确认项目 JSON】
${confirmedPayload}

【驳回项目 JSON】
${refutedPayload}

【报告格式（参照既有调研报告风格，输出纯 Markdown，不包代码块）】
1. 标题：# 狗文档与知识库开源项目调研报告
2. 元信息块：调研日期 2026-07-06 ｜ 方法：Dynamic Workflow 多 agent 编排 + 对抗核验 ｜ 调研目标
3. 一、任务与方法：执行约束（无 gh CLI/无 GITHUB_TOKEN，60req/h 限速；WebFetch + GitHub API + DuckDuckGo/Bing 三段式；防伪装 sources_fetched）、Workflow 编排（5 路并行检索 → 去重 → 逐项目对抗核验 → 综合）、对抗核验机制、执行统计（agent 数=检索5+核验${deduped.length}+综合1）
4. 二、确认项目总览（对比表）：# / 项目(repoUrl) / Star / 狗主题 / 数据格式 / License / 活跃度
5. 三、项目详情：每个项目 URL/性质/覆盖/优势/不足/核验结论
6. 四、驳回项目及原因：表格列出 refuted 项目及驳回原因（若有）
7. 五、结论与选型建议：关键发现 + 按用途选型建议表 + 局限性
8. 六、执行元数据：workflow 脚本 code/dog-doc-kb-research/workflow.js、agent 数、防伪装校验说明、核验抽样

【注意】
- 数据必须来自 verify 的 sources_fetched 与 API 抓取结果，不得编造
- 与既有"宠物行为知识库"调研报告重叠的项目（如 sstroell 系列、shadow-reactivity-coach、dog-curriculum、Animal-Kingdom、birnuruzunn/cats），在详情中标注"⚠ 与宠物行为知识库调研重叠"
- 对比表要能一眼看出各项目差异
- 若确认项目数 < 5，在局限性中说明 GitHub 上该品类稀缺

直接输出 Markdown 报告正文。`

const report = await agent(synthPrompt, { label: 'synthesize:report', phase: 'Synthesize', agentType: 'general-purpose', effort: 'high' })

return {
  confirmedCount: confirmed.length,
  refutedCount: refuted.length,
  uncertainCount: uncertain.length,
  totalCandidates: deduped.length,
  confirmed: confirmed.map(v => ({ name: v.candidate.name, repoUrl: v.candidate.repoUrl, stars: v.verdict && v.verdict.stars, category: v.verdict && v.verdict.category })),
  report
}
