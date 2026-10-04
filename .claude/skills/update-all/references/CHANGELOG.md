# update-all 历史变更记录

> v2.3.0 起历史条目从 SKILL.md 拆分至此（SKILL.md 遵守 1000 行上限）。当前版本变更见 SKILL.md 头部。

## v2.2.0 变更（2026-09-18，pm-skills 插件事件固化为预检）

1. **Phase 2 新增插件对账块**：反向对账（已装但不在 PLUGINS_TO_UPDATE 清单 → WARN 防静默漏更新）+ enabledPlugins 死条目检测（启用≠安装，疑市场撞名/卸载残留）；
2. **防坑清单**：`references/plugin-pitfalls.md`（市场同名撞车、commands 不随插件分发、安装≠会话可见等 5 坑 + 处置命令）；
3. 完整事件记录见项目 `doc/claude-code/插件安装与迁移记录.md`。

## v2.1.0 变更（2026-09-18）

1. **mattpocock 插件化**：S1（npx skills add 项目级安装）整体移除，改为 P* 清单中的 `mattpocock-skills@mattpocock` 插件（上游已有官方 marketplace）；skills-lock.json / .agents/skills 项目级副本已删除；
2. **pm-skills 插件扩充**：jobs-to-be-done 之外新增 8 个 pm-skills 市场插件（prd-development、discovery-process、product-strategy-session、roadmap-planning、market-landscape-scan、competitive-analysis-process、saas-revenue-growth-metrics、organic-growth-advisor）；
3. **C1 语义调整**：npx skills 不再运行，superpowers 副本清理改为 P* 之后的防御性清理。

## v2.0.0 变更

在 v1.4.0「更新 + 验证」基础上新增四项能力：

1. **版本追踪**：逐组件记录是否更新、更新是否成功、版本变迁 from → to；
2. **更新后验证**：统一重探 to 版本 + 功能验证，判定 7 态富状态；
3. **功能差异分析**：定向采集 changelog/commit/diff 证据（三级降级链，禁止臆测）；
4. **更新报告**：无条件在 `doc/update-reports/` 生成中文更新报告（含新增功能举例）。
