# 功能差异证据采集指引（update-all v2.0.0 · Phase 3）

> 时机铁律：**Phase 3 必须完整位于 Phase 2 完成后、Phase 4 任何 rm -rf 之前**。违反即永久丢失证据。
> 对象：仅对 Phase 2 判定为 UPDATED 的组件采集；UP_TO_DATE/BLACKLIST/NOT_INSTALLED 不采集。
> 产出：`$SNAP_DIR/evidence/<component>.md`（原始证据摘录，超长截断并存全文路径）+ `$SNAP_DIR/evidence-manifest.tsv`（桥接文件，Phase 5 撰写报告 §4 的唯一索引）。

---

## 1. orphan 抢救（Phase 3 第一步，H5 删除前最后窗口）

现存实例教训：claude-notifications-go 1.40.1 带 `.orphaned_at` 且内含完整 CHANGELOG.md（1.39.3→1.40.1 证据），清理一跑即失。

```bash
find ~/.claude/plugins/cache -name ".orphaned_at" 2>/dev/null | while read m; do
  d=$(dirname "$m"); pv=$(basename "$d")
  mkdir -p "$SNAP_DIR/evidence/orphan/$pv"
  for f in CHANGELOG.md RELEASE-NOTES.md VERSION package.json; do
    [ -f "$d/$f" ] && cp "$d/$f" "$SNAP_DIR/evidence/orphan/$pv/"
  done
done
```

Phase 4 的 H3/H5 删除前再做一次条件拷贝（未快照才拷），双保险后删除无信息损失。

---

## 2. 三级证据链（L1 首选 → L2 降级 → L3 固定降级句）

| 组件类型 | L1 首选 | L2 降级 | L3 固定降级句（报告必须如实写，禁止编造） |
|---|---|---|---|
| npm 包 | 包内 CHANGELOG.md from→to 段：`$(npm root -g)/<pkg>/CHANGELOG.md` | `npm view <pkg> time --json` 版本时间线 + GitHub compare | 「无变更明细证据：仅版本 X→Y，上游未提供 changelog」 |
| git 市场 | `fetch --unshallow` 后 `git log --oneline OLD..NEW` | GitHub compare API | 「市场已刷新（HEAD A→B），提交明细获取失败（原因）」 |
| GCS 市场 | marketplace.json diff（各插件版本号变化） | 下沉插件层证据 | 「市场快照已更新（gcs-sha A→B），无更细粒度」 |
| 插件 | 新版 cache 目录 CHANGELOG.md/RELEASE-NOTES.md 的 from→to 段（新版文件含历史段） | 新旧目录并存时文件清单 diff → manifest gitCommitSha compare API | 「无 changelog 且旧目录已删，仅版本变迁 X→Y」 |
| gstack | CHANGELOG.md awk 段提取（维护极好，L1 基本可得） | VERSION+HEAD 对比 / unshallow 后 git log | 仅 VERSION 对 |
| specify-cli | commit_id 对 → compare API 提交列表 | 仅 commit_id A→B | 「无细粒度 changelog，仅 commit 范围，详见 github/spec-kit compare 链接」 |
| playwright skills | Phase 0 旧装技能副本 vs 新包内技能 `diff -r` | — | 仅 hash 变化 |
| mattpocock skills | lock diff 定位变更技能 → 变更技能 Phase 0 快照 `diff -r` | `git ls-remote` 上游 HEAD 仅证"上游动了" | 「技能 <名> 内容已变更，无版本号，diff 见附录」 |

已知证据质量实测（2026-08-05）：
- ecc 有 CHANGELOG.md+VERSION（Keep-a-Changelog 风格、含历史版本）；superpowers 有 RELEASE-NOTES.md（51 个 `## vX` 段，新版目录即含旧版本说明）；claude-notifications-go 有高质量 CHANGELOG.md。
- understand-anything / ui-ux-pro-max 无 changelog；html-to-react-components CHANGELOG 停在 2019-01（项目休眠）；@playwright/cli 无 CHANGELOG 只有 README。

---

## 3. 常用采集命令

### 3.1 插件 changelog 段提取（L1）

```bash
# 新版 cache 目录（激活版本目录从 manifest 版本推得）
CACHE=~/.claude/plugins/cache/<mkt>/<plg>/<new-ver>
# Keep-a-Changelog 风格：提取 old→new 之间版本段（按实际标题格式调整）
awk '/^## \[?<NEW>/{f=1} /^## \[?<OLD>/{f=0} f' "$CACHE/CHANGELOG.md"
# superpowers 类：RELEASE-NOTES.md 的 ## v6.2.0 段
awk '/^## v<NEW>/{f=1} /^## v<OLD>/{f=0} f' "$CACHE/RELEASE-NOTES.md"
```

### 3.2 新旧目录文件清单 diff（L2，新旧目录并存时）

