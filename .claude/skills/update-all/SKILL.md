---
name: update-all
description: 一键更新所有 Claude Code 环境组件 — 市场、插件、npm 全局工具、uv 工具、skills。逐组件记录更新结果与版本变迁(from→to)，更新后验证，分析功能差异，并在 doc/update-reports/ 生成更新报告。
version: 2.4.0
source: project-init
allowed-tools: Bash(claude:*) Bash(npm:*) Bash(npx:*) Bash(uv:*) Bash(playwright-cli:*) Bash(specify:*) Bash(git:*) Bash(pnpm:*) Bash(bash:*) Bash(curl:*) Bash(rm:*) Bash(mv:*) Bash(cp:*) Bash(find:*) Bash(cat:*) Bash(ls:*) Bash(awk:*) Bash(sed:*) Bash(grep:*) Bash(mkdir:*) Bash(date:*) Bash(diff:*) Bash(wc:*) Bash(head:*) Bash(timeout:*) Bash(tail:*) Bash(sort:*) Bash(xargs:*) Bash(sha256sum:*) Bash(basename:*) Bash(dirname:*) Bash(uname:*) Bash(test:*) Bash(cmp:*) Read Write
---

# 一键更新所有环境组件

v2.4.0 变更（2026-09-18，命令副本收敛事件固化）：Phase 2 新增命令重名检测（坑 7）：用户级 `~/.claude/commands` 与已装插件 commands 交集 → WARN 同名双套行为；退役命令副本自动清理（坑 7b，`references/cleanup-retired-commands.sh`：与上游退役前版本逐字节一致则自动移除，不一致 WARN 留人工）；历史变更（v2.0.0-v2.2.0）拆分至 `references/CHANGELOG.md`。

v2.3.0 变更（2026-09-18，mattpocock 文档漂移事件固化）：Phase 2 新增文档漂移预警（坑 6）：插件版本 from≠to → WARN 人工核对引用其版本/技能清单的文档；防坑清单扩至 6 坑；事件记录见项目 `doc/claude-code/插件安装与迁移记录.md`。

v2.2.0 及更早变更（v2.2.0 对账预检、v2.1.0 mattpocock 插件化、v2.0.0 版本追踪/验证/差异/报告四能力）：见 `references/CHANGELOG.md`。

## 触发条件

当用户说"更新环境"、"更新所有插件"、"update all"、"升级组件"时，直接执行下方全部阶段，**无需确认**。六阶段按序执行，报告无条件生成。

