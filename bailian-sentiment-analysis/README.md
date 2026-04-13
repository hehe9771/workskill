# 舆情分析技能配置说明

## 概述

本技能实现：用户发送舆情分析请求 → 调用百炼 API → 创建飞书云文档 → 返回摘要 + 文档链接

**工作模式**：透传模式（所有搜索、分析、明细生成逻辑均在百炼端完成，本地仅负责请求转发与结果渲染）

## 文件结构

```
~/.openclaw/workspace/skills/bailian-sentiment-analysis/
├── SKILL.md          # 技能文档
├── README.md         # 本配置说明
└── run.sh            # 执行脚本
```

## API 配置

### 百炼应用信息
- **App ID**: `cd6799ccd4fe45fd984ff00f51653f7a`
- **API Key**: `sk-11f7b63be296419099fc355aae9bcf97`
- **超时时间**: 300 秒（5 分钟）
- **工作模式**: 透传模式

### API 调用命令

```bash
curl -s -X POST "https://dashscope.aliyuncs.com/api/v1/apps/cd6799ccd4fe45fd984ff00f51653f7a/completion" \
  -H "Authorization: Bearer sk-11f7b63be296419099fc355aae9bcf97" \
  -H "Content-Type: application/json" \
  -d '{"input":{"prompt":"分析一下小米科技的舆情"},"parameters":{},"debug":{}}' --max-time 300
```

## 使用方式

### 方式一：直接在对话中使用（推荐）

用户发送：
```
分析舆情：XXX
舆情报告：XXX
情感分析：XXX
舆情分析：XXX
/sentiment XXX
```

处理流程：
1. 调用百炼 API 获取完整报告
2. 创建飞书云文档
3. 返回核心摘要 + 文档链接

### 方式二：手动执行脚本

```bash
~/.openclaw/workspace/skills/bailian-sentiment-analysis/run.sh "分析一下小米科技的舆情"
```

## 触发关键词

支持以下触发格式：

| 格式 | 示例 |
|------|------|
| 分析舆情：XXX | 分析舆情：小米科技 |
| 舆情报告：XXX | 舆情报告：中联重科 |
| 情感分析：XXX | 情感分析：某品牌发布会 |
| 舆情分析：XXX | 舆情分析：特斯拉最近新闻 |
| /sentiment XXX | /sentiment 华为舆情 |

## 输出格式

### 聊天回复
```
📊 舆情分析报告已生成

【核心摘要】
- 声量统计：XXX
- 情感占比：正面 XX% / 负面 XX% / 中立 XX%
- 关键发现：XXX

【明细数据】
- 数据条数：X 条（由百炼 API 返回决定）

【风险预警】
⚠️ XXX

📄 完整报告：https://xxx.feishu.cn/docx/XXXXXX
```

### 飞书文档内容（完整报告）
- 宏观摘要（声量、热度、情绪结构）
- 深度分析（市场动态、行业背景、议题集中度）
- 明细数据表（带链接，数量由百炼 API 返回决定）
- 可视化图表（QuickChart 情感分布图）
- 风险与建议

## 关键配置说明

| 配置项 | 值 | 说明 |
| :--- | :--- | :--- |
| `timeout` | `300000` | **关键**: 设置为 5 分钟。因百炼端需生成明细数据及长报告，耗时较长，需防止中途截断。 |
| `retry` | `2` | 网络波动时自动重试 2 次。 |
| `stream` | `false` | 非流式响应，等待完整报告生成后一次性返回，确保表格完整性。 |
| `body.prompt` | `{{content}}` | **纯净透传**: 不在本地添加额外指令，完全依赖百炼应用内部的 System Prompt 逻辑。 |

## 故障排查

### 问题 1：报告生成不全/表格缺失
**解决**：检查 `timeout` 是否被重置为默认值（通常 30s-60s 不够用），确保设置为 300 秒

### 问题 2：飞书文档创建失败
**解决**：检查飞书授权状态，运行 `feishu_oauth_batch_auth` 完成授权

### 问题 3：明细数据条数较少
**说明**：数据条数由百炼 API 根据实际可获取的公开信息决定，实事求是，不强制固定数量。某些冷门主题可能数据较少，属于正常现象。

### 问题 4：API 调用超时
**解决**：
1. 检查网络连接
2. 确认 API Key 有效
3. 适当增加 `--max-time` 参数值

## 测试验证

### 测试命令
```bash
# API 调用测试
curl -s -X POST "https://dashscope.aliyuncs.com/api/v1/apps/cd6799ccd4fe45fd984ff00f51653f7a/completion" \
  -H "Authorization: Bearer sk-11f7b63be296419099fc355aae9bcf97" \
  -H "Content-Type: application/json" \
  -d '{"input":{"prompt":"分析一下特斯拉的舆情"},"parameters":{},"debug":{}}' --max-time 300
```

### 验证标准
- ✅ API 调用成功，返回完整 Markdown 报告
- ✅ 飞书文档创建成功，链接可访问
- ✅ 报告包含宏观摘要、深度分析、明细数据、风险建议
- ✅ 明细数据条数由百炼 API 决定，不强制固定数量

---

**最后更新**: 2026-03-24
**版本**: 1.2.0 (优化超时与透传逻辑)