```bash
diff <(cd ~/.claude/plugins/cache/<mkt>/<p>/<old> && find . -type f | sort) \
     <(cd ~/.claude/plugins/cache/<mkt>/<p>/<new> && find . -type f | sort)
```

### 3.3 git 市场提交明细（L1）

```bash
OLD=$(cat "$SNAP_DIR/mkt-<名>.head")
MKT=~/.claude/plugins/marketplaces/<名>
git -C "$MKT" fetch --unshallow origin 2>/dev/null || true   # 浅克隆必须补历史；网络操作，失败容忍并记录
git -C "$MKT" log --oneline "$OLD..$(git -C "$MKT" rev-parse HEAD)" 2>/dev/null || true
```

注意：`marketplace update` = 删除+重克隆，reflog 无旧 HEAD，Phase 0 快照是唯一旧 HEAD 来源。

### 3.4 GitHub compare API（L2 降级；本机无 gh CLI、无 jq，用 curl + grep/sed）

```bash
# 仓库名动态解析，禁止硬编码：
# - git 市场：从 $SNAP_DIR/marketplace-list.txt 的 "GitHub (<owner>/<repo>)" 行解析
# - 插件：从对应市场的 remote 解析（git -C <市场目录> remote get-url origin）
# - specify-cli：github/spec-kit、gstack：garrytan/gstack 属安装命令参数，允许
REPO="<owner>/<repo>"   # 动态解析所得
curl -s -m 15 "https://api.github.com/repos/$REPO/compare/$OLD...$NEW" \
  | grep -o '"message": *"[^"]*"' | sed 's/^"message": *"//; s/"$//' | head -50
```

> ⚠️ GitHub API 实际返回 `"message": "..."`（冒号后带空格），旧模式 `'"message":"..."'` 实测 0 匹配导致 L2 静默空结果；`"message": *` 兼容冒号后有无空格。caveat：commit message 含 `\"` 转义引号时 `[^"]*` 会提前截断，可接受（截断结果仍是有效证据，需要时在 manifest gap 列注明）。

约束（全部必须遵守）：
- 匿名限速 60 次/h：**只查 HEAD/版本有变化的组件**，请求间 `sleep 1`，403/超限即弃并记 L3。
- 大跨度 >250 commits 会截断（per_page 上限），报告须注明"compare 结果可能被截断"。
- `-m 15` 超时必带；失败降级并记录，绝不因取证失败阻断主流程。

### 3.5 npm 时间线（L2）

```bash
npm view @playwright/cli time --json   # 只给版本发布时间，给不了变更内容
```

### 3.6 playwright / mattpocock skills diff（L1）

```bash
# playwright：Phase 0 旧装副本 vs 新包内权威技能
diff -r "$SNAP_DIR/playwright-installed-skills/user" "$(npm root -g)/@playwright/cli/skills/playwright-cli"
# mattpocock：先 lock diff 定位变更技能，再对变更技能做快照 diff
diff "$SNAP_DIR/skills-lock.json" "$PROJECT_ROOT/skills-lock.json"
diff -r "$SNAP_DIR/mattpocock-skills-before/<skill>" "$PROJECT_ROOT/.agents/skills/<skill>"
```

---

## 4. evidence-manifest.tsv 格式

TAB 分隔，表头固定：

```
component	level	path	gap
```

- `component`：登记表规范名（如 `plugin/superpowers@claude-plugins-official`）。
- `level`：L1/L2/L3（与上表对应）。
- `path`：证据文件绝对路径（L3 写 `-`）。
- `gap`：缺口说明（L1 写 `-`；L2/L3 写缺失内容与原因）。

Phase 5 撰写报告 §4 时逐行读取：**每条功能论断必须引用 level 为 L1/L2 的证据路径**。

---

## 5. 报告撰写红线（禁止臆测）

1. 每条功能论断必须引用证据文件路径或命令输出，引用格式如"（证据：`$SNAP/evidence/orphan/…/CHANGELOG.md` [2.1.0] 段）"。
2. 证据缺失（L3）时用 §2 固定降级句，**禁止凭训练记忆编造 changelog**。
3. **举例来源白名单**：用法举例只能从证据文件中取出——
   - 新增技能的 SKILL.md frontmatter description → 触发语示例；
   - 新增 agents/*.md → agent 名+用途；
   - 新增 rules 文件 → 生效路径；
   - changelog Added/Fixed 条目 → 结合本机场景一句话。
   证据只有名称没有用法时写「用法待验证」；找不到对应证据写「无新增可举例项」。
4. 重大行为变化（影响黑名单/--settings/daemon 的）用 ★★ 标注，判断依据必须写进报告；无实质新功能的组件一句话带过，禁止罗列 changelog 充数。

---

## 6. 网络操作全部可选化

`fetch --unshallow`、compare API、`git ls-remote` 均 `|| true` + 超时收尾，失败降级并记录（写 manifest 的 gap 列 + LOG_FILE WARN 行），绝不因取证失败阻断主流程。
