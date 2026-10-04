# 版本探测命令手册（update-all v2.0.0）

> 本文件是 SKILL.md 组件登记表的探测命令完整版 + 实测样例输出 + caveats。
> **全部命令于 2026-08-05 在本机 Git Bash（Windows 11）实际执行并复验**，不得臆造未验证的命令。
> 运行环境事实：本机**无 jq**，一切 JSON 解析用 `awk -F'"'` 实测方案；探测失败一律降级 `unknown` 并在 note 写"版本解析失败:<命令>"，不中断、不臆测填补。

---

## 1. npm 全局工具

### N1 html-to-react-components

```bash
npm list -g html-to-react-components --depth=0 2>/dev/null | sed -n 's/.*html-to-react-components@\([^ ]*\).*/\1/p'
```

样例输出：

```
C:\Users\wuyan\AppData\Roaming\npm
└── html-to-react-components@1.6.6
→ 解析结果: 1.6.6
```

caveats：
- 包缺失时 npm exit=1 且输出 `└── (empty)`，sed 输出为空（可作未安装判据）。
- `[^ ]*` 会自动截断 npm 可能附加的 ` -> path` 后缀。
- 全量扫描变体（同样实测通过）：`npm list -g --depth=0 | awk -F'@' '/html-to-react-components@/{print $NF}'`。

### N2 @playwright/cli

```bash
npm list -g @playwright/cli --depth=0 2>/dev/null | sed -n 's/.*@playwright\/cli@\([^ ]*\).*/\1/p'
```

样例输出：

```
C:\Users\wuyan\AppData\Roaming\npm
└── @playwright/cli@0.1.17
→ 解析结果: 0.1.17
```

caveats：
- scoped 包版本在最后一个 @ 之后，sed 按包全名锚定最稳。
- 全量扫描变体实测通过：`npm list -g --depth=0 | awk -F'@' '/@playwright\/cli@/{print $NF}'` → 0.1.17（awk -F'@' 取 $NF 对 scoped/unscoped 都成立）。

---

## 2. playwright-cli 工具版本

```bash
playwright-cli --version 2>&1 | grep -oE '^[0-9]+\.[0-9]+\.[0-9]+' | head -1
```

样例输出：

```
stdout: 0.1.17（exit=0）
stderr: Unicode 警告框 'The playwright-cli skill at .claude\skills\playwright-cli does not match the tool version. Run playwright-cli install --skills'
```

caveats：
- 实测版本号先打印在 stdout 且为纯版本号，exit=0。
- 警告框行以 ╔/║ 开头、断言行以文字开头，均非数字开头，故**行首锚定 grep（`^[0-9]`）对 2>&1 合并流安全**。
- 纯 stdout 变体同样验证：`playwright-cli --version 2>/dev/null | grep -oE '^[0-9]+\.[0-9]+\.[0-9]+'`。
- **禁止用 grep "version"**（输出不含该字样）。此为 v1.4.0 步骤 3 原文保留教训：`--version` 只输出纯版本号如 0.1.15，不含 "version" 字样。
- stderr 警告框本身可作为"技能需重装"的信号源（任意 cwd 都出现，含 $HOME）。

---

## 3. specify-cli（uv tool，git 安装）

### 显示版本串

```bash
uv tool list 2>/dev/null | sed -n 's/^specify-cli v\([^ ]*\).*/\1/p'
```

样例输出：

```
specify-cli v0.15.3.dev0
- specify
→ 解析结果: 0.15.3.dev0
```

caveats：
- 版本带 v 前缀，sed 变体剥掉 v；`awk '/^specify-cli /{print $2}'` 保留 v（两种均实测通过）。
- 第二行 `- specify` 是暴露的命令名，`^specify-cli` 锚定不会误匹配。未安装时输出空。
- dev 版本号（v0.15.3.dev0）说明从 git main 安装，非正式 release；`--reinstall` 每次版本串恒为 dev，**只有 commit_id 能区分更新前后**。

### 对比键 commit_id（唯一精确源）

venv 内无 .git（uv 从 git 构建 wheel 后不留仓库），dist-info 内 `direct_url.json` 是唯一精确源：

```bash
DU=$(ls "$APPDATA"/uv/tools/specify-cli/Lib/site-packages/specify_cli-*.dist-info/direct_url.json 2>/dev/null | head -1)
grep -o '"commit_id": *"[0-9a-f]*"' "$DU" | sed 's/.*"\([0-9a-f]*\)"$/\1/'
```

