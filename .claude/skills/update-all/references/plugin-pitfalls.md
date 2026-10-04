# 插件防坑清单（plugin-pitfalls）

> 来源：2026-09-18 pm-skills/mattpocock 插件事件实测教训。update-all Phase 2 对账块已内置坑 1/2/6 的自动检测；坑 3/4/5 属结构性事实，安装类任务执行前人工过一遍。完整事件记录见项目 `doc/claude-code/插件安装与迁移记录.md`。

## 坑 1：新装插件不在 update-all 更新清单（静默漏更新）

**现象**：手动 `claude plugins install` 新插件后，update-all 的 `PLUGINS_TO_UPDATE` 静态清单不含它，每轮更新静默跳过（本次实测人工补救两次：9→15→36）。

**检测（已固化在 Phase 2 对账块）**：installed_plugins.json 全量 key vs `$SNAP_DIR/plugins.list` 反向对比，清单外已装插件记 WARN。

**处置**：把新插件追加进 SKILL.md 的 `PLUGINS_TO_UPDATE` 与登记表 P* 行，两处同步改。

## 坑 2：enabledPlugins 死条目（启用 ≠ 安装）

**现象**：settings.json 的 enabledPlugins 有 `true` 条目，但 installed_plugins.json 无记录、cache 无目录——看似启用实则从未装上（本次 8 个 pm-* 残留数月）。

**检测（已固化在 Phase 2 对账块）**：enabledPlugins key 集合 − installed_plugins.json key 集合 = 死条目，记 WARN 并给出清理命令（编辑 settings.json 删行，改前备份）。

**处置**：删死条目；若本意要装，先确认市场存在该插件名再 install。

## 坑 3：市场同名撞车（致命且无警告）

**现象**：两个 GitHub 仓库的 `.claude-plugin/marketplace.json` 里 `"name"` 相同（如 phuryn/pm-skills 与 deanpeters/Product-Manager-Skills 都叫 `pm-skills`）。本机 `known_marketplaces.json` 该名字只指向一个 repo，另一仓库的插件**永远装不上且无任何报错**（install 报 "not found" 或直接装错市场）。

**检测**：`claude plugins marketplace list` 看市场指向的 repo；对不上预期来源即撞名。

**处置**：两者只能占一个名字——`claude plugins marketplace remove <名>` 后 add 另一个；换源前先把旧市场插件的处理想清楚。

## 坑 4：commands/ 目录不随插件分发

**现象**：部分仓库（实例：deanpeters v0.84，77 个单技能插件）把斜杠命令放在仓库 `commands/` 目录，但 marketplace.json 中**没有任何插件的 source 指向它**——装满全部插件也敲不出命令。

**检测**：`grep '"source"' <市场repo>/.claude-plugin/marketplace.json` 是否有指向仓库根或 commands 的插件。

**处置**：手动复制 `commands/*.md` 到 `~/.claude/commands/`（用户级）或 `<项目>/.claude/commands/`（项目级）；注意命令 `uses:` 引用的技能插件需另行安装（本次补装 21 个）。上游重构 commands 后需手动重拷（此类文件不在 update-all 更新范围）。

## 坑 5：安装成功 ≠ 会话可见

**现象**：install exit 0、manifest/cache 全健康，但当前会话敲不出新技能/命令——插件组件在**会话启动时**快照加载，运行中的会话不热加载。

**处置**：会话内 `/reload-plugins`（实测立即生效，输出 Reloaded: N plugins · N skills…）或重启 daemon。update-all 报告"需重启生效"提示的机制依据即此。

## 坑 6：文档漂移（插件版本变化 → 周边文档静默过期）

**现象**：插件更新/迁移只改组件，不改引用它的文档。文档里的版本号、技能数量、技能名、安装方式全部静默过期，无任何报错（实例：mattpocock 插件化 v1.2.3 后，Obsidian 最佳实践文档仍写 29 技能 / npx 安装 / 旧技能名 to-prd、diagnose、caveman、zoom-out，2026-09-18 人工发现后全量重写）。

