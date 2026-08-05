# 更新报告模板（update-all v2.0.0 · Phase 5 撰写用）

## 写作红线（先读）

1. **版本号只准来自本次实查**（results.tsv / versions-before.env / Phase 2 重探），禁止凭记忆或上一篇报告推断（环境会变）。
2. **失败不许隐藏**：每个 FAIL 必须进 §6 并附错误摘录（截自 `$SNAP_DIR/errors/<step>.err`，不改写）+ 修复建议；无失败时显式写"本次无失败项"，不许省略该节。
3. **SKIP/黑名单必写原因**，不许静默略过（呼应项目规则"禁止静默吞异常"与 2026-07-07 claude-mem 残缺版教训）。
4. **功能论断必引证据**：只准引用 evidence-manifest.tsv 中 L1/L2 条目的证据路径；L3 用固定降级句（见 references/evidence-guide.md §2）；禁止凭训练记忆编造 changelog。
5. 全文中文。

## 落点与命名

- 目录：`$REPORT_DIR`（Phase 0 已写入 `$SNAP_DIR/meta`；默认 `<git 根>/doc/update-reports`，可被环境变量 `UPDATE_ALL_REPORT_DIR` 覆盖；本项目即 `D:/mydoc/workskill/doc/update-reports/`）。执行前 `mkdir -p`。
- 文件名：`更新报告-YYYYMMDD-HHmm.md`，时间戳取 START_TIME，24 小时制精确到分钟，**禁用冒号**（Windows 文件名 9 个非法字符 `: \ / ? * " < > |`）；同日同分钟撞名追加 `-2`。
- 不复用 `doc/claude-code/`（那是 CLI changelog 分析系列，语义不同）；报告开头注明两系列区别并引用其最新一篇。
- 撰写方式：Claude 用 **Write 工具**落盘（长中文内容不走 bash heredoc，规避 Windows Git Bash 编码与引号风险）。
- 数据源：`$SNAP_DIR/results.tsv` + `versions-before.env` + `evidence-manifest.tsv` + `evidence/` + `errors/` + `~/.claude/update-all.log` 尾部。
- 行数校验：生成后 `wc -l` 校验 ≤1000 行；超限拆 `更新报告-<同时间戳>-附录-证据摘录.md`（主报告保留 §1–§7，证据明细入附录）。

---

## 模板正文

