---
name: claude-update-report
description: Use when 用户要求检查 Claude Code CLI 版本更新、撰写更新记录/升级分析报告，或提到"更新记录""升级建议""changelog 分析""新版本有什么值得升的"——产出结合本机环境的更新报告。
---

# Claude Code 版本更新报告生成

## Overview

基于 npm registry 版本数据 + 官方 changelog，生成"版本概览 → 重点特性 → 行为变化 → 新增设置 → bug 修复 → 本机关联 → 升级建议"的更新报告，输出到 `doc/claude-code/更新YYYYMMDD.md`（YYYYMMDD = 生成当天日期）。

**核心原则：不是 changelog 翻译。** 报告的价值在于每条更新都回答"这对本机意味着什么"，并标注 ✅ 直接受益 / ⚠️ 无直接效果（附原因）/ 潜在冲突。

## When to Use

- 用户说"检查 Claude Code 更新""写份更新记录""要不要升级 CLI"
- 距 doc/claude-code/ 最新一篇 更新*.md 已超过两周且 CLI 有新版本

## 执行流程

### 1. 确定版本范围

```bash
claude --version                                       # 当前安装版本 = 起点
npm view @anthropic-ai/claude-code dist-tags.latest    # npm 最新版 = 终点
npm view @anthropic-ai/claude-code time --json         # 各版本发布日期（取范围内条目）
```

### 2. 抓取官方 changelog

WebFetch `https://code.claude.com/docs/en/changelog`，提取起点到终点之间的条目。changelog 未列入的版本（如曾经的 2.1.188/189）记入附录，标注"未列入，疑为内部版本/未发布"，不要臆测内容。

### 3. 收集本机环境特征（关联分析依据）

**动态读取，不凭记忆**（环境会变）：

- `~/.claude/settings.json` env 段：`ANTHROPIC_BASE_URL`（非 Anthropic 主机 → Sonnet 新模型/组织默认模型/Remote Control 类更新对本机无直接效果）、`DISABLE_AUTOUPDATER`、上下文窗口相关设置
- 项目与全局 CLAUDE.md 的特殊规则（如"禁用 chrome_devtools、网页浏览用 gstack /browse"——与 Claude in Chrome 类更新存在潜在冲突，需点出）
- `update-all` 技能黑名单：CLI 本体是否被拉黑 → 决定"升级方法"段给手动命令还是自动方式
- doc/claude-code/ 最近一篇 更新*.md 的「与本机环境的关联汇总」表 → 继承本机特征清单（DashScope 代理 / Windows+PowerShell / 1M 窗口 / 重度 skill·agent 用户等）

### 4. 按模板撰写

风格对齐 doc/claude-code/ 最新一篇 更新*.md，保持系列一致。模板见下。

### 5. 输出

写入 `doc/claude-code/更新YYYYMMDD.md`。**禁止**放根目录或其他位置（项目规则）。写完后向用户汇报：跨越版本数、对本机最有价值的 3 项更新、升级建议结论。

## 文档模板

```markdown
# YYYY-MM-DD Claude Code 版本更新记录（v起点 → v终点）

> 本文参考 `更新XXXXXXXX.md` 风格编写，记录 X 到 Y 的功能更新，
> 并结合本机环境（<特征摘要>）给出关联分析与升级建议。
> 数据来源：npm registry（版本号）+ 官方 changelog（URL）。

## 1. 版本概览
[表格：当前安装版本 / npm 最新版 / 跨越版本数 / 发布时间跨度]
[版本清单表：版本 | 发布日期 | 性质]

## 2. 重点新特性详解
[每条一小节，固定三要素：**含义** / **好处**（可选）/ **与本机关系**（必须）]
[对本机有高价值的条目用 ★ 标注，如"★ 重度 agent 用户必看"]

## 3. 行为变化（影响使用习惯）
[每条：**变化** / **影响**；重大变化用 ★★ 标注]

## 4. 新增设置与环境变量
[表格：版本 | 设置/变量 | 作用]
[涉及日志/隐私/权限的条目，表后加**安全提醒**段]

## 5. 重要 bug 修复（挑本机有感项）
[每条：**问题** / **修复** / **与本机关系**；与本机强相关用 ★ 标注]

## 6. 与本机环境的关联汇总
[表格：本机特征 | 相关更新 | 影响（✅/⚠️）]

## 7. 升级建议
### 7.1 是否升级 [结论 + 理由]
### 7.2 升级方法 [结合本机更新策略给可执行命令，附回滚到当前版本的命令]
### 7.3 升级后必做 [重启 daemon、配置检查清单]
### 7.4 不升级的风险

## 附：未列入详解的版本
[changelog 缺失/跳号的版本及说明]
```

## 写作要求

- 每条更新必须给出本机相关性判断，禁止只罗列不分析
- 开头注明来源与风格参考对象
- 升级建议必须结合本机更新策略（黑名单 / `DISABLE_AUTOUPDATER`），不盲目推荐
- 全文中文

## Common Mistakes

| 错误 | 正确做法 |
|------|----------|
| 只翻译 changelog，无本机关联 | 每条回答"对本机意味着什么" |
| 建议 `claude update` 自动升级 | 本机 `DISABLE_AUTOUPDATER=1` 且黑名单含 CLI，给 `npm install -g @anthropic-ai/claude-code@latest` 手动方式 |
| 凭记忆判断本机环境 | 先读 settings.json env 与 CLAUDE.md 当前值 |
| 文档写进根目录 | 只写 `doc/claude-code/更新YYYYMMDD.md` |
| changelog 缺的版本硬编内容 | 进附录标注"未列入"，不臆测 |