**检测（已固化在 Phase 2 对账块，v2.3.0）**：本轮有插件版本变化（from≠to）→ WARN 文档漂移预警，列出变化插件清单。

**处置**：人工核对并同步文档。取证以插件缓存内 SKILL.md / plugin.json 为权威源，GitHub README / CHANGELOG 交叉核验；技能改名必须建"旧名→新名"映射表，场景链/速查表逐名核对。

**本机已知引用插件版本/技能名的文档（变更后逐一核对）**：
- 项目 `doc/claude-code/插件安装与迁移记录.md`（追加事件记录）
- Obsidian `D:\mydoc\Obsidian\0-AI编程\产品skill\`：1-mattpocock-skills-best-practices.md（2026-09-18 已同步至 v1.2.3）、2-pms.md（基于 pm-skills v0.79，待同步）、pm-skills-best-practices.md（待同步）、three-plugins-comparison.md（待同步）

## 坑 7：命令副本脱离插件版本管理（同名双套行为）

**现象**：手动把插件仓库的 commands/*.md 复制到 `~/.claude/commands/`（典型：ECC 手动安装/复制），形成脱离版本管理的副本。后果：(1) 插件升级不同步副本，副本分叉漂移（实例：react-test 用户副本仍是旧版相对路径 `../rules/react/`，插件版已修正为 `../rules/ecc/react/`）；(2) 裸名命中副本、`/ecc:` 前缀命中插件版，同名两套行为；(3) 实测 94 份副本中 93 份与插件版 MD5 完全一致，纯冗余。

**检测（已固化在 Phase 2 对账块，v2.4.0）**：用户级 `~/.claude/commands/*.md` 与已装插件 `cache/*/*/*/commands` 递归命令名求交集 → WARN 同名双套。注意只取插件版本目录下的真实 commands（插件缓存里 `docs/*/commands`、`node_modules` 等同名目录是文档副本，会干扰统计）。

**处置**：与插件版 hash 一致的副本直接移除（先备份）；内容有差异的先判断是"用户自定义"还是"旧版残留"（对比插件版修正记录），旧版残留同样移除；确属用户自定义的保留（有意覆盖）。区分两种复制：**有意复制**（上游命令不随插件分发，须手动复制——坑 4 的正路，如 pm-skills 6 命令）与**无意冗余副本**（插件已有等价物，应删用 `/插件名:` 前缀调用）。

**清理实例**：2026-09-18 移除 94 个 ECC 衍生副本（备份于 `~/.claude/commands-backup-ecc-20260918/`，含 MANIFEST.md 对照表），详见项目 `doc/claude-code/插件安装与迁移记录.md`。

**退役命令副本（坑 7b，v2.4.0 起自动处理）**：上游会把旧命令体收编为技能（"collapse legacy command bodies into skills"），`legacy-command-shims/commands/` 留退役垫片——用户目录里的同名副本从此永久停在退役前版本（实例：`/e2e` 用户副本停在 2026-03-29 代，上游已收编为 `ecc:e2e-testing` 技能）。**检测**：用户命令名 ∈ marketplace 克隆 `legacy-command-shims/commands/`。**处置（自动）**：`references/cleanup-retired-commands.sh`——与上游退役前版本逐字节一致 → 自动移除并记日志；不一致（疑自定义）→ WARN 留人工。**注意与坑 4 的区分**：坑 4 是"上游命令存在但插件不分发"（须手动复制保留）；7b 是"上游已退役"（应删，改用 `/ecc:` 技能）。

## 通用铁律（沿用登记表规则）

- 安装/激活状态唯一权威源 = `~/.claude/plugins/installed_plugins.json`；enabledPlugins、cache 目录名、`claude plugins list` 只作旁证
- 装完必做三查：manifest 有 key、cache 目录 `find -type f` 非空壳、`claude plugins list` 可见
