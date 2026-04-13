#!/bin/bash

# 舆情分析执行脚本 - 修复版
# 用法：./run.sh "分析对象" [user_open_id]
# 输出：JSON 格式，包含完整报告和进度消息

PROMPT=$1
USER_OPEN_ID=$2

if [ -z "$PROMPT" ]; then
  echo '{"error":"用法：./run.sh \"分析对象\" [user_open_id]"}'
  exit 1
fi

# 转义提示词中的特殊字符
ESCAPED_PROMPT=$(echo "$PROMPT" | sed 's/"/\\"/g' | sed "s/'/\\'/g")

echo "📊 正在分析舆情：$PROMPT"
echo ""

# 调用百炼 API（需要较长超时时间，舆情分析约需 2-5 分钟）
echo "🔍 正在全网检索舆情信息..."
RESPONSE=$(curl -s -X POST "https://dashscope.aliyuncs.com/api/v1/apps/cd6799ccd4fe45fd984ff00f51653f7a/completion" \
  -H "Authorization: Bearer sk-11f7b63be296419099fc355aae9bcf97" \
  -H "Content-Type: application/json" \
  -d "{\"input\":{\"prompt\":\"$PROMPT\"},\"parameters\":{},\"debug\":{}}" --max-time 300)

# 检查 API 响应
if echo "$RESPONSE" | grep -q '"output"'; then
  echo "✅ API 调用成功"
else
  echo "❌ API 调用失败：$RESPONSE"
  exit 1
fi

# 输出完整响应（供上层解析）
echo ""
echo "=== RAW_RESPONSE_START ==="
echo "$RESPONSE"
echo "=== RAW_RESPONSE_END ==="
