export const meta = {
  name: 'pet-behavior-kb-research-round2',
  description: '补充深度调研被 star 排序挤出的低 star 文档型宠物行为知识库候选',
  phases: [
    { title: 'DeepDive', detail: '对 10 个低 star/文档型候选逐个 WebFetch 抓 README 判定' },
    { title: 'Verify', detail: '对判定为知识库的候选独立对抗核验' },
  ],
}

const DEEP_SCHEMA = {
  type: 'object',
  properties: {
    name: { type: 'string' },
    url: { type: 'string' },
    fetch_ok: { type: 'boolean', description: 'repo 主页/README 是否真实可访问' },
    is_pet_behavior_kb: { type: 'boolean', description: '是否为宠物/动物行为知识库或文档（非纯 app/工具/训练代码）' },
    content_scope: { type: 'string', description: '内容覆盖范围（物种、行为主题）' },
    data_format: { type: 'string', description: 'markdown/json/wiki/pdf/csv/clp 等' },
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
    exists: { type: 'boolean' },
    pet_behavior_confirmed: { type: 'boolean' },
    knowledge_base_confirmed: { type: 'boolean' },
    refutation_attempt: { type: 'string' },
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

const CANDIDATES = [
  { name: 'sstroell/dog-behavior-framework', url: 'https://github.com/sstroell/dog-behavior-framework', hint: '基于信任的犬类行为概念框架，非编码知识库。README 阐述情感训练理念与阶段，含路线图，v1.0.0 发布于 2025-07-08' },
  { name: 'sstroell/puppy-development-timeline', url: 'https://github.com/sstroell/puppy-development-timeline', hint: '幼犬发育时间线文档知识库，纯 README 无代码' },
  { name: 'sstroell/dogsoul-dictionary', url: 'https://github.com/sstroell/dogsoul-dictionary', hint: '犬类训练术语词典知识库，15 条术语，CC BY 4.0，含 glossary 文件夹' },
  { name: 'sstroell/neurobond-docs', url: 'https://github.com/sstroell/neurobond-docs', hint: 'GitBook 风格文档知识库，含 introduction/philosophy/case-studies/glossary 等结构化 Markdown 章节' },
  { name: 'catiseyeqaq/Real-time-Monitoring-and-Analysis-of-Pet-Behavior', url: 'https://github.com/catiseyeqaq/Real-time-Monitoring-and-Analysis-of-Pet-Behavior', hint: '面向宠物行为健康监测的视觉-音频多模态分析系统，YOLO26 猫咪行为检测 + Qwen VLM + ASR，7 stars' },
  { name: 'kokitakahashi-baulife/dog-curriculum', url: 'https://github.com/kokitakahashi-baulife/dog-curriculum', hint: 'dog-training topic 页发现的狗课程项目' },
  { name: 'codeWithRewaskar/shadow-reactivity-coach', url: 'https://github.com/codeWithRewaskar/shadow-reactivity-coach', hint: 'dog-training topic 页发现的影子反应教练项目' },
  { name: 'orujovshah/Classification-of-Dogs-Emotional-Behaviour', url: 'https://github.com/orujovshah/Classification-of-Dogs-Emotional-Behaviour', hint: '犬类情绪行为分类 CNN，Python ML 项目，2 stars' },
  { name: 'alms93/SingleBehaviorLab', url: 'https://github.com/alms93/SingleBehaviorLab', hint: '动物行为动作定位模型训练工具，支持视频标注到训练全流程 + 无监督行为分析，7 stars' },
  { name: 'ryanpeach/DogBarking', url: 'https://github.com/ryanpeach/DogBarking', hint: 'dog-training topic 页发现的狗叫相关项目' },
]

function deepDivePrompt(c) {
  return `你是 GitHub 深度调研 agent。对单个项目做深度调研，判定其是否为"宠物行为知识库/文档"。

项目：${c.name}
URL：${c.url}
搜索阶段线索：${c.hint}

执行步骤（必须真实 WebFetch，禁止凭记忆编造）：
1. WebFetch 抓 ${c.url} —— prompt: "Summarize this GitHub repo: What is it about? Is it a knowledge base / documentation / dataset about pet or animal behavior? What species and behavior topics does it cover? What format (markdown/json/wiki/pdf/clp)? Stars, license, last commit date, activity level. Quote README headings if any."
2. 若 README 在 repo 页只是摘要，额外 WebFetch 抓 ${c.url}/blob/master/README.md（先试 master 再试 main），任一成功即可
3. 若是文档型仓库（如 sstroell 系列），尝试抓仓库根目录文件列表 ${c.url}/tree/master 或 ${c.url}/tree/main 确认文档结构
4. 若 404/重定向/私有，fetch_ok=false，is_pet_behavior_kb=false，如实标注

判定标准：is_pet_behavior_kb=true 当且仅当仓库实质包含宠物/动物行为的知识、文档、数据集（而非只是训练 app 的源码、与行为无关的宠物商店项目、或通用工具）。注意：纯文档型仓库（无代码、只有 README/markdown）只要内容是宠物/动物行为知识，即为 true，不能因"没有代码"而判 false。

返回结构化结果，content_scope 写清覆盖的物种与行为主题，data_format 写清格式，sources_fetched 列所有抓取的 URL 与状态。`
}

function verifyPrompt(deep, c) {
  return `你是独立对抗核验 agent。任务是尝试推翻"以下项目是宠物行为知识库/文档"的论断。默认怀疑，证据不足即判 uncertain/refuted。

项目：${c.name}
URL：${c.url}
前一 agent 结论：is_pet_behavior_kb=${deep?.is_pet_behavior_kb}, content_scope=${deep?.content_scope || '(无)'}

执行步骤（必须真实 WebFetch，禁止编造）：
1. 独立 WebFetch 抓 ${c.url} —— prompt: "Does this GitHub repo exist and is it accessible? Is it really about pet/animal BEHAVIOR knowledge or documentation (not just a pet-related app, shop, game, or unrelated project)? Summarize evidence from README."
2. 若需佐证，WebFetch 抓 ${c.url}/blob/master/README.md 或 master 分支根目录文件列表
3. 尝试推翻：项目是否其实不是知识库？是否其实与宠物行为无关？URL 是否 404？是否只是游戏/工具/无关项目？

返回 exists、pet_behavior_confirmed、knowledge_base_confirmed、refutation_attempt、verdict、sources_fetched。`
}

phase('DeepDive')
log(`对 ${CANDIDATES.length} 个低 star/文档型候选做深度调研`)
const investigated = await pipeline(
  CANDIDATES,
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
const confirmed = valid.filter(x => x.deep?.is_pet_behavior_kb && x.verify?.verdict === 'confirmed')
const uncertain = valid.filter(x => x.deep?.is_pet_behavior_kb && (!x.verify || x.verify.verdict !== 'confirmed'))
const rejected = valid.filter(x => !x.deep?.is_pet_behavior_kb)
log(`深度调研 ${valid.length} 个，确认 ${confirmed.length} 个，存疑 ${uncertain.length} 个，驳回 ${rejected.length} 个`)

return {
  round: 2,
  confirmed_projects: confirmed.map(x => ({
    name: x.candidate.name,
    url: x.candidate.url,
    stars: x.deep?.stars,
    content_scope: x.deep?.content_scope,
    data_format: x.deep?.data_format,
    license: x.deep?.license,
    last_updated: x.deep?.last_updated,
    activity_level: x.deep?.activity_level,
    strengths: x.deep?.strengths,
    weaknesses: x.deep?.weaknesses,
    verify_verdict: x.verify?.verdict,
    verify_refutation: x.verify?.refutation_attempt,
    sources: [...(x.deep?.sources_fetched || []), ...(x.verify?.sources_fetched || [])],
  })),
  uncertain_projects: uncertain.map(x => ({
    name: x.candidate.name,
    url: x.candidate.url,
    deep_is_kb: x.deep?.is_pet_behavior_kb,
    verify_verdict: x.verify?.verdict,
    content_scope: x.deep?.content_scope,
  })),
  rejected_projects: rejected.map(x => ({
    name: x.candidate.name,
    url: x.candidate.url,
    content_scope: x.deep?.content_scope,
    reason: 'not a pet behavior knowledge base',
  })),
}
