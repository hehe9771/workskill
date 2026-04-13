---
name: bailian-sentiment-analysis
description: 阿里百炼舆情分析应用，生成深度舆情报告并自动创建飞书云文档
homepage: https://www.aliyun.com/product/bailian
metadata: {"moltbot":{"emoji":"📊","requires":{"bins":["mcporter"]},"install":[{"id":"node","kind":"node","package":"mcporter","bins":["mcporter"],"label":"Install mcporter (node)"}]}}
---

# Bailian Sentiment Analysis MCP（百炼舆情分析）

阿里百炼高阶舆情分析应用，自动生成深度舆情报告，并创建飞书云文档存储完整内容。

## 何时使用

当用户需要查询以下类型信息时：

| 类型 | 示例 |
|------|------|
| 企业舆情 | 分析舆情：中联重科、舆情报告：某某公司最近有什么负面新闻 |
| 品牌声量 | 分析舆情：XX 品牌的热度怎么样、市场情绪如何 |
| 情感分析 | 舆情报告：这件事的舆论风向、公众对某事的看法 |
| 风险监测 | 分析舆情：有没有什么风险点、需要关注什么议题 |

**注意**：此类分析**禁止**使用 `web_fetch` / `web_search`，**必须**使用本工具。

## 触发格式

用户消息支持以下格式：

```
分析舆情：XXX
舆情报告：XXX
情感分析：XXX
舆情分析：XXX
/sentiment XXX
```

## 工作流程（重要！）

**必须严格执行以下步骤，确保用户能看到完整信息：**

1. **📡 发送进度消息** - 立即发送：`📡 开始执行「全网舆情检索」...`
2. **🔍 调用百炼 API** - 获取完整舆情分析报告（约 2-5 分钟）
3. **📄 发送进度消息** - 发送：`📄 开始执行「舆情文档生成中」...`
4. **📄 创建飞书文档** - 将 API 返回的**完整原文**写入飞书文档（一字不少）
5. **📤 返回结果** - 发送核心摘要 + 完整文档链接

## 调用方式（OpenClaw 环境）

```bash
# 步骤 1：发送开始进度消息
feishu_im_user_message --action send --receive_id_type open_id --receive_id "ou_xxx" --msg_type text --content '{"text":"📡 开始执行「全网舆情检索」..."}'

# 步骤 2：调用百炼 API（超时 5 分钟）
RESPONSE=$(curl -s -X POST "https://dashscope.aliyuncs.com/api/v1/apps/cd6799ccd4fe45fd984ff00f51653f7a/completion" \
  -H "Authorization: Bearer sk-11f7b63be296419099fc355aae9bcf97" \
  -H "Content-Type: application/json" \
  -d '{"input":{"prompt":"分析对象"},"parameters":{},"debug":{}}' --max-time 300)

# 步骤 3：发送文档生成进度消息
feishu_im_user_message --action send --receive_id_type open_id --receive_id "ou_xxx" --msg_type text --content '{"text":"📄 开始执行「舆情文档生成中」..."}'

# 步骤 4：从响应中提取完整报告文本
# 使用 jq 或手动解析 JSON，提取 .output.text 字段
REPORT=$(echo "$RESPONSE" | jq -r '.output.text')

# 步骤 5：创建飞书文档（完整内容，不省略）
DOC_RESPONSE=$(feishu_create_doc --title "舆情分析报告 - 分析对象" --markdown "$REPORT")

# 步骤 6：提取文档 URL 并返回最终结果
DOC_URL=$(echo "$DOC_RESPONSE" | jq -r '.doc_url')
```

**参数说明**：
- 分析对象：企业名称、品牌名、事件关键词等
- 用户 open_id：用于发送进度消息（可选，但强烈建议提供）

## 输出内容

### 聊天窗口返回（核心摘要）

```
✅ 舆情报告已生成

📄 完整文档：https://xxx.feishu.cn/docx/xxx

---

## 📊 核心摘要

<300 字以内的核心摘要，从完整报告中提取>

| 指标 | 数值 |
|:---|:---:|
| 正面舆情 | XX% |
| 中性舆情 | XX% |
| 负面舆情 | XX% |

---

💡 完整数据明细、图表、详细分析请点击文档链接查看
```

### 飞书文档内容（完整报告，一字不少）

**必须包含 API 返回的所有内容，不得省略：**

- 宏观摘要：声量、热度、情绪结构
- 深度分析：股票/市场动态、行业背景、议题集中度
- 明细数据表：带链接的详细分类数据（全部条数，不截断）
- 可视化图表：QuickChart 情感分布图（如有）
- 风险与建议：多维度风险评估与应对策略
- 数据来源：所有引用链接

## 注意事项（重要！）

1. **完整内容**：飞书文档必须包含 API 返回的**所有内容**，不得省略、截断或摘要
2. **进度推送**：执行过程中必须发送 2 条进度消息（开始检索、开始生成文档）
3. **超时配置**：timeout 设置为 300 秒（5 分钟），确保长报告完整生成
4. **数据来源**：数据来源于阿里百炼舆情分析应用
5. **文档权限**：创建的飞书文档默认对当前用户可见
6. **明细数据**：数据条数由百炼 API 返回决定，实事求是，不强制固定数量
7. **原文保留**：API 返回的 Markdown 格式、表格、图表链接等必须原样保留

## 错误处理

- **API 调用失败**：返回错误信息，建议用户重试
- **文档创建失败**：将报告保存为本地文件，返回文件路径
- **超时**：返回已获取的部分内容，说明原因