```markdown
# YYYY-MM-DD HH:mm 环境更新报告（update-all 执行记录）

> 本报告记录 YYYY-MM-DD HH:mm 在本机执行 update-all vX.Y.Z 的结果，
> 覆盖 npm 全局工具 / gstack / playwright-cli / specify-cli / marketplace / 插件 / ECC 同步 / skills 包全过程。
> 数据来源：本次 update-all 命令实际输出（$SNAP_DIR/results.tsv、out/、errors/）+ ~/.claude/update-all.log + 各组件版本实查。
> 与 doc/claude-code/更新*.md 的区别：本文是"本机更新后的结果报告"，不是"升级前 changelog 分析"；
> CLI 本体在黑名单内本次未更新，其版本分析见 doc/claude-code/ 最新一篇（<引用其文件名>）。

## 1. 执行概况

[表格：执行开始/结束时间 | 耗时 | update-all 版本 | PASS / FAIL / SKIP 数 | 总体结论（✅ 全部通过 / ⚠️ N 项失败）]
[验证失败 N 项（V- 行口径：更新命令 exit=0 但功能验证失败，不计入三态 FAIL，单独列出；0 项也写明）]
[富状态分布：UPDATED / UP_TO_DATE / FAILED / BLACKLIST / NOT_INSTALLED / REPAIRED / OK 计数]
[黑名单跳过项单独列出：@anthropic-ai/claude-code、claude-notifications-go，各附跳过原因]
[一句话结论先行：本次更新是否达到预期、是否需要人工介入]

## 2. 组件更新状态总表

[以 results.tsv 的 V- 复核行为准（版本真相），一行一组件，不许合并省略]
[列：组件 | 类别（npm/skill/uv/marketplace/plugin/修复/健康检查）| 状态图标 | 旧版本 | 新版本 | 备注]
[状态图标映射：UPDATED=✅ 已更新 / UP_TO_DATE=⏸ 已是最新 / FAILED=❌ 更新失败 /
 BLACKLIST=⏭ 黑名单跳过 / NOT_INSTALLED=⏭ 未安装跳过 / REPAIRED=🔧 已修复 / OK=⏺ 检查正常]
[SKIP 项必须写明跳过原因（未安装 / 黑名单 / 条件未触发），不许静默略过]

## 3. 版本变迁

[每个有版本变化的组件一行/一小节：旧版本 → 新版本 | 更新途径（npm/git clone/marketplace/uv/npx）| 版本信息来源命令]
[版本号必须来自本次实查，禁止凭记忆填写]
[无版本变化的组件标注"已是最新，无变迁"，并给出判定依据（命令 exit 0 且 to==from）]

## 4. 功能差异与新增功能详解（含举例）

[每个"版本有实质变化"的组件一小节，固定三要素：]
[**变化内容**：只摘与本机相关的 changelog/commit 条目，不复述全部 changelog，每条附证据路径]
[**对本机影响**：✅ 直接受益（说明受益场景）/ ⚠️ 无感（附原因）/ 潜在冲突（如与 CLAUDE.md 规则、黑名单、--settings 环境的关系）]
[**用法举例**：结合本机真实场景，遵守举例来源白名单（evidence-guide.md §5 第 3 条）；
 新增技能给触发语示例（取自证据中 SKILL.md frontmatter description）、新增 agents 给名称+用途、
 新增 rules 给生效路径；证据只有名称没有用法写「用法待验证」；无对应证据写「无新增可举例项」]
[重大行为变化（影响黑名单/--settings/daemon）用 ★★ 标注并写明判断依据]
[证据缺失用固定降级句；无实质新功能的组件一句话带过——禁止只罗列 changelog 充数]

## 5. 验证结果

[表格一（更新步骤，来自 results.tsv 动作行）：步骤 | 组件 | 验证方式（verify 列）| 结果 | 说明]
[表格二（健康检查 H1–H7）：检查项 | 检查内容 | 结果 | 说明]
[计数与 ~/.claude/update-all.log 末尾汇总行核对一致；不一致时以 results.tsv 为准并注明]
[口径说明：「exit=0 但功能验证失败」的组件，表一（动作行）显示 exit=0 而 V- 复核行为 FAIL——两轨各记真相
 （动作行=命令执行真相，V- 行=版本/功能真相）；§1/§6 的失败口径为动作行 FAIL + V- 行 FAIL 的并集]
[有 FAIL 时附关键错误输出摘录（截自 $SNAP_DIR/errors/<step>.err 原文，不改写）]

## 6. 失败项与修复建议

[每个 FAIL 一小节，固定四要素：**现象**（错误摘录）/ **根因判断** / **修复命令**（可直接复制执行）/ **是否已当场修复**]
[修复建议优先引用 update-all 技能「故障排查」节现成方案（specify-cli ModuleNotFoundError、
 插件改名、gstack setup、激活版本判定、symlink find 空结果、V- 复核失败排查、报告补写路径）]
[本次全部通过时，此节写"本次无失败项"，并列出下次执行需关注的风险点（如某上游近期出过残缺发布）]

## 7. 后续待办

[必含三项：]
[1. 重启 Claude Code daemon 使插件生效]
[2. 如改过 settings：逐文件核对各 --settings 文件 env 段 DISABLE_AUTOUPDATER=1（不继承坑，见技能黑名单节警告）]
[3. 黑名单组件手动升级跟进：引用 doc/claude-code/ 最新一篇的升级建议结论]
[可选：失败项未修复时的复跑计划]

## 附：执行环境快照

[本机特征：Windows 版本 | 代理状态（HTTP_PROXY/HTTPS_PROXY）| DISABLE_AUTOUPDATER 各 settings 文件核对结果 |
 update-all 版本与黑名单快照 | 全组件版本（含 claude-mem 被动行，标注"不在本技能管理范围"）]
[数据取自 $SNAP_DIR/env.txt + versions-before.env；此快照供下一篇报告做版本变迁与行为对比的基线]
```

---

## 收尾口头汇报（模板外硬性动作）

报告写完后向用户汇报四件事：
1. 总体结论（成功/部分失败）；
2. 版本变化最大的 3 项；
3. 失败数与待办；
4. 报告绝对路径。