> **allowed-tools 已知局限**：按命令前缀匹配，复合命令块（如管道中段命令）仍可能触发权限询问；代码块组织上尽量让块首命令落在已允许前缀上。v1.4.0 正文实际使用但未声明的 git/pnpm/bash/coreutils 等命令已在 v2.0.0 frontmatter 补齐；v2.0.0 审查再补齐可执行块实用的其余外部命令 timeout/tail/sort/xargs/sha256sum/basename/dirname/uname/test/cmp（printf/echo/[ 为 bash 内建，无需声明）。

---

## 黑名单（跳过更新）

以下组件已拉黑，**禁止更新**：

| 组件 | 原因 |
|------|------|
| `@anthropic-ai/claude-code` | 自动更新可能导致兼容性问题，需手动控制版本 |
| `claude-notifications-go@claude-notifications-go` | 1.40.0 上游发布缺 Windows exe(残缺版),需手动控制版本 |

> 如需更新黑名单中的组件，请手动执行对应命令。

### ⚠️ 重要：技能黑名单挡不住 daemon 自动更新

本技能的黑名单只阻止下方第 6 类的 `claude plugins update` 命令，**挡不住 Claude Code daemon 自身的插件自动更新机制**。实测：黑名单中的 `claude-notifications-go` 仍被 daemon 偷偷升级到残缺的 1.40.0，`understand-anything` 也被升级后留下残缺（缺 dist/node_modules）。

**根治配置**（已在 `~/.claude/settings.json` 的 `env` 段设置）：

```json
{
  "env": {
    "DISABLE_AUTOUPDATER": "1"
  }
}
```

此为总开关，**同时禁用 CLI 本体 + 所有插件的自动更新**。此后插件只在执行本技能第 6 类或手动 `claude plugin update <plugin>` 时更新。注意：仅靠 `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` 的等价关系不够（子进程可能未继承），必须显式设 `DISABLE_AUTOUPDATER=1`。改后需重启 daemon 生效。

> **⚠️ 自定义 `--settings` 文件必须单独设（2026-07-07 claude-mem 崩溃教训）**：用 `claude --settings <file>` 启动时，该文件的 `env` 段会**覆盖**默认 `~/.claude/settings.json` 的 env，`DISABLE_AUTOUPDATER` **不继承**。因此每个实际使用的 settings 文件（如 `~/.claude/setting/settings-*.json`）都必须在自己的 `env` 段显式加 `"DISABLE_AUTOUPDATER": "1"`。否则 daemon 仍会自动更新插件——2026-07-07 实测：`settings-glm.json` 未设此开关，daemon 自动更新 claude-mem 失败留下残缺 13.10.2，hook 脚本 `ls -dt` 选错版本 + worker 起不来 + `exit 1` 阻断 SessionStart/UserPromptSubmit，导致一切命令无法执行。已删的插件如不补此开关，daemon 仍会自动拉回。

---

## 执行原则（六阶段契约）

v1.4.0 四步契约（执行更新 → 立即验证 → 验证失败记录但继续 → 最后汇总）扩展为六阶段，**"单步失败不中断整体"的容错语义不变**：

1. **Phase 0 预检 + 快照**：纯只读、幂等；一切 rm/mv/install 之前完成；固化全部 from 版本与证据基线。
2. **Phase 1 执行更新**：黑名单门控；单步失败记录 FAILED 后继续下一组件；每命令经 `run_cmd` 留痕；禁用 `set -e`。
3. **Phase 2 验证判定**：只读重探全部 to 版本，按决策表判定 7 态，写 V- 复核行。
4. **Phase 3 证据采集**：必须完整位于 Phase 4 之前；按登记表定向采集，三级降级。
5. **Phase 4 清理 + 健康检查**：一切 `rm -rf` 集中于此（H1–H7，去重后）。
6. **Phase 5 报告 + 汇总**：无条件执行；报告生成失败必须记录，不静默。

## 整体阶段流程

```
Phase 0  预检 + 更新前快照          [新增 · 纯只读 · 幂等]
   │     框架初始化（record_result/run_cmd/log_error、SNAP_DIR/.latest/meta）+ 日志/快照轮转
   │     全部 from 版本探测 + 证据基线固化（含 gstack.bak，赶在 G1 删它之前）+ K0/K1 黑名单只读记录
   ▼
Phase 1  执行更新                  [黑名单门控 · 单步失败不中断 · 每命令经 run_cmd 留痕]
   │     N1 → N2 → G1 gstack → P1（须在 N2 之后）→ U1 specify-cli（含 rm 残留 exe）
   │     → M* marketplaces（一条命令 10 市场）→ P* plugins ×36（逐个更新）
   │     → R1 symlink 退化修复（插件更新后：更新可能重新引入退化）→ E1 ECC 同步（紧跟 ecc）
   │     → C1 superpowers 副本清理（防御性收尾，收敛原 2.5/7/H8）
   ▼
Phase 2  更新后验证 + 状态判定      [只读探测]
   │     统一重探全部 to 版本 → 决策表判定 7 态 → 写 V- 复核行入 results.tsv
   ▼
Phase 3  功能差异证据采集           [必须整段位于 Phase 4 之前]
   │     orphan 抢救 → changelog/commit/diff 定向抽取（三级降级）→ 产出 evidence/ + evidence-manifest.tsv
   ▼
Phase 4  清理 + 健康检查            [全部 rm -rf 集中于此 · H1–H7（去重后）]
   ▼
Phase 5  报告生成 + 终端汇总        [无条件执行]
         Claude 读 results.tsv/快照/证据 → Write 写 $REPORT_DIR/更新报告-*.md（汇总表全要素 + 富状态分布行 + 口头汇报）
```

### 顺序红线（清理动作与健康检查必须排在差异分析之后）

**铁律：Phase 3（证据采集）必须完整位于 Phase 4（一切 rm -rf / 健康检查清理）之前；Phase 0 快照必须位于任何变更动作之前。** 违反即永久丢失证据：

| 易失点 | 销毁时机 | 防护 |
|---|---|---|
| gstack.bak（上一代版本证据） | G1 内部第一步 `rm -rf gstack.bak`（更新**过程中**即销毁） | Phase 0 快照 bak 的 VERSION+HEAD |
| 市场旧 HEAD | `marketplace update` = 删除+重克隆，reflog 无旧 HEAD | Phase 0 逐市场 `rev-parse HEAD`（完整 SHA） |
| orphan 插件目录内 CHANGELOG / notifications-go 缺 exe 版本目录 | H5 清理全部 orphan、H3 先 install.sh 自愈、不可修复才清残缺目录（现存实例：notifications-go 1.40.1 orphan 含 1.39.3→1.40.1 完整 changelog） | Phase 3 第一步 orphan 抢救 + Phase 4 删除前条件拷贝双保险 |
| playwright 旧已装技能 | `install --skills` 一跑即覆盖 | Phase 0 整目录副本 |
| superpowers 用户级副本 VERSION | C1 删除 | Phase 0 快照 VERSION |
| npm/uv/npx 旧版本 | 全部原地覆盖无残留 | Phase 0 manifest/版本快照 |

插件 from→to 版本对一律以 Phase 0 的 `installed_plugins.json` 快照为准，**禁止依赖"新旧缓存目录并存"**（实测 superpowers 6.1.0 目录已消失、understand-anything 2.8.2 是 0 文件空壳）。

### 跨 Bash 调用状态约定（运行环境事实）

Claude Code Bash 工具跨调用不保留 shell 状态（cwd 也重置），因此：
- `SNAP_DIR` 写指针文件 `~/.claude/update-evidence/.latest`，**每个后续 Bash 块开头**先 `SNAP_DIR=$(cat ~/.claude/update-evidence/.latest)` 恢复；
- `PROJECT_ROOT`、`REPORT_DIR`、`START_TIME`、`SKILL_VERSION`、`LOG_FILE` 写入 `$SNAP_DIR/meta`（KEY=VALUE，可 source）；
- `record_result`/`run_cmd`/`log_error` 函数定义在每个需要它们的 Bash 块前置重放（见"通用前置块"）；
- Phase 5 汇总计数从 `results.tsv` 用 awk 重算，不依赖跨调用 shell 变量（单调用内内存计数仍保留用于即时回显）。

---

## 组件登记表

**通用规则（实测教训）**：
- 插件"激活版本"**唯一权威源** = `~/.claude/plugins/installed_plugins.json`；**禁止用 `ls -td`（mtime）或 `sort -V` 判定激活版本**——实测双双选错（understand-anything 选 2.8.2 实为 2.9.4；notifications-go 选中残缺 1.40.1 实为 1.39.3）。缓存目录探测只回答"磁盘上有哪些版本"。
- 本机无 jq，一切 JSON 解析用 `awk -F'"'` 实测方案。
- 探测失败一律降级为 `unknown` 并在 note 强制写"版本解析失败:<命令>"，不中断、不臆测填补。
- 探测命令完整版与样例输出见 `references/version-commands.md`。

### 表 A：更新类组件（Phase 1）

| ID | 组件（component 规范名） | 类别 | 版本键 | 版本探测（要点，全量见 references/version-commands.md） | 更新命令（沿用 v1.4.0） | 更新后验证（Phase 2） | 功能差异证据源 |
|---|---|---|---|---|---|---|---|
| N1 | `npm/html-to-react-components` | npm | semver | `npm list -g ... \| sed` 解析 `@` 后版本 | `npm update -g html-to-react-components` | 重探非空 + exit 0 | 包内 CHANGELOG.md（项目休眠，多数运行无变化） |
| N2 | `npm/@playwright/cli` | npm | semver | 同上，按 scoped 全名锚定 | `npm install -g @playwright/cli@latest` | 重探非空 + exit 0 | 无 changelog → `npm view time --json` + 包内 skills diff（经 P1） |
| G1 | `git/gstack` | git clone | VERSION + HEAD | `cat VERSION`（先 `[ -d ]` 判空）+ `rev-parse --short HEAD`；**.bak 同法，赶在 G1 删它之前** | bak 轮换 → `git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack` → `(cd ... && ./setup)` 子 shell | `.git/HEAD` + `setup` 存在 + 新 VERSION 可读 + setup 退出码 | 新目录 CHANGELOG.md awk 段提取；跨 clone git 对比不可行（对象库不相交，实测），unshallow 后 git log 列为可选 |
| P1 | `skill/playwright-cli-skills` | skill | 工具 semver + 技能目录 hash | `playwright-cli --version 2>&1 \| grep -oE '^[0-9]+\.[0-9]+\.[0-9]+' \| head -1`（行首锚定；**禁止 grep "version"**）+ 技能目录 sha256 | `playwright-cli install --skills` | exit 0 + 已装 SKILL.md 与包内权威文件 cmp 一致 + stderr 无版本不匹配警告框 | Phase 0 旧装技能副本 vs 新包内 skills 的 `diff -r`（install 一跑旧文件即覆盖，Phase 0 快照是唯一旧版） |
| U1 | `uv/specify-cli` | uv | 显示版本串 + **commit_id（对比键）** | `uv tool list \| sed` 剥 v 前缀；对比键取 dist-info 内 `direct_url.json` 的 `commit_id`（grep/sed，无 jq） | `rm -f ~/.local/bin/specify.exe`（教训驱动）→ `uv tool install specify-cli --from "git+https://github.com/github/spec-kit.git" --reinstall` | `uv tool list` 含 specify-cli + `specify --version` 可运行 | commit_id A→B → GitHub compare API（github/spec-kit）；无网络降级"仅 commit 范围 + compare 链接"（--reinstall 版本串恒为 dev，只有 commit 能区分） |
| M* | `mkt/<名称>` ×10（git 型 9 + GCS 型 claude-plugins-official；v2.1.0 新增 mattpocock） | marketplace | git HEAD 全 SHA / gcs-sha | 逐市场先判型：`git -C "$d" rev-parse --git-dir` → `rev-parse HEAD`（**存完整 SHA**）；否则 `.gcs-sha`；两者皆非 → unknown | `claude plugins marketplace update`（实测=删除+重克隆） | update exit 0 + 重探 HEAD/sha 可读 + marketplace list 含该市场 | git 型：旧 HEAD vs 新 HEAD，`fetch --unshallow` 后 `git log OLD..NEW`；降级 compare API。GCS 型：`.gcs-sha` diff + marketplace.json diff，细节下沉插件层 |
| P* | `plugin/<名@市场>` ×36：claude-hud@claude-hud、ecc@ecc、superpowers@claude-plugins-official、understand-anything@understand-anything、ui-ux-pro-max@ui-ux-pro-max-skill、mattpocock-skills@mattpocock、pm-skills 市场插件 ×30（jobs-to-be-done、prd-development、discovery-process、product-strategy-session、roadmap-planning、market-landscape-scan、competitive-analysis-process、saas-revenue-growth-metrics、organic-growth-advisor + 2026-09-18 补装 21 个：problem-framing-canvas、discovery-interview-prep、opportunity-solution-tree、pol-probe-advisor、positioning-workshop、problem-statement、proto-persona、user-story、user-story-splitting、epic-hypothesis、prioritization-advisor、user-story-mapping、epic-breakdown-advisor、feature-investment-advisor、acquisition-channel-advisor、finance-based-pricing-advisor、recommendation-canvas、altitude-horizon-framework、director-readiness-advisor、vp-cpo-readiness-advisor、executive-onboarding-playbook） | plugin | manifest version（semver 或 SHA 形态） | **权威源**：`awk -F'"'` 解析 installed_plugins.json（单插件按 key 过滤） | 逐个 `claude plugins update <p>@<mkt>` | 命令退出码 + manifest 版本对比 + 版本目录存在且**非空壳**（`find <dir> -type f \| head -1` 非空） | 新版 cache 目录 CHANGELOG/RELEASE-NOTES 的 from→to 段 → manifest gitCommitSha compare API → 新旧目录文件清单 diff |
| K0 | `cli/claude-code`（黑名单） | cli | semver | `claude --version 2>/dev/null \| grep -oE '^[0-9]+\.[0-9]+\.[0-9]+' \| head -1` | **禁止更新**（只读记录） | — | 不采集；报告引用 doc/claude-code/ 系列 |
| K1 | `plugin/claude-notifications-go`（黑名单） | plugin | manifest version | 同 P* awk（只读） | **禁止更新**；H3 先 install.sh 自愈、不可修复的残缺目录清理保留 | — | 其 orphan 目录 CHANGELOG 在 Phase 3 抢救 |

### 表 B：修复/同步类组件（状态走 REPAIRED/OK/FAILED）

| ID | 组件 | 动作 | 验证 | 记录语义 |
|---|---|---|---|---|
| R1 | `fix/ui-ux-symlink`（原 2.6） | DEGRADED 检测（scripts/data 是文件非目录）→ 从 cache `src/ui-ux-pro-max/` 复制实体；**位于 P\* 之后**（插件更新可能重新引入退化） | `test -f $UI_SKILL/scripts/search.py` 实证（v1.4.0 验证范式标杆） | 修复成功=REPAIRED；未退化=OK；未安装=NOT_INSTALLED |
| E1 | `sync/ecc`（原 6.5） | `(cd "$ECC_DIR" && bash install.sh --target claude --profile full)` + 按 `STALE_RULES_DIRS` 清理旧顶层 rules（单一变量，E1/H6 共用） | agents 数 ≥ cache 数 且 rules/ecc 数 ≥ cache 内规则目录数（**动态阈值，废弃魔法数字 20**） | 同步成功=REPAIRED；cache 缺失=NOT_INSTALLED |
| C1 | `copy/superpowers`（原 2.5+7+H8 收敛） | **仅在 P* 之后执行一次（防御性）**：`[ -d ~/.claude/skills/superpowers ] && rm -rf ~/.claude/skills/superpowers` | `[ ! -d ~/.claude/skills/superpowers ]` | 删除了=REPAIRED；本无副本=OK。副本 VERSION 已在 Phase 0 快照 |

### 表 C：黑名单与范围外

| 组件 | 处理 |
|---|---|
| K0 `@anthropic-ai/claude-code` | 禁止更新（兼容性需手动控版）；只读记录当前版本进 Phase 0 快照与报告附录；状态 BLACKLIST。 |
| K1 `claude-notifications-go@claude-notifications-go` | 禁止更新（1.40.0 残缺版缺 Windows exe）；只读记录激活版本；H3 先 install.sh 自愈、不可修复的残缺目录仍清理；状态 BLACKLIST。 |
| `claude-mem` | **不在管理范围，完全不碰**：不探测、不记录、不检查、无记录行；仅因 installed_plugins.json 整体 cp 被动出现在报告"环境快照"附录，标注"不在本技能管理范围"。改造中不得恢复对 claude-mem 的任何操作。 |

> 「claude-mem 不在本技能管理范围内，完全跳过，不做任何检查或操作」——v1.4.0 安全决策注释原文保留。

**三处联动**：本技能顶部黑名单表、登记表 K0/K1 行与 Phase 1 代码内 `[黑名单]` 注释，改造时必须同步修改。

---

## 记录框架（v2）

### 通用前置块（每个后续 Bash 块开头必须重放）

```bash
# ===== 通用前置：Claude Code Bash 工具跨调用不保留状态（cwd 也重置），必须重放 =====
SNAP_DIR=$(cat "$HOME/.claude/update-evidence/.latest")
. "$SNAP_DIR/meta"          # 恢复 START_TIME/SNAP_DIR/PROJECT_ROOT/REPORT_DIR/SKILL_VERSION/LOG_FILE
PASS_COUNT=0; FAIL_COUNT=0; SKIP_COUNT=0; FAILURES=""
# 随后重放 record_result / run_cmd / log_error 三个函数定义（见下）；选缓存目录的块另重放 manifest_version / active_cache_dir
```

### record_result v2（兼容签名：前 3 参冻结 + 尾部可选参数）

```bash
record_result() {
  local step="$1" status="$2" desc="$3"
  local component="${4:-}" vfrom="${5:-}" vto="${6:-}" class="${7:-}" verify="${8:-}"
  case $status in                       # 三态计数器保留（向后兼容）
    PASS) PASS_COUNT=$((PASS_COUNT+1)); echo "  PASS [$step] $desc" ;;
    FAIL) FAIL_COUNT=$((FAIL_COUNT+1)); FAILURES="$FAILURES $step"; echo "  FAIL [$step] $desc" ;;
    SKIP) SKIP_COUNT=$((SKIP_COUNT+1)); echo "  SKIP [$step] $desc" ;;
  esac
  # 兼容层：日志行结构冻结（时间戳/三态/step 三括号逐字节不变），富状态注入 desc 前缀
  local rich=""; [ -n "$class" ] && rich="[$class] "
  echo "[$(date '+%H:%M:%S')] [$status] [$step] ${rich}${desc}" >> "$LOG_FILE"
  # 机器层：结构化行旁路到本次运行 TSV（TAB 分隔，字段内 TAB/换行替换为空格，空值写 -）
  [ -n "$SNAP_DIR" ] && printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$step" "${component:--}" "$status" "${class:--}" "${vfrom:--}" "${vto:--}" "${verify:--}" "${desc//$'\t'/ }" >> "$SNAP_DIR/results.tsv"
}
```

### results.tsv（报告唯一状态数据源）

表头：`step	component	status	class	version_from	version_to	verify	desc`。双轨行：

- **动作行**（step=N1/G1/M-all/P-ecc/H1…）：记录命令执行真相（Phase 1/4 写入）。
- **V- 复核行**（step=V-<原 step>）：记录版本真相（Phase 2 写入）。
- 报告 §2 组件总表以 **V- 行**为准，§5 验证表以**动作行 + H 行**为准；真失败时两轨同记 FAIL。

示例：

```
N1	npm/html-to-react-components	PASS	UPDATED	1.6.5	1.6.6	exit=0	npm update exit 0
V-N1	npm/html-to-react-components	PASS	UPDATED	1.6.5	1.6.6	重探非空	复核通过
```

### 状态分类（class，7 态）与三态映射

| class | 报告展示 | 判定 | 映射计数 |
|---|---|---|---|
| `UPDATED` | ✅ 已更新 | 版本键变化 且 验证通过 | PASS |
| `UP_TO_DATE` | ⏸ 已是最新 | 命令成功 且 版本未变（命令输出的"已是最新"不再被当二值丢弃） | PASS |
| `FAILED` | ❌ 更新失败 | 命令失败 或 验证失败 | FAIL |
| `BLACKLIST` | ⏭ 黑名单跳过 | 黑名单命中（from=to=当前值） | SKIP |
| `NOT_INSTALLED` | ⏭ 未安装跳过 | Phase 0 探测为空（统一语义，结束 v1 中 PASS/SKIP 混用） | SKIP |
| `REPAIRED` | 🔧 已修复 | 检测到问题并修复成功（R1/E1/C1/H 类） | PASS（修复失败→FAILED） |
| `OK` | ⏺ 检查正常 | 修复/检查项无需动作 | PASS |

### run_cmd / log_error（禁止静默吞异常）

```bash
run_cmd() { # run_cmd <step> <cmd...>：输出落盘 + 退出码落盘 + 失败留痕
  local step="$1"; shift
  mkdir -p "$SNAP_DIR/out" "$SNAP_DIR/errors"
  "$@" > "$SNAP_DIR/out/$step.log" 2>&1
  local rc=$?                          # 直接取码，不用管道末端（避 PIPESTATUS 陷阱）
  echo "$rc" > "$SNAP_DIR/out/$step.exit"
  if [ $rc -ne 0 ]; then cp "$SNAP_DIR/out/$step.log" "$SNAP_DIR/errors/$step.err"; log_error "$step" "$*" "$rc"; fi
  return $rc
}
log_error() { # log_error <step> <cmd> <rc>：errors.log 索引行 + 明细见 errors/<step>.err
  echo "[$(date '+%H:%M:%S')] [ERROR] [$1] rc=$3 cmd=$2 detail=$SNAP_DIR/errors/$1.err" >> "$SNAP_DIR/errors.log"
}
```

Phase 1 所有更新命令一律经 `run_cmd` 执行；禁用 `set -e`；每命令失败→FAILED 记录后继续下一组件。

### 激活版本缓存目录推导（manifest 唯一权威源；禁止 ls -td/sort -V；需要选缓存目录的块重放：R1/E1/Phase 4）

```bash
manifest_version() { awk -F'"' -v k="$1" '/@/ && /: \[/{key=$2} /"version":/{if($4!="" && key==k) print $4}' "$HOME/.claude/plugins/installed_plugins.json" 2>/dev/null | head -1; }
active_cache_dir() { # active_cache_dir <mkt> <plg> <plugin@mkt>：激活版本缓存目录；manifest 不可读→降级 mtime 选择 + WARN
  local base="$HOME/.claude/plugins/cache/$1/$2" v
  v=$(manifest_version "$3")
  { [ -n "$v" ] && [ -d "$base/$v" ]; } && { echo "$base/$v/"; return; }
  echo "[$(date '+%H:%M:%S')] [WARN] [$3] manifest 不可读或版本目录缺失(v=${v:-空})，降级 mtime 选目录" >> "$LOG_FILE"
  ls -td "$base"/*/ 2>/dev/null | while read -r d; do [ -f "$d/.orphaned_at" ] || { echo "$d"; break; }; done; }
```

### 日志与轮转

- `LOG_FILE=~/.claude/update-all.log`，起止 marker 与完成行 `===== update-all 完成: PASS=x FAIL=y SKIP=z =====` **逐字不变**；完成行后**追加**一行富状态分布（如 `UPDATED=2 UP_TO_DATE=6 REPAIRED=3 ...`）。
- 轮转（补 v1.4.0 缺口）：Phase 0 检查日志 >1MB 时 `mv "$LOG_FILE" "$LOG_FILE.1"`（单代备份）。
- Phase 5 三态计数用 awk 从 results.tsv 重算（排除 V- 复核行避免双计，跨调用稳健），与内存计数不一致时以 TSV 为准。

---

## Phase 0：预检 + 更新前快照

**时机**：技能第一个阶段，一切 rm/mv/install 之前，纯只读、幂等。
**位置**：`EVIDENCE_ROOT=~/.claude/update-evidence`（用户级，不进项目、不进 git；快照是机器中间态不是生成文档，不受 doc/ 规则约束）；保留最近 3 个运行目录。
项目相关路径动态取：`PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)`，禁止硬编码项目路径。

### 块 0-1：框架初始化 + 轮转

```bash
LOG_FILE="$HOME/.claude/update-all.log"
mkdir -p "$HOME/.claude"
# 日志轮转：>1MB 单代备份（补 v1.4.0 缺口）
if [ -f "$LOG_FILE" ] && [ "$(wc -c < "$LOG_FILE")" -gt 1048576 ]; then
  mv "$LOG_FILE" "$LOG_FILE.1"
fi

START_TIME=$(date '+%Y-%m-%d %H:%M:%S')
EVIDENCE_ROOT="$HOME/.claude/update-evidence"
SNAP_DIR="$EVIDENCE_ROOT/$(date '+%Y%m%d-%H%M')"
i=2
while [ -e "$SNAP_DIR" ]; do SNAP_DIR="$EVIDENCE_ROOT/$(date '+%Y%m%d-%H%M')-$i"; i=$((i+1)); done
mkdir -p "$SNAP_DIR/out" "$SNAP_DIR/errors" "$SNAP_DIR/evidence"
echo "$SNAP_DIR" > "$EVIDENCE_ROOT/.latest"

# 快照保留最近 3 份；删除前把目录名写入日志（不静默）
ls -1dt "$EVIDENCE_ROOT"/2* 2>/dev/null | tail -n +4 | while read -r old; do
  echo "[$(date '+%H:%M:%S')] [INFO] 删除过期快照: $old" >> "$LOG_FILE"; rm -rf "$old"; done

PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
REPORT_DIR="${UPDATE_ALL_REPORT_DIR:-$PROJECT_ROOT/doc/update-reports}"
SKILL_VERSION="2.2.0"
cat > "$SNAP_DIR/meta" <<EOF
START_TIME="$START_TIME"
SNAP_DIR="$SNAP_DIR"
PROJECT_ROOT="$PROJECT_ROOT"
REPORT_DIR="$REPORT_DIR"
SKILL_VERSION="$SKILL_VERSION"
LOG_FILE="$LOG_FILE"
EOF

printf 'step\tcomponent\tstatus\tclass\tversion_from\tversion_to\tverify\tdesc\n' > "$SNAP_DIR/results.tsv"
echo "[$START_TIME] ===== update-all 开始 =====" >> "$LOG_FILE"
echo "SNAP_DIR=$SNAP_DIR"
```

### 块 0-2：全部 from 版本探测 + 证据基线固化（通用前置 + 三函数重放后执行）

```bash
VB="$SNAP_DIR/versions-before.env"; : > "$VB"

probe() { # probe <key> <shell 一行式>：空输出降级 unknown + 记日志原因（不中断、不臆测）
  local key="$1" cmd="$2" v
  v=$(bash -c "$cmd" 2>/dev/null | head -1)
  if [ -z "$v" ]; then
    v="unknown"
    echo "[$(date '+%H:%M:%S')] [WARN] [probe] $key 版本解析失败: $cmd" >> "$LOG_FILE"
  fi
  echo "$key=$v" >> "$VB"
}

# --- npm / 工具 / CLI（命令与 2026-08-05 实测一致，全量说明见 references/version-commands.md）---
probe "npm/html-to-react-components" "npm list -g html-to-react-components --depth=0 2>/dev/null | sed -n 's/.*html-to-react-components@\([^ ]*\).*/\1/p'"
probe "npm/@playwright/cli" "npm list -g @playwright/cli --depth=0 2>/dev/null | sed -n 's/.*@playwright\/cli@\([^ ]*\).*/\1/p'"
probe "skill/playwright-cli-tool" "playwright-cli --version 2>&1 | grep -oE '^[0-9]+\.[0-9]+\.[0-9]+' | head -1"
probe "uv/specify-cli" "uv tool list 2>/dev/null | sed -n 's/^specify-cli v\([^ ]*\).*/\1/p'"
probe "cli/claude-code" "claude --version 2>/dev/null | grep -oE '^[0-9]+\.[0-9]+\.[0-9]+' | head -1"

# --- 插件激活版本（唯一权威源；禁止 ls -td / sort -V）---
awk -F'"' '/@/ && /: \[/{key=$2} /"version":/{if($4!="") print "plugin/"key"="$4}' \
  "$HOME/.claude/plugins/installed_plugins.json" >> "$VB" 2>/dev/null
cp "$HOME/.claude/plugins/installed_plugins.json" "$SNAP_DIR/" 2>/dev/null
cp "$HOME/.claude/plugins/known_marketplaces.json" "$SNAP_DIR/" 2>/dev/null

# --- 市场 HEAD / gcs-sha（先判型；存完整 SHA，compare API 需要）---
for d in "$HOME"/.claude/plugins/marketplaces/*/; do
  n=$(basename "$d")
  if git -C "$d" rev-parse --git-dir >/dev/null 2>&1; then
    git -C "$d" rev-parse HEAD > "$SNAP_DIR/mkt-$n.head" 2>/dev/null
    echo "mkt/$n=$(cat "$SNAP_DIR/mkt-$n.head" 2>/dev/null || echo unknown)" >> "$VB"
  elif [ -f "$d/.gcs-sha" ]; then
    cp "$d/.gcs-sha" "$SNAP_DIR/official.gcs-sha"
    echo "mkt/$n=gcs-sha:$(cat "$d/.gcs-sha")" >> "$VB"
  else
    echo "mkt/$n=unknown" >> "$VB"
    echo "[$(date '+%H:%M:%S')] [WARN] 未知市场类型: $n（不炸流程只降级）" >> "$LOG_FILE"
  fi
done
claude plugins marketplace list > "$SNAP_DIR/marketplace-list.txt" 2>&1 || true
cp "$HOME/.claude/plugins/marketplaces/claude-plugins-official/.claude-plugin/marketplace.json" \
   "$SNAP_DIR/official-marketplace.json" 2>/dev/null

# --- gstack 与 gstack.bak（赶在 G1 删 bak 之前固化上一代证据）---
: > "$SNAP_DIR/gstack-before.env"
for g in gstack gstack.bak; do
  d="$HOME/.claude/skills/$g"
  if [ -d "$d" ]; then
    ver=$(cat "$d/VERSION" 2>/dev/null || echo unknown)
    head=$(git -C "$d" rev-parse --short HEAD 2>/dev/null || echo unknown)
  else
    ver="unknown"; head="unknown"
  fi
  echo "$g VERSION=$ver HEAD=$head" >> "$SNAP_DIR/gstack-before.env"
  [ "$g" = "gstack" ] && echo "git/gstack=${ver}(${head})" >> "$VB"
done

# --- specify-cli 对比键 commit_id（venv 内无 .git，direct_url.json 是唯一精确源）---
SPECIFY_DU=$(ls "$APPDATA"/uv/tools/specify-cli/Lib/site-packages/specify_cli-*.dist-info/direct_url.json 2>/dev/null | head -1)
[ -n "$SPECIFY_DU" ] && cp "$SPECIFY_DU" "$SNAP_DIR/specify-direct_url.json"
OLD_COMMIT=$(grep -o '"commit_id": *"[0-9a-f]*"' "$SNAP_DIR/specify-direct_url.json" 2>/dev/null | sed 's/.*"\([0-9a-f]*\)"$/\1/')
echo "uv/specify-cli-commit=${OLD_COMMIT:-unknown}" >> "$VB"

# --- playwright 旧装技能副本（install --skills 一跑即覆盖，Phase 0 快照是唯一旧版）---
mkdir -p "$SNAP_DIR/playwright-installed-skills"
[ -d "$HOME/.claude/skills/playwright-cli" ] && cp -r "$HOME/.claude/skills/playwright-cli" "$SNAP_DIR/playwright-installed-skills/user"
[ -d "$PROJECT_ROOT/.claude/skills/playwright-cli" ] && cp -r "$PROJECT_ROOT/.claude/skills/playwright-cli" "$SNAP_DIR/playwright-installed-skills/project"
PKG_SKILLS="$(npm root -g 2>/dev/null)/@playwright/cli/skills"
[ -d "$PKG_SKILLS" ] && cp -r "$PKG_SKILLS" "$SNAP_DIR/playwright-package-skills"
P1_HASH=$(find "$HOME/.claude/skills/playwright-cli" -type f -print0 2>/dev/null | sort -z | xargs -0 sha256sum 2>/dev/null | sha256sum | awk '{print $1}')
echo "skill/playwright-cli-skills-hash=${P1_HASH:-unknown}" >> "$VB"

# --- superpowers 用户级副本 VERSION + npm 全局清单 + 环境快照 ---
[ -d "$HOME/.claude/skills/superpowers" ] && cp "$HOME/.claude/skills/superpowers/VERSION" "$SNAP_DIR/superpowers-copy.VERSION" 2>/dev/null
npm ls -g --depth=0 > "$SNAP_DIR/npm-global.txt" 2>&1
{
  echo "os=$(uname -s -r 2>/dev/null || echo unknown)"
  echo "proxy: HTTP_PROXY=${HTTP_PROXY:-none} HTTPS_PROXY=${HTTPS_PROXY:-none}"
  for f in "$HOME/.claude/settings.json" "$HOME"/.claude/setting/settings-*.json; do
    [ -f "$f" ] || continue
    if grep -q '"DISABLE_AUTOUPDATER"' "$f"; then echo "DISABLE_AUTOUPDATER 已设: $f"; else echo "[WARN] DISABLE_AUTOUPDATER 缺失: $f"; fi
  done
} > "$SNAP_DIR/env.txt"

# --- K0/K1 黑名单只读记录（BLACKLIST 行：from=to=当前值）---
K0_VER=$(sed -n 's|^cli/claude-code=||p' "$VB" | head -1)
record_result "K0" "SKIP" "黑名单：@anthropic-ai/claude-code 禁止更新（兼容性需手动控版）" "cli/claude-code" "$K0_VER" "$K0_VER" "BLACKLIST" "只读记录"
K1_VER=$(sed -n 's|^plugin/claude-notifications-go@claude-notifications-go=||p' "$VB" | head -1)
record_result "K1" "SKIP" "黑名单：claude-notifications-go 禁止更新（1.40.0 残缺版缺 Windows exe）" "plugin/claude-notifications-go@claude-notifications-go" "$K1_VER" "$K1_VER" "BLACKLIST" "只读记录"

cat "$VB"
```

---

## Phase 1：执行更新

黑名单门控、单步失败不中断、每命令经 run_cmd 留痕。N1/N2/P1 有未安装门控；U1 无条件执行（教训驱动修复型步骤，`--reinstall` 幂等，见下）；其余组件按登记表顺序执行。

```bash
# （通用前置 + 三函数重放后执行）
get_before() { sed -n "s|^$1=||p" "$SNAP_DIR/versions-before.env" | head -1; }

upd() { # upd <step> <component> <from> <cmd...>：未安装门控 + run_cmd + 按退出码记动作行
  local step="$1" comp="$2" from="$3"; shift 3
  if [ -z "$from" ] || [ "$from" = "unknown" ]; then
    record_result "$step" "SKIP" "未安装，跳过更新" "$comp" "unknown" "unknown" "NOT_INSTALLED" "-"
    mkdir -p "$SNAP_DIR/out"; echo "-1" > "$SNAP_DIR/out/$step.exit"
    return 0
  fi
  run_cmd "$step" "$@"; local rc=$?
  if [ $rc -eq 0 ]; then
    record_result "$step" "PASS" "$* exit 0" "$comp" "$from" "" "" "exit=0"
  else
    record_result "$step" "FAIL" "$* exit $rc，明细见 $SNAP_DIR/errors/$step.err" "$comp" "$from" "" "" "exit=$rc"
  fi
  return $rc
}

# --- N1/N2：npm 全局工具 ---
upd N1 npm/html-to-react-components "$(get_before npm/html-to-react-components)" npm update -g html-to-react-components
upd N2 npm/@playwright/cli "$(get_before npm/@playwright/cli)" npm install -g @playwright/cli@latest
# [黑名单] npm install -g @anthropic-ai/claude-code@latest   ← 禁止执行（K0，与顶部黑名单表联动）

# --- G1：gstack（bak 轮换 → clone → 子 shell setup；bak 的 VERSION/HEAD 已在 Phase 0 快照）---
if [ -d "$HOME/.claude/skills/gstack" ]; then
  rm -rf "$HOME/.claude/skills/gstack.bak"
  mv "$HOME/.claude/skills/gstack" "$HOME/.claude/skills/gstack.bak"
fi
run_cmd G1 git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git "$HOME/.claude/skills/gstack"
rc=$?
if [ $rc -eq 0 ]; then
  record_result "G1" "PASS" "git clone exit 0" "git/gstack" "$(get_before git/gstack)" "" "" "exit=0"
  run_cmd G1-setup bash -c 'cd ~/.claude/skills/gstack && ./setup'   # 子 shell，规避 cd 污染路径坑
  src=$?
  [ $src -eq 0 ] && record_result "G1-setup" "PASS" "gstack setup exit 0" "git/gstack" "" "" "" "exit=0" \
                 || record_result "G1-setup" "FAIL" "gstack setup exit $src（见 errors/G1-setup.err）" "git/gstack" "" "" "" "exit=$src"
else
  record_result "G1" "FAIL" "git clone exit $rc（见 errors/G1.err）" "git/gstack" "$(get_before git/gstack)" "" "" "" "exit=$rc"
fi

# --- P1：playwright skills（须在 N2 之后，让包内权威技能先更新）---
# 教训（v1.4.0 原文保留）：--version 只输出纯版本号如 0.1.15，不含 "version" 字样，不可用 grep "version"
upd P1 skill/playwright-cli-skills "$(get_before skill/playwright-cli-tool)" playwright-cli install --skills

# --- U1：specify-cli（先清残留 exe，教训驱动，防 ModuleNotFoundError）---
# 不走未安装门控：--reinstall 幂等；故障态（残留 exe 但 uv tool list 无条目）下门控判 NOT_INSTALLED 会只删 exe 不装回，故无条件执行（见故障排查节）
rm -f "$HOME/.local/bin/specify.exe" 2>/dev/null || true
run_cmd U1 uv tool install specify-cli --from "git+https://github.com/github/spec-kit.git" --reinstall
rc=$?
[ $rc -eq 0 ] && record_result "U1" "PASS" "uv tool install --reinstall exit 0" "uv/specify-cli" "$(get_before uv/specify-cli)" "" "" "exit=0" \
              || record_result "U1" "FAIL" "uv tool install --reinstall exit $rc，明细见 $SNAP_DIR/errors/U1.err" "uv/specify-cli" "$(get_before uv/specify-cli)" "" "" "exit=$rc"

# --- M*：市场（一条命令全量，9 个市场；update=删除+重克隆，旧 HEAD 以 Phase 0 快照为准）---
upd M-all mkt/all present claude plugins marketplace update

# --- P*：插件逐个更新（列表为登记表数据；持久化 plugins.list 单源，供 Phase 2 复核读取——变量不跨 Bash 调用）---
# v2.1.0：mattpocock-skills 插件化（替代原 S1 npx skills 安装），pm-skills 市场全部 30 个已装插件
PLUGINS_TO_UPDATE="claude-hud@claude-hud ecc@ecc superpowers@claude-plugins-official understand-anything@understand-anything ui-ux-pro-max@ui-ux-pro-max-skill mattpocock-skills@mattpocock jobs-to-be-done@pm-skills prd-development@pm-skills discovery-process@pm-skills product-strategy-session@pm-skills roadmap-planning@pm-skills market-landscape-scan@pm-skills competitive-analysis-process@pm-skills saas-revenue-growth-metrics@pm-skills organic-growth-advisor@pm-skills problem-framing-canvas@pm-skills discovery-interview-prep@pm-skills opportunity-solution-tree@pm-skills pol-probe-advisor@pm-skills positioning-workshop@pm-skills problem-statement@pm-skills proto-persona@pm-skills user-story@pm-skills user-story-splitting@pm-skills epic-hypothesis@pm-skills prioritization-advisor@pm-skills user-story-mapping@pm-skills epic-breakdown-advisor@pm-skills feature-investment-advisor@pm-skills acquisition-channel-advisor@pm-skills finance-based-pricing-advisor@pm-skills recommendation-canvas@pm-skills altitude-horizon-framework@pm-skills director-readiness-advisor@pm-skills vp-cpo-readiness-advisor@pm-skills executive-onboarding-playbook@pm-skills"
printf '%s\n' $PLUGINS_TO_UPDATE > "$SNAP_DIR/plugins.list"
for plugin in $PLUGINS_TO_UPDATE; do
  upd "P-${plugin%%@*}" "plugin/$plugin" "$(get_before "plugin/$plugin")" claude plugins update "$plugin"
done
# [黑名单] claude plugins update claude-notifications-go@claude-notifications-go
# claude-mem 不在本技能管理范围内，完全跳过，不做任何检查或操作
```

### R1：ui-ux-pro-max symlink 退化修复（原 2.6；移到插件更新后：更新可能重新引入退化）

> **问题根因**：Windows `core.symlinks=false` 下，`claude plugins update` 检出时把 symlink 变成含目标路径的文本文件（30-40B），导致 `search.py` 等不可达。

```bash
# （通用前置 + 三函数 + manifest_version/active_cache_dir 重放后执行）
UI_SKILL="$HOME/.claude/skills/ui-ux-pro-max"
UI_CACHE=$(active_cache_dir ui-ux-pro-max-skill ui-ux-pro-max ui-ux-pro-max@ui-ux-pro-max-skill)
if [ -d "$UI_CACHE" ] && [ -d "$UI_SKILL" ]; then
  DEGRADED=0
  for item in scripts data; do
    [ -f "$UI_SKILL/$item" ] && [ ! -d "$UI_SKILL/$item" ] && DEGRADED=1
  done
  if [ "$DEGRADED" -eq 1 ]; then
    rm -f "$UI_SKILL/scripts" "$UI_SKILL/data"
    cp -r "$UI_CACHE/src/ui-ux-pro-max/scripts" "$UI_SKILL/scripts"
    cp -r "$UI_CACHE/src/ui-ux-pro-max/data" "$UI_SKILL/data"
    if test -f "$UI_SKILL/scripts/search.py"; then
      record_result "R1" "PASS" "ui-ux-pro-max symlink 已修复" "fix/ui-ux-symlink" "" "" "REPAIRED" "test -f search.py 通过"
    else
      record_result "R1" "FAIL" "ui-ux-pro-max symlink 修复失败" "fix/ui-ux-symlink" "" "" "FAILED" "test -f search.py 失败"
    fi
  else
    record_result "R1" "PASS" "ui-ux-pro-max scripts/data 正常，无需修复" "fix/ui-ux-symlink" "" "" "OK" "未退化"
  fi
else
  record_result "R1" "SKIP" "ui-ux-pro-max 未安装" "fix/ui-ux-symlink" "" "" "NOT_INSTALLED" "-"
fi
```

### E1：ECC 资源同步（紧跟 ecc 插件之后；原 6.5）

> **问题根因**：`claude plugins update ecc@ecc` 只更新 plugin cache（`~/.claude/plugins/cache/ecc/`），**不会自动同步** rules/agents/skills/commands 到用户级目录。ECC 升级后，本地 rules/agents 仍是旧版（如缺少 Prompt Defense 安全层），新 agent 不生效。
>
> **解决**：每次 ECC 插件更新后，跑 `install.sh --profile full` 重新同步。同时清理旧顶层重复 rules（`rules/common`、`rules/python` 等），避免与新的 `rules/ecc/` 结构双重注入。

```bash
# （通用前置 + 三函数 + manifest_version/active_cache_dir 重放后执行）
STALE_RULES_DIRS="common cpp golang kotlin perl php python swift typescript"   # 单一变量，E1/H6 共用（消除 v1.4.0 双份清单）
ECC_DIR=$(active_cache_dir ecc ecc ecc@ecc)
if [ -n "$ECC_DIR" ] && [ -f "$ECC_DIR/install.sh" ]; then
  run_cmd E1 bash -c "cd '$ECC_DIR' && bash install.sh --target claude --profile full"   # 子 shell，规避 cd 污染路径坑
  rc=$?
  for d in $STALE_RULES_DIRS; do
    [ -d "$HOME/.claude/rules/$d" ] && rm -rf "$HOME/.claude/rules/$d"
  done
  AGENTS_N=$(ls "$HOME"/.claude/agents/*.md 2>/dev/null | wc -l)
  RULES_N=$(ls "$HOME"/.claude/rules/ecc/ 2>/dev/null | grep -v README | wc -l)
  CACHE_AGENTS=$(ls "$ECC_DIR"/agents/*.md 2>/dev/null | wc -l)
  CACHE_RULES=$(ls "$ECC_DIR/rules/" 2>/dev/null | grep -v README | wc -l)
  if [ $rc -eq 0 ] && [ "$AGENTS_N" -ge "$CACHE_AGENTS" ] && [ "$RULES_N" -ge "$CACHE_RULES" ]; then
    record_result "E1" "PASS" "ECC 同步完成 (agents=$AGENTS_N/$CACHE_AGENTS rules/ecc=$RULES_N/$CACHE_RULES)" "sync/ecc" "" "" "REPAIRED" "动态阈值通过"
  else
    record_result "E1" "FAIL" "ECC 同步不完整 (install exit=$rc agents=$AGENTS_N/$CACHE_AGENTS rules=$RULES_N/$CACHE_RULES)" "sync/ecc" "" "" "FAILED" "见 errors/E1.err"
  fi
else
  record_result "E1" "SKIP" "ECC plugin cache 未找到" "sync/ecc" "" "" "NOT_INSTALLED" "-"
fi
```

### C1：superpowers 副本单点清理（原 7 + 2.5/7/H8 收敛）

> **问题根因（C1）**：`npx skills@latest add mattpocock/skills`（v2.0.0 及之前的 S1 步骤，v2.1.0 已移除）会在 `~/.claude/skills/superpowers/` 创建静态副本，与 plugin cache（`claude plugins update superpowers@claude-plugins-official`）完全独立。两套同时存在导致 Claude Code 可能加载旧版。
>
> **解决**：删除用户级副本，让 plugin cache 通过 plugin.json 自动加载。v2.1.0 起 npx skills 不再运行，本步为**防御性清理**（手动跑其他技能包安装仍可能重建副本），位置在 P* 之后。

```bash
# （通用前置 + 三函数 + get_before 重放后执行）
get_before() { sed -n "s|^$1=||p" "$SNAP_DIR/versions-before.env" | head -1; }

# --- C1：superpowers 用户级副本清理（防御性，P* 之后执行一次）---
if [ -d "$HOME/.claude/skills/superpowers" ]; then
  CP_VER=$(cat "$SNAP_DIR/superpowers-copy.VERSION" 2>/dev/null || echo unknown)
  rm -rf "$HOME/.claude/skills/superpowers"
  if [ ! -d "$HOME/.claude/skills/superpowers" ]; then
    record_result "C1" "PASS" "superpowers 过期副本已清理 (v$CP_VER)" "copy/superpowers" "$CP_VER" "-" "REPAIRED" "副本不存在"
  else
    record_result "C1" "FAIL" "superpowers 副本删除失败" "copy/superpowers" "$CP_VER" "-" "FAILED" "删除后仍存在"
  fi
else
  record_result "C1" "PASS" "superpowers 无用户级副本（plugin cache 直接生效）" "copy/superpowers" "" "" "OK" "无副本"
fi
```

---

## Phase 2：更新后验证 + 状态判定

对每个更新类组件统一重探 to 版本（探测命令与 from 同款，见 references/version-commands.md），按决策表判定 class 并写 V- 行：

| 条件 | 判定 |
|---|---|
| 更新命令 exit≠0 | FAILED（无论版本是否变化） |
| exit=0 但 to 版本探测为空/失败 | FAILED（verify 注"探测失败"，字段写 unknown） |
| exit=0 且 to≠from 且功能验证通过 | UPDATED |
| exit=0 且 to≠from 但功能验证失败 | FAILED（note 记"版本已变但验证失败"） |
| exit=0 且 to==from | UP_TO_DATE |
| 黑名单组件 | BLACKLIST（from=to=当前值，只读；Phase 0 已记） |
| Phase 0 探测为空（未安装，exit=-1） | NOT_INSTALLED（跳过更新） |

```bash
# （通用前置 + 三函数重放后执行）
TSV="$SNAP_DIR/results.tsv"
get_before() { sed -n "s|^$1=||p" "$SNAP_DIR/versions-before.env" | head -1; }
exit_of() { cat "$SNAP_DIR/out/$1.exit" 2>/dev/null || echo 1; }

judge() { # judge <step> <component> <from> <to> <action_rc> <verify_rc> <verify_note>
  local step="$1" comp="$2" from="$3" to="$4" arc="$5" vrc="$6" note="$7" class status
  if [ "$arc" = "-1" ]; then class="NOT_INSTALLED"; status="SKIP"
  elif [ "$arc" != "0" ]; then class="FAILED"; status="FAIL"
  elif [ -z "$to" ] || [ "$to" = "unknown" ]; then class="FAILED"; status="FAIL"; note="探测失败;$note"
  elif [ "$vrc" != "0" ]; then class="FAILED"; status="FAIL"; note="版本已变但验证失败;$note"
  elif [ "$to" != "$from" ]; then class="UPDATED"; status="PASS"
  else class="UP_TO_DATE"; status="PASS"; fi
  record_result "V-$step" "$status" "$comp: $from -> $to" "$comp" "$from" "$to" "$class" "$note"
  # 回填对应动作行的 class（报告 §2 以 V- 行为准，§5 以动作行为准）
  awk -F'\t' -v OFS='\t' -v s="$step" -v c="$class" '$1==s{$4=c} {print}' "$TSV" > "$TSV.tmp" && mv "$TSV.tmp" "$TSV"
}

# --- N1/N2：重探非空即验证通过（to 为空由 judge 判 FAILED）---
from=$(get_before "npm/html-to-react-components")
to=$(npm list -g html-to-react-components --depth=0 2>/dev/null | sed -n 's/.*html-to-react-components@\([^ ]*\).*/\1/p')
judge N1 npm/html-to-react-components "${from:-unknown}" "${to:-unknown}" "$(exit_of N1)" 0 "重探非空"

from=$(get_before "npm/@playwright/cli")
to=$(npm list -g @playwright/cli --depth=0 2>/dev/null | sed -n 's/.*@playwright\/cli@\([^ ]*\).*/\1/p')
judge N2 npm/@playwright/cli "${from:-unknown}" "${to:-unknown}" "$(exit_of N2)" 0 "重探非空"

# --- G1：.git/HEAD + setup 存在 + 新 VERSION 可读 + setup 退出码 ---
from=$(get_before "git/gstack")
to_ver=$(cat "$HOME/.claude/skills/gstack/VERSION" 2>/dev/null || echo unknown)
to_head=$(git -C "$HOME/.claude/skills/gstack" rev-parse --short HEAD 2>/dev/null || echo unknown)
vrc=0
{ [ -f "$HOME/.claude/skills/gstack/.git/HEAD" ] && [ -f "$HOME/.claude/skills/gstack/setup" ] && [ "$to_ver" != "unknown" ] \
  && [ -f "$SNAP_DIR/out/G1-setup.exit" ] && [ "$(cat "$SNAP_DIR/out/G1-setup.exit")" = "0" ]; } || vrc=1
judge G1 git/gstack "${from:-unknown}" "${to_ver}(${to_head})" "$(exit_of G1)" "$vrc" ".git/HEAD+setup 存在，VERSION 可读，setup exit 0"

# --- P1：SKILL.md cmp + 无版本不匹配警告框 + 技能目录 hash 对比（版本键=工具 semver + 目录 hash）---
from=$(get_before "skill/playwright-cli-tool")
to=$(playwright-cli --version 2>&1 | grep -oE '^[0-9]+\.[0-9]+\.[0-9]+' | head -1)
PKG_SKILL="$(npm root -g 2>/dev/null)/@playwright/cli/skills/playwright-cli/SKILL.md"
vrc=1
for inst in "$HOME/.claude/skills/playwright-cli/SKILL.md" "$PROJECT_ROOT/.claude/skills/playwright-cli/SKILL.md"; do
  [ -f "$inst" ] && cmp -s "$PKG_SKILL" "$inst" && vrc=0
done
note="SKILL.md 与包内权威文件 cmp"
playwright-cli --version 2>&1 | grep -q "does not match the tool version" && note="$note；仍有版本不匹配警告框（可能为其他副本残留）"
# 技能目录 hash 对比（命令与 Phase 0 同款）：上游只改 skills 内容而工具版本不变时防 UP_TO_DATE 假阴性
OLD_HASH=$(get_before "skill/playwright-cli-skills-hash")
NEW_HASH=$(find "$HOME/.claude/skills/playwright-cli" -type f -print0 2>/dev/null | sort -z | xargs -0 sha256sum 2>/dev/null | sha256sum | awk '{print $1}')
judge P1 skill/playwright-cli-skills "${from:-unknown}(h:${OLD_HASH:0:8})" "${to:-unknown}(h:${NEW_HASH:0:8})" "$(exit_of P1)" "$vrc" "$note；技能 hash ${OLD_HASH:0:8}→${NEW_HASH:0:8}"

# --- U1：对比键=commit_id（--reinstall 版本串恒为 dev，只有 commit 能区分更新前后）；新 commit 落盘供 Phase 3 ---
from=$(get_before "uv/specify-cli")
to_ver=$(uv tool list 2>/dev/null | sed -n 's/^specify-cli v\([^ ]*\).*/\1/p')
NEW_DU=$(ls "$APPDATA"/uv/tools/specify-cli/Lib/site-packages/specify_cli-*.dist-info/direct_url.json 2>/dev/null | head -1)
[ -n "$NEW_DU" ] && cp "$NEW_DU" "$SNAP_DIR/specify-direct_url-after.json"   # 落盘供 Phase 3
NEW_COMMIT=$(grep -o '"commit_id": *"[0-9a-f]*"' "$SNAP_DIR/specify-direct_url-after.json" 2>/dev/null | sed 's/.*"\([0-9a-f]*\)"$/\1/')
OLD_COMMIT=$(get_before "uv/specify-cli-commit"); vrc=0; specify --version >/dev/null 2>&1 || vrc=1
if [ -n "$NEW_COMMIT" ] && [ -n "$OLD_COMMIT" ] && [ "$OLD_COMMIT" != "unknown" ]; then
  judge U1 uv/specify-cli "${from:-unknown} (commit ${OLD_COMMIT:0:8})" "${to_ver:-unknown} (commit ${NEW_COMMIT:0:8})" "$(exit_of U1)" "$vrc" "specify --version 可运行；对比键=commit_id"
else   # 降级：commit 对比键缺失，退回 dev 版本串对比，不静默
  echo "[$(date '+%H:%M:%S')] [WARN] [U1] commit 对比键缺失(旧=${OLD_COMMIT:-空} 新=${NEW_COMMIT:-空})，降级 dev 串对比" >> "$LOG_FILE"
  judge U1 uv/specify-cli "${from:-unknown}" "${to_ver:-unknown}" "$(exit_of U1)" "$vrc" "specify --version 可运行；commit 对比键缺失"
fi

# --- M*：逐市场重探 HEAD/sha（update exit 码以 M-all 计）---
M_RC=$(exit_of M-all)
claude plugins marketplace list > "$SNAP_DIR/marketplace-list-after.txt" 2>&1 || true
for d in "$HOME"/.claude/plugins/marketplaces/*/; do
  n=$(basename "$d")
  from=$(get_before "mkt/$n"); from="${from#gcs-sha:}"
  if git -C "$d" rev-parse --git-dir >/dev/null 2>&1; then
    to=$(git -C "$d" rev-parse HEAD 2>/dev/null)
  elif [ -f "$d/.gcs-sha" ]; then
    to=$(cat "$d/.gcs-sha" 2>/dev/null)
  else
    to="unknown"
  fi
  vrc=0; claude plugins marketplace list 2>/dev/null | grep -q "$n" || vrc=1
  judge "M-$n" "mkt/$n" "${from:-unknown}" "${to:-unknown}" "$M_RC" "$vrc" "HEAD/sha 重读 + marketplace list 含该市场"
done

# --- P*：manifest 版本对比 + 版本目录存在且非空壳（防空壳/残缺安装）---
# 插件清单读 Phase 1 持久化的 plugins.list（跨调用变量为空，循环会静默跑 0 次）
[ -s "$SNAP_DIR/plugins.list" ] || echo "[$(date '+%H:%M:%S')] [ERROR] [P*] plugins.list 缺失或为空（Phase 1 未执行？），无法逐插件复核" >> "$LOG_FILE"
awk -F'"' '/@/ && /: \[/{key=$2} /"version":/{if($4!="") print key"="$4}' \
  "$HOME/.claude/plugins/installed_plugins.json" > "$SNAP_DIR/plugin-versions-after.env" 2>/dev/null
for plugin in $(cat "$SNAP_DIR/plugins.list" 2>/dev/null); do
  step="P-${plugin%%@*}"
  from=$(get_before "plugin/$plugin")
  to=$(sed -n "s|^$plugin=||p" "$SNAP_DIR/plugin-versions-after.env" | head -1)
  mkt="${plugin##*@}"; pname="${plugin%%@*}"
  vdir="$HOME/.claude/plugins/cache/$mkt/$pname/$to"
  vrc=1
  [ -d "$vdir" ] && [ -n "$(find "$vdir" -type f 2>/dev/null | head -1)" ] && vrc=0
  judge "$step" "plugin/$plugin" "${from:-unknown}" "${to:-unknown}" "$(exit_of "$step")" "$vrc" "manifest 版本对比 + 版本目录非空壳"
done
# 计数校验（不静默）：V-P-* 复核行数应等于清单长度
EXPECT_N=$(wc -l < "$SNAP_DIR/plugins.list" 2>/dev/null); EXPECT_N=${EXPECT_N:-0}; GOT_N=$(awk -F'\t' '$1 ~ /^V-P-/' "$TSV" | wc -l)
[ "$GOT_N" -eq "$EXPECT_N" ] || echo "[$(date '+%H:%M:%S')] [ERROR] [P*] V- 复核行数不符：期望 $EXPECT_N 实际 $GOT_N" >> "$LOG_FILE"

# --- 插件对账预检（v2.2.0 固化；坑清单见 references/plugin-pitfalls.md）---
# 反向对账：已装但不在 PLUGINS_TO_UPDATE 清单 → WARN（防静默漏更新；排除黑名单/管理范围外）
awk -F'"' '/@/ && /: \[/{print $2}' "$HOME/.claude/plugins/installed_plugins.json" 2>/dev/null | sort -u > "$SNAP_DIR/installed-all.list"
sort "$SNAP_DIR/plugins.list" -o "$SNAP_DIR/plugins.list"
comm -23 "$SNAP_DIR/installed-all.list" "$SNAP_DIR/plugins.list" \
  | grep -v -e '^claude-notifications-go@' -e '^claude-mem@' -e '^paddle@' > "$SNAP_DIR/not-in-update-list.txt"
[ -s "$SNAP_DIR/not-in-update-list.txt" ] \
  && echo "[$(date '+%H:%M:%S')] [WARN] [P*] 以下已装插件不在 PLUGINS_TO_UPDATE 清单（每轮更新静默跳过），请同步扩登记表: $(tr '\n' ' ' < "$SNAP_DIR/not-in-update-list.txt")" >> "$LOG_FILE"
# 死条目检测：enabledPlugins 标 true 但未安装（启用≠安装；典型根因=市场同名撞车或卸载残留）
grep -o '"[^"]*@[^"]*": *true' "$HOME/.claude/settings.json" 2>/dev/null | sed 's/[": ]//g; s/true$//' | sort -u > "$SNAP_DIR/enabled.list"
comm -23 "$SNAP_DIR/enabled.list" "$SNAP_DIR/installed-all.list" > "$SNAP_DIR/dead-enabled.txt"
[ -s "$SNAP_DIR/dead-enabled.txt" ] \
  && echo "[$(date '+%H:%M:%S')] [WARN] [P*] enabledPlugins 死条目（启用但未装）: $(tr '\n' ' ' < "$SNAP_DIR/dead-enabled.txt")；处置见 references/plugin-pitfalls.md 坑2/坑3" >> "$LOG_FILE"
: > "$SNAP_DIR/plugins-version-changed.txt"; for plugin in $(cat "$SNAP_DIR/plugins.list" 2>/dev/null); do vfrom=$(get_before "plugin/$plugin"); vto=$(sed -n "s|^$plugin=||p" "$SNAP_DIR/plugin-versions-after.env" | head -1); [ -n "$vfrom" ] && [ -n "$vto" ] && [ "$vfrom" != "$vto" ] && echo "$plugin $vfrom->$vto" >> "$SNAP_DIR/plugins-version-changed.txt"; done
[ -s "$SNAP_DIR/plugins-version-changed.txt" ] && echo "[$(date '+%H:%M:%S')] [WARN] [P*] 以下插件版本已变化，引用其版本号/技能清单/技能名的文档可能漂移（坑6，人工核对，处置与已知文档位置见 references/plugin-pitfalls.md）: $(tr '\n' ' ' < "$SNAP_DIR/plugins-version-changed.txt")" >> "$LOG_FILE"
find "$HOME"/.claude/plugins/cache/*/*/*/commands -name '*.md' 2>/dev/null | sed 's|.*/||; s|\.md$||' | sort -u > "$SNAP_DIR/plugin-cmd-names.txt"; : > "$SNAP_DIR/cmd-collision.txt"; for f in "$HOME/.claude/commands/"*.md; do [ -e "$f" ] || continue; n=$(basename "$f" .md); grep -qix "$n" "$SNAP_DIR/plugin-cmd-names.txt" && echo "$n" >> "$SNAP_DIR/cmd-collision.txt"; done
[ -s "$SNAP_DIR/cmd-collision.txt" ] && echo "[$(date '+%H:%M:%S')] [WARN] [P*] 用户级命令与插件命令重名（同名双套行为，坑7，人工核对，处置见 references/plugin-pitfalls.md）: $(tr '\n' ' ' < "$SNAP_DIR/cmd-collision.txt")" >> "$LOG_FILE"
[ -f "$HOME/.claude/skills/update-all/references/cleanup-retired-commands.sh" ] && bash "$HOME/.claude/skills/update-all/references/cleanup-retired-commands.sh" >> "$LOG_FILE" 2>&1
```

验证结果进报告 §5 表一；Phase 4 的 H 检查进 §5 表二。

---

## Phase 3：功能差异证据采集

**时机**：Phase 2 完成后、Phase 4 任何 rm 之前。**完整采集指引（读取命令 + 三级降级链 + 固定降级句 + 举例白名单）见本技能目录 `references/evidence-guide.md`，执行前 Read 该文件。** 此处只留 orphan 抢救（第一步）与产出约定。

```bash
# （通用前置重放后执行）
# --- orphan 抢救（H5 删除前最后窗口；现存实例：notifications-go 1.40.1 orphan 含完整 changelog）---
find "$HOME/.claude/plugins/cache" -name ".orphaned_at" 2>/dev/null | while read m; do
  d=$(dirname "$m"); pv=$(basename "$d"); mkdir -p "$SNAP_DIR/evidence/orphan/$pv"
  for f in CHANGELOG.md RELEASE-NOTES.md VERSION package.json; do [ -f "$d/$f" ] && cp "$d/$f" "$SNAP_DIR/evidence/orphan/$pv/"; done
done

printf 'component\tlevel\tpath\tgap\n' > "$SNAP_DIR/evidence-manifest.tsv"   # 证据清单初始化（Phase 3 → Phase 5 桥接文件）
```

对 Phase 2 判定为 **UPDATED** 的每个组件，按 `references/evidence-guide.md` 的三级证据链定向采集，产出 `$SNAP_DIR/evidence/<component>.md`（原始证据摘录）并在 evidence-manifest.tsv 登记一行（L1/L2/L3 + 缺口说明）。示例命令（真实值替换占位符）：

```bash
# gstack changelog 段提取（L1，维护极好基本可得）
awk '/^## \[<NEW>\]/{f=1} /^## \[<OLD>\]/{f=0} f' "$HOME/.claude/skills/gstack/CHANGELOG.md"

# git 型市场提交明细（L1；网络操作可选化，失败降级并记录）
OLD=$(cat "$SNAP_DIR/mkt-ecc.head"); MKT="$HOME/.claude/plugins/marketplaces/ecc"
git -C "$MKT" fetch --unshallow origin 2>/dev/null || true
git -C "$MKT" log --oneline "$OLD..$(git -C "$MKT" rev-parse HEAD)" 2>/dev/null || true

# specify-cli commit 对（L1/L2；仓库 github/spec-kit 属安装命令参数）
# 旧 commit：$SNAP_DIR/specify-direct_url.json；新 commit：$SNAP_DIR/specify-direct_url-after.json
```

**网络操作全部可选化**：fetch --unshallow、compare API（curl -m 超时、匿名 60/h、只查有变化的组件、请求间 sleep 1、403 即弃）、git ls-remote 失败均降级并记录，绝不因取证失败阻断主流程。

---

## Phase 4：清理 + 健康检查（去重后 H1–H7，功能一项不丢）

| 新编号 | 内容 | 对应 v1.4.0 | 关键约束 |
|---|---|---|---|
| H1 | understand-anything dist 构建补救 | H1 | 保留 pnpm build 补救与残缺版背景注记；输出经 run_cmd 落盘（v1.4.0 `2>&1 >/dev/null` 重定向顺序错误致 stderr 泄漏，已修正） |
| H2 | ui-ux symlink 终态断言 | H2（原 2.6 修复已移至 R1） | 与 R1 共用同一检测逻辑，终态只断言不重复修复 |
| H3 | notifications-go 自愈 + 残缺目录清理 + 激活 exe 检查 | H3 | 位于 Phase 3 之后；缺 exe 目录先跑 install.sh 自愈（2026-08-05 补丁，1.40.1 事故）；不可修复者删除前把目录内 CHANGELOG.md 再拷入 $SNAP（双保险）；残缺版教训注记原文保留 |
| H4 | claude-mem 移出管理范围占位注释 | H4 | 原文保留，**禁止借重构恢复任何 claude-mem 操作** |
| H5 | orphan 抢救复查 + orphan/temp_git 清理 | H5+H7 合并 | 删除前逐个 orphan 目录条件拷贝 CHANGELOG/RELEASE-NOTES/VERSION 到 $SNAP/evidence/orphan/ |
| H6 | ECC 漂移终检 | H6+6.5 验证合并 | 动态阈值（与 cache 实际目录数对比，废魔法数字 20）；旧顶层 rules 清理用 `STALE_RULES_DIRS` 单一变量 |
| H7 | superpowers 副本终态断言 | H8（清理已收敛到 C1） | 只断言"无副本"，发现副本记 FAIL |

```bash
# （通用前置 + 三函数 + manifest_version/active_cache_dir 重放后执行）
STALE_RULES_DIRS="common cpp golang kotlin perl php python swift typescript"

# ===== H1: understand-anything 构建产物补救 =====
# 背景注记（残缺版教训）：daemon 自动更新留下缺 dist/node_modules 的残缺版，需 pnpm build 补救
# 目录从 manifest 激活版本推导（ls -td 实测选中非激活 2.8.2，对错误目录跑 build）
CUR=$(active_cache_dir understand-anything understand-anything understand-anything@understand-anything)
if [ -n "$CUR" ] && [ ! -f "$CUR/packages/core/dist/index.js" ]; then
  run_cmd H1 bash -c "cd '$CUR' && pnpm install && pnpm -r build"
  if test -f "$CUR/packages/core/dist/index.js"; then
    record_result "H1" "PASS" "understand-anything dist 已构建" "plugin/understand-anything@understand-anything" "" "" "REPAIRED" "dist/index.js 存在"
  else
    record_result "H1" "FAIL" "understand-anything 构建失败（见 errors/H1.err）" "plugin/understand-anything@understand-anything" "" "" "FAILED" "dist/index.js 缺失"
  fi
else
  record_result "H1" "PASS" "understand-anything dist 正常" "plugin/understand-anything@understand-anything" "" "" "OK" "无需构建"
fi

# ===== H2: ui-ux symlink 终态断言（原 2.6 修复已移至 R1，此处只断言）=====
UI_SKILL="$HOME/.claude/skills/ui-ux-pro-max"
if [ -d "$UI_SKILL" ]; then
  DEGRADED=0
  for item in scripts data; do
    [ -f "$UI_SKILL/$item" ] && [ ! -d "$UI_SKILL/$item" ] && DEGRADED=1
  done
  [ "$DEGRADED" -eq 0 ] && record_result "H2" "PASS" "ui-ux-pro-max symlink 正常" "fix/ui-ux-symlink" "" "" "OK" "终态断言" \
                        || record_result "H2" "FAIL" "ui-ux-pro-max symlink 仍退化" "fix/ui-ux-symlink" "" "" "FAILED" "终态断言"
else
  record_result "H2" "SKIP" "ui-ux-pro-max 未安装" "fix/ui-ux-symlink" "" "" "NOT_INSTALLED" "-"
fi

# ===== H3: claude-notifications-go 自愈 + 残缺目录清理 + 激活 exe 检查 =====
# 背景注记（残缺版教训）：上游自 1.40.0 起不随包提供 Windows exe（bin/claude-notifications 是 33B darwin 桩）。
# 缺 exe 时先跑 bin/install.sh 自愈；修复失败才判残缺：抢救 CHANGELOG 后删除；激活版本以 installed_plugins.json 为准
NG="$HOME/.claude/plugins/cache/claude-notifications-go/claude-notifications-go"
for v in "$NG"/*/; do
  if [ ! -f "$v/.orphaned_at" ] && [ ! -f "$v/bin/claude-notifications-windows-amd64.exe" ]; then
    bn=$(basename "$v")
    # 自愈优先：跑 install.sh 补装 Windows 二进制（2026-08-05 补丁，1.40.1 事故即以 install.sh 修复）
    if [ -f "$v/bin/install.sh" ]; then
      echo "[$(date '+%H:%M:%S')] [HEAL] [H3] $bn 缺 Windows exe，自动跑 install.sh" >> "$LOG_FILE"
      (cd "$v" && bash bin/install.sh >> "$LOG_FILE" 2>&1)
    fi
    if [ -f "$v/bin/claude-notifications-windows-amd64.exe" ]; then
      record_result "H3-heal" "PASS" "$bn 自愈成功（install.sh 补装 exe）" "plugin/claude-notifications-go@claude-notifications-go" "" "" "REPAIRED" "install.sh 自愈"
      continue
    fi
    # 修复失败 → 残缺目录：双保险删除前再拷一次 CHANGELOG（Phase 3 orphan 抢救可能未覆盖非 orphan 目录）
    if [ -f "$v/CHANGELOG.md" ] && [ ! -f "$SNAP_DIR/evidence/orphan/$bn/CHANGELOG.md" ]; then
      mkdir -p "$SNAP_DIR/evidence/orphan/$bn"
      cp "$v/CHANGELOG.md" "$SNAP_DIR/evidence/orphan/$bn/"
    fi
    rm -rf "$v"
  fi
done
DIR=$(active_cache_dir claude-notifications-go claude-notifications-go claude-notifications-go@claude-notifications-go)
test -f "${DIR}bin/claude-notifications-windows-amd64.exe" \
  && record_result "H3" "PASS" "claude-notifications-go exe 存在" "plugin/claude-notifications-go@claude-notifications-go" "" "" "OK" "exe 检查" \
  || record_result "H3" "FAIL" "claude-notifications-go 无可用 exe" "plugin/claude-notifications-go@claude-notifications-go" "" "" "FAILED" "exe 检查"

# ===== H4: (claude-mem 已移出管理范围，不再检查) =====
# 安全决策占位：claude-mem 完全不碰——不探测、不记录、不检查、无记录行；禁止借重构恢复任何 claude-mem 操作

# ===== H5: orphan 抢救复查 + orphan/temp_git 清理（原 H5+H7 合并）=====
find "$HOME/.claude/plugins/cache" -name ".orphaned_at" 2>/dev/null | while read m; do
  d=$(dirname "$m"); pv=$(basename "$d"); mkdir -p "$SNAP_DIR/evidence/orphan/$pv"
  for f in CHANGELOG.md RELEASE-NOTES.md VERSION package.json; do
    [ -f "$d/$f" ] && [ ! -f "$SNAP_DIR/evidence/orphan/$pv/$f" ] && cp "$d/$f" "$SNAP_DIR/evidence/orphan/$pv/"; done
  rm -rf "$d"
done
rm -rf "$HOME"/.claude/plugins/cache/temp_git_* 2>/dev/null
record_result "H5" "PASS" "orphan + temp_git 已清理（删除前 CHANGELOG 已抢救）" "cleanup/orphan" "" "" "OK" "清理完成"

# ===== H6: ECC 漂移终检（原 H6+6.5 验证合并；动态阈值，废魔法数字 20）=====
ECC_DIR=$(active_cache_dir ecc ecc ecc@ecc)
if [ -n "$ECC_DIR" ]; then
  CACHE_AGENTS=$(ls "$ECC_DIR"/agents/*.md 2>/dev/null | wc -l)
  INSTALLED_AGENTS=$(ls "$HOME"/.claude/agents/*.md 2>/dev/null | wc -l)
  CACHE_RULES=$(ls "$ECC_DIR/rules/" 2>/dev/null | grep -v README | wc -l)
  RULES_N=$(ls "$HOME"/.claude/rules/ecc/ 2>/dev/null | grep -v README | wc -l)
  if [ "$INSTALLED_AGENTS" -ge "$CACHE_AGENTS" ] && [ "$RULES_N" -ge "$CACHE_RULES" ]; then
    record_result "H6" "PASS" "ECC 无漂移 (agents=$INSTALLED_AGENTS/$CACHE_AGENTS rules=$RULES_N/$CACHE_RULES)" "sync/ecc" "" "" "OK" "动态阈值"
  else
    record_result "H6" "FAIL" "ECC 漂移 (cache agents=$CACHE_AGENTS installed=$INSTALLED_AGENTS rules cache=$CACHE_RULES installed=$RULES_N)" "sync/ecc" "" "" "FAILED" "动态阈值"
  fi
  for d in $STALE_RULES_DIRS; do
    [ -d "$HOME/.claude/rules/$d" ] && rm -rf "$HOME/.claude/rules/$d"
  done
else
  record_result "H6" "SKIP" "ECC 未安装" "sync/ecc" "" "" "NOT_INSTALLED" "-"
fi

# ===== H7: superpowers 副本终态断言（原 H8；清理已收敛到 C1，此处只断言）=====
[ -d "$HOME/.claude/skills/superpowers" ] \
  && record_result "H7" "FAIL" "superpowers 用户级副本复现（C1 清理未生效或被重建）" "copy/superpowers" "" "" "FAILED" "终态断言" \
  || record_result "H7" "PASS" "无 superpowers 用户级副本" "copy/superpowers" "" "" "OK" "终态断言"
```

---

## Phase 5：报告生成 + 终端汇总（无条件执行）

### 终端汇总（三态计数从 results.tsv 重算，排除 V- 复核行避免双计；验证失败另从 V- 行并入，不静默）

```bash
# （通用前置重放后执行）
TSV="$SNAP_DIR/results.tsv"
PASS_COUNT=$(awk -F'\t' '$1 !~ /^V-/ && $3=="PASS"' "$TSV" | wc -l)
FAIL_COUNT=$(awk -F'\t' '$1 !~ /^V-/ && $3=="FAIL"' "$TSV" | wc -l)
SKIP_COUNT=$(awk -F'\t' '$1 !~ /^V-/ && $3=="SKIP"' "$TSV" | wc -l)
FAILURES=$(awk -F'\t' '$1 !~ /^V-/ && $3=="FAIL"{printf " %s", $1}' "$TSV")
# 验证失败（命令 exit=0 但功能验证失败 → 动作行 PASS、V- 行 FAIL）：三态完成行口径冻结不变，此处单独并入失败展示
VFAILURES=$(awk -F'\t' '$1 ~ /^V-/ && $3=="FAIL"{printf " %s", $1}' "$TSV")

# ===== 最终汇总表 =====
echo ""
echo "============================================================"
echo "           update-all 执行汇总"
echo "============================================================"
echo ""
echo "  开始时间: $START_TIME"
echo "  结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "  PASS: $PASS_COUNT"
echo "  FAIL: $FAIL_COUNT"
echo "  SKIP: $SKIP_COUNT"
echo ""
if [ -n "$FAILURES" ] || [ -n "$VFAILURES" ]; then
  [ -n "$FAILURES" ] && echo "  失败步骤:$FAILURES"
  [ -n "$VFAILURES" ] && echo "  验证失败步骤(命令 exit=0 但功能验证失败):$VFAILURES"
  echo "  请检查上述失败项并手动修复"
else
  echo "  所有步骤通过 ✅"
fi
echo ""
echo "  日志: ~/.claude/update-all.log"
echo "  提示: 更新完成后需重启 Claude Code daemon 使插件生效"
echo "  提示: 更新前已运行的会话需重启或 /reload-plugins 才会加载新插件版本"
echo "============================================================"

echo "[$(date '+%H:%M:%S')] ===== update-all 完成: PASS=$PASS_COUNT FAIL=$FAIL_COUNT SKIP=$SKIP_COUNT =====" >> "$LOG_FILE"
[ -n "$FAILURES" ] && echo "[$(date '+%H:%M:%S')] 失败步骤:$FAILURES" >> "$LOG_FILE"
[ -n "$VFAILURES" ] && echo "[$(date '+%H:%M:%S')] 验证失败步骤(V- 行口径):$VFAILURES" >> "$LOG_FILE"
# 富状态分布行（v2 新增，完成行结构不变，其后追加；与三态计数同口径排除 V- 行，避免 class 回填导致双计）
DIST=$(awk -F'\t' 'NR>1 && $1 !~ /^V-/ && $4!="-"{c[$4]++} END{s=""; for(k in c) s=s k"="c[k]" "; print s}' "$TSV")
echo "[$(date '+%H:%M:%S')] 状态分布: $DIST" >> "$LOG_FILE"
echo "报告目录: $REPORT_DIR"
```

### 更新报告生成（Claude 用 Write 工具，无条件执行）

1. **落点**：`REPORT_DIR="${UPDATE_ALL_REPORT_DIR:-$PROJECT_ROOT/doc/update-reports}"`（环境变量可覆盖 + git 根动态探测，不硬编码；本项目即 `D:/mydoc/workskill/doc/update-reports/`）。Phase 0 已写入 `$SNAP_DIR/meta`（cwd 跨调用重置，必须持久化绝对路径）；执行时 `mkdir -p`。
2. **命名**：`更新报告-YYYYMMDD-HHmm.md`，时间戳取 START_TIME，精确到分钟，**禁用冒号**（Windows 文件名 9 个非法字符）；同日同分钟撞名追加 `-2`。
3. **无条件自动生成**：紧跟汇总表之后执行，无需确认；全部 UP_TO_DATE 也生成（报告价值在留痕与基线）。不复用 `doc/claude-code/`（那是 CLI changelog 分析系列，语义不同）；报告开头注明两系列区别并引用其最新一篇，§7 后续待办交叉引用。
4. **撰写**：Claude 用 **Write 工具**落盘（长中文内容不走 bash heredoc，规避 Windows Git Bash 编码与引号风险）。数据源 = results.tsv + versions-before.env + evidence-manifest.tsv + evidence/ + errors/ + update-all.log 尾部，按 `references/report-template.md` 撰写（执行前 Read 该模板）。
5. **行数校验**：生成后 `wc -l` 校验 ≤1000 行，超限拆 `更新报告-<同时间戳>-附录-证据摘录.md`（主报告保留 §1–§7，证据明细入附录）。
6. **异常不静默**：报告生成失败/证据缺失必须记入 LOG_FILE 并在口头汇报中说明。
7. **收尾口头汇报**（模板外硬性动作）：报告写完后向用户汇报四件事——总体结论、版本变化最大的 3 项、失败数与待办、报告绝对路径。

---

## 健壮性与 Windows 边界规则

1. **部分失败不阻断**：禁用 `set -e`；每命令立即 `rc=$?` 捕获（不用管道末端取码）；失败→FAILED + stderr 落盘，继续下一组件；Phase 5 报告不依赖任何组件成功。
2. **版本解析降级链**：所有探测 one-liner 以 `2>/dev/null || true` 收尾；空输出→`unknown` + note 强制写原因；playwright-cli/claude 用行首锚定 `grep -oE '^[0-9]+\.[0-9]+\.[0-9]+' | head -1`。
3. **git 类型判定兜底**：市场循环内先 `git -C "$d" rev-parse --git-dir` 判型，非 git 查 `.gcs-sha`，两者皆非记 unknown（未来新市场类型不炸流程）。
4. **路径坑**：一切 cd 改子 shell（gstack setup、ECC install.sh 均 `bash -c 'cd ... && ...'`）；$SNAP 路径无空格。
5. **幂等**：Phase 0 纯只读；$SNAP 分钟级命名+冲突后缀；报告文件名冲突后缀；清理只动本技能自产物（过期快照）与既定残留（orphan/temp_git/副本）。
6. **黑名单联动**：黑名单表、Phase 1 注释行、报告 §1 单列三处同步；claude-mem 完全不碰决策原文保留。

---

## 故障排查

### specify-cli 报错 `ModuleNotFoundError: No module named 'specify_cli'`

**原因**：`~/.local/bin/specify.exe` 是残留文件，实际 Python 包未安装。

**修复**：
```bash
rm -f ~/.local/bin/specify.exe
uv tool install specify-cli --from "git+https://github.com/github/spec-kit.git" --reinstall
```

### claude plugins update 报 "not found"

**原因**：上游市场已重构，插件名称变更。

**修复**：运行 `claude plugins list` 确认新名称后重新安装。

### gstack 更新后命令不可用

**原因**：setup 脚本未正确执行。

**修复**：
```bash
cd ~/.claude/skills/gstack && ./setup
```

### 激活版本判断错误（v2.0.0 新增）

**原因**：用 `ls -td`（mtime）或 `sort -V` 判定激活版本。实测 `ls -td` 对 understand-anything 选中 2.8.2（实际激活 2.9.4，两目录 mtime 仅差 46 秒）、对 notifications-go 选中残缺 1.40.1（实际激活 1.39.3）；`sort -V` 同样会选中残缺版。

**修复**：激活版本一律查 `~/.claude/plugins/installed_plugins.json`（awk -F'"' 一行式见 `references/version-commands.md` §5）；缓存目录探测只回答"磁盘上有哪些版本"。

### mattpocock 探测类故障（v2.1.0 已消除）

v2.1.0 起 mattpocock 走插件（`mattpocock-skills@mattpocock`），激活版本以 `installed_plugins.json` 为准，原「npx skills 探测返回 0 个文件」「lock 漂移判据」等坑随 S1 移除而消失。历史背景：`<项目>/.claude/skills/<skill>` 曾是指向 `.agents/skills/<skill>` 的 symlink，find 默认不跟随（2026-08-05 实测）。

### V- 复核 FAILED 但更新命令 exit 0（v2.0.0 新增）

**原因**：版本已变但功能验证失败。常见：版本目录是空壳（understand-anything 2.8.2 式，0 文件）、残缺版缺文件（notifications-go 1.40.0 式缺 Windows exe）、探测命令与组件不匹配。

**修复**：核对 manifest 版本与缓存目录 `find <dir> -type f | head -1` 是否非空；查 `$SNAP_DIR/errors/<step>.err` 与 out/<step>.log 原始输出。

### 报告缺失或执行中断后的补写路径（v2.0.0 新增）

**原因**：Phase 5 中断、Write 失败或会话提前结束。

**修复**：全部数据都在 `$SNAP_DIR`（路径：`cat ~/.claude/update-evidence/.latest`）——results.tsv、versions-before.env、evidence/、evidence-manifest.tsv、errors/、out/、meta。按 `references/report-template.md` 手动补写报告，文件名沿用 meta 中 START_TIME 的时间戳。

---

## 注意事项

- 更新完成后需**重启 Claude Code daemon** 使插件生效（终端汇总中的提示与此条为同一事，交叉引用）
- **更新前已运行的会话**不会自动加载新插件版本：需重启对应会话或在会话内 `/reload-plugins`（旧版本缓存目录在 Phase 4 清理，钉着旧路径的会话会丢失插件技能——2026-08-05 实测 superpowers/understand-anything 从会话中消失）
- `specify-cli` 始终从 `github/spec-kit` 主分支安装最新开发版
- `everything-claude-code` 已重构为 `ecc@ecc`，旧名不可用
- 每个步骤的验证失败不会中断整体流程，但最终汇总与报告 §5/§6 会显示所有问题

---

## references 文件索引

本技能引用的 references 均为**本技能目录（本 SKILL.md 所在目录）的相对路径**；执行时以 SKILL.md 自身路径推出绝对路径后 Read（本技能位于项目 `.claude/skills/update-all/`，即 `<项目>/.claude/skills/update-all/references/<文件>`）。

| 文件 | 内容 | 使用时机 |
|---|---|---|
| `references/version-commands.md` | 登记表全部探测 one-liner + 2026-08-05 实测样例输出 + caveats | Phase 0/Phase 2 探测、故障排查 |
| `references/evidence-guide.md` | 三级证据链表 + orphan 抢救 + 固定降级句 + 举例白名单 + 网络可选化规则 | Phase 3 证据采集 |
| `references/plugin-pitfalls.md` | 插件 5 大坑（清单漏更新/死条目/市场撞名/commands 不随插件分发/安装≠可见）+ 检测与处置命令 | Phase 2 对账 WARN 处置、任何插件安装任务执行前 |
| `references/report-template.md` | 报告 7 节完整模板 + 写作红线 + 落点命名与拆分规则 | Phase 5 撰写报告 |

references 只放 Claude 阅读型指引；可执行 bash 代码一律留在本文件，执行时按需 Read。
