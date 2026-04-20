# 修复 Claude Code 通过阿里云代理的模型调用错误

## 问题描述
当 Claude Code 通过阿里云代理（如 CCswitch）使用 GLM 模型时，Paperclip 仍会尝试调用原始的 Claude 模型名称（如 `claude-sonnet-4-6`），导致 "model is not supported" 错误。

## 问题原因
- Claude Code 通过代理使用 GLM-5.1 模型（配置在环境变量中）
- Paperclip 维护独立的 LLM 配置，默认使用 Claude 模型名称
- 两者配置不一致导致模型调用失败

## 解决步骤

### 1. 检查当前配置
```bash
# 查看 Paperclip 配置
cat ~/.paperclip/instances/default/config.json
```

### 2. 更新 LLM 配置
修改 `~/.paperclip/instances/default/config.json` 文件，在 `llm` 部分添加模型映射：

```json
"llm": {
  "provider": "claude",
  "apiKey": "<your-aliyun-api-key>",
  "baseUrl": "https://dashscope.aliyuncs.com/api/v2/apps/claude-code-proxy",
  "models": {
    "default": "glm-5.1",
    "haiku": "glm-5.1",
    "sonnet": "glm-5.1",
    "opus": "glm-5.1",
    "reasoning": "glm-5.1"
  }
}
```

### 3. 验证配置
```bash
# 重启 Paperclip 服务
npx paperclipai start

# 测试模型连接
curl -X POST "http://localhost:3100/api/companies/[COMPANY_ID]/adapters/claude_local/test-environment" \
  -H "Content-Type: application/json" \
  -d '{"model":"glm-5.1"}'
```

### 4. 触发代理重新运行
```bash
# 获取代理 ID（从 UI 或 API 获取）
AGENT_ID="your-agent-id"

# 手动唤醒代理
curl -X POST "http://localhost:3100/api/agents/$AGENT_ID/wakeup" \
  -H "Content-Type: application/json" \
  -d '{"source":"on_demand","triggerDetail":"manual","reason":"manual_wakeup","payload":{}}'
```

## 注意事项
- 保留阿里云的 API 密钥和代理 URL 设置不变
- 确保 baseUrl 与您在 CCswitch 中配置的端点一致
- 配置完成后可能需要重启 Paperclip 服务
- 如果有符号链接错误（EPERM），通常不影响模型调用，属于权限问题

## 预防措施
- 在设置 Paperclip 时，同步配置好与 Claude Code 相同的模型映射
- 保持 Claude Code 和 Paperclip 的 LLM 配置一致性