实测值：`03d71b336387b57b8dfb7d79777a6b65425a801c`（2026-08-05）。

---

## 4. claude CLI（K0 黑名单，只读）

```bash
claude --version 2>/dev/null | grep -oE '^[0-9]+\.[0-9]+\.[0-9]+' | head -1
```

样例输出：`2.1.202 (Claude Code)` → 解析结果 `2.1.202`。输出单行、exit=0、格式稳定。
注意本机 @anthropic-ai/claude-code 也在 npm 全局列表中（2.1.202），两条探测路径结果一致。

---

## 5. 插件激活版本（唯一权威源）

**重大事实**：`~/.claude/plugins/installed_plugins.json` 记录每个激活插件的 version + installPath + gitCommitSha，是判定"激活版本"的**唯一权威来源**。

```bash
awk -F'"' '/@/ && /: \[/{key=$2} /"version":/{if($4!="") print key"="$4}' ~/.claude/plugins/installed_plugins.json
```

样例输出（2026-08-05）：

```
claude-hud@claude-hud=0.6.0
claude-mem@thedotmack=13.10.2
claude-notifications-go@claude-notifications-go=1.39.3
ecc@ecc=2.1.0
jobs-to-be-done@pm-skills=99710188c134
paddle@claude-community=72e6fdf6ec31-ab82885f
superpowers@claude-plugins-official=6.2.0
ui-ux-pro-max@ui-ux-pro-max-skill=2.11.0
understand-anything@understand-anything=2.9.4
```

单插件查询变体：

```bash
awk -F'"' '/@/ && /: \[/{key=$2} /"version":/{if($4!="" && key=="ecc@ecc") print $4}' ~/.claude/plugins/installed_plugins.json
```

caveats：
- awk 解析实测可靠（$4 判空可跳过顶层 `"version": 2`）。
- Version 可能非 semver（git SHA `99710188c134`、repo@commit 形式 `72e6fdf6ec31-ab82885f`）。
- 查不存在的插件返回空。

### ⚠️ 禁止用 ls -td / sort -V 判定激活版本（实测双双选错）

- `ls -td`（mtime 排序）：understand-anything 有 2.8.2 与 2.9.4 两个缓存目录，mtime 最新是 2.8.2 但激活是 2.9.4（两目录 mtime 仅差 46 秒）；claude-notifications-go 有 1.39.3 与 1.40.1，mtime 最新 1.40.1 但激活是 1.39.3（1.40.1 缺 Windows exe，bin/ 里只有 Unix 二进制）。
- `sort -V` 取最大版本同样错（notifications-go 会选残缺 1.40.1）。
- **缓存目录探测只回答"磁盘上有哪些版本"**：`ls ~/.claude/plugins/cache/<mkt>/<plg>/`，目录名即版本字符串。排除 orphan 的"磁盘最新版"一行式（仅限回答磁盘问题）：

```bash
UA=~/.claude/plugins/cache/<mkt>/<plg>
ls -td $UA/*/ 2>/dev/null | while read d; do [ -f "$d/.orphaned_at" ] || { echo "$d"; break; }; done
```

### 辅助：claude plugins list（状态核对用，不作版本权威）

```bash
claude plugins list 2>/dev/null | awk '$1=="❯"{name=$2} $1=="Version:"{print name"="$2}'
```

结构：`  ❯ 名@市场` 行后跟 `Version:`/`Scope:`/`Status:` 行；输出无 ANSI 转义仅 Unicode；有两个 section（Installed plugins 与 Skills-directory plugins，后者多一行 Path:）。Status 行含 enabled/disabled 实测状态（本机 claude-mem、ecc 当前 disabled）。

---

## 6. 市场 HEAD / gcs-sha

```bash
for d in ~/.claude/plugins/marketplaces/*/; do
  n=$(basename "$d")
  if git -C "$d" rev-parse --git-dir >/dev/null 2>&1; then
    echo "$n=$(git -C "$d" rev-parse HEAD)"
  elif [ -f "$d/.gcs-sha" ]; then
    echo "$n=gcs-sha:$(cat "$d/.gcs-sha")"
  else
    echo "$n=unknown"
  fi
done
```

样例输出（2026-08-05，短 SHA 展示）：

```
claude-community=9247660 / claude-hud=e39bafc / claude-notifications-go=74b9fba
claude-plugins-official=gcs-sha:60f5e338b2aa / ecc=f1fec0e / pm-skills=9971018
thedotmack=f85bb28 / ui-ux-pro-max-skill=4d140cf / understand-anything=fe8c5bc
```

caveats：
- 9 个市场中 8 个是有效 git clone（全部 branch=main）；claude-plugins-official 不是 git 仓库（git rev-parse exit=128），是 GCS 快照下载，版本标识是 `.gcs-sha` 文件（40 字节完整 SHA），仅该市场有此文件。
- **Phase 0 快照必须存完整 SHA**（GitHub compare API 需要），展示可截短。
- `claude plugins marketplace list` 只给 GitHub 源（如 `GitHub (jarrodwatts/claude-hud)`）无版本/hash，实测确认；`known_marketplaces.json` 另含各市场 source repo + lastUpdated ISO 时间戳。
- 先判型再探测（新市场类型不炸流程只降级 unknown）。

---

## 7. gstack

```bash
[ -d ~/.claude/skills/gstack ] && cat ~/.claude/skills/gstack/VERSION
git -C ~/.claude/skills/gstack rev-parse --short HEAD 2>/dev/null
# .bak 目录同法（赶在 G1 删它之前）
```

样例输出：VERSION=1.60.1.0，HEAD=a325940（branch=main，remote=garrytan/gstack）；gstack.bak: VERSION=1.58.5.0，HEAD=11de390。

caveats：
- 双重版本标识：VERSION 文件与 package.json 一致（`grep '"version"' ~/.claude/skills/gstack/package.json` 亦可）。
- 目录不存在时 cat VERSION 报错，**探测前需 `[ -d ]` 判空**。
- **跨 clone git 对比不可行**：gstack 与 gstack.bak 是两个独立 depth-1 clone，对象库不相交（实测 `git log OLD..NEW` 跨目录 fatal/0 条）。本地 git log 路线需先 `git -C ~/.claude/skills/gstack fetch --unshallow origin`（联网+写 .git），列为可选。

---

## 8. mattpocock skills（v2.1.0 起为插件，无独立探测）

v2.1.0 起以 `mattpocock-skills@mattpocock` 插件安装（上游官方 marketplace：github.com/mattpocock/skills 的 `.claude-plugin/marketplace.json`，插件 version semver 形态如 1.2.3）。激活版本与更新后复核**并入 P* 插件通用流程**（§5 awk 解析 installed_plugins.json + cache 版本目录非空壳校验），无独立探测命令。

**历史背景（v2.0.0 及之前为 npx skills 项目级安装时的坑，现 S1 已移除，仅存档）**：实体文件在 `<项目>/.agents/skills/<skill>/`，`<项目>/.claude/skills/<skill>` 是 symlink，find 默认不跟随返回 0 文件（2026-08-05 实测）；skills-lock.json 的 computedHash 与本地 sha256 不相等（语义不明），曾禁止用作漂移判据。

---

## 9. 2026-08-05 实测版本快照（供下次运行对比基线）

```
claude 2.1.202 / @playwright/cli 0.1.17 / playwright-cli 0.1.17
html-to-react-components 1.6.6 / specify-cli 0.15.3.dev0 (commit 03d71b33)
gstack 1.60.1.0 (a325940) / gstack.bak 1.58.5.0 (11de390)
插件: claude-hud 0.6.0、ecc 2.1.0、superpowers 6.2.0、ui-ux-pro-max 2.11.0、
      understand-anything 2.9.4、claude-mem 13.10.2(disabled，不在管理范围)、
      claude-notifications-go 1.39.3、jobs-to-be-done 99710188c134、
      paddle 72e6fdf6ec31-ab82885f、humanizer(skills-dir) 2.9.1
市场 HEAD（短）: claude-community=9247660 claude-hud=e39bafc claude-notifications-go=74b9fba
      ecc=f1fec0e pm-skills=9971018 thedotmack=f85bb28
      ui-ux-pro-max-skill=4d140cf understand-anything=fe8c5bc
      claude-plugins-official=gcs-sha:60f5e338b2aa
```

注：全程只读探测（唯一网络访问是只读的 git ls-remote）；claude plugins list 显示 ecc 与 claude-mem 当前 Status=disabled。
