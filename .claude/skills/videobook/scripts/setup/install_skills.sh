#!/bin/bash
# 安装所需的技能
# 该脚本会安装处理视频所需的各项技能

set -e  # 遇到错误立即退出

echo "正在安装所需技能..."

# 检查是否已安装npm
if ! command -v npm &> /dev/null; then
    echo "错误: 未找到npm，请先安装Node.js"
    exit 1
fi

# 安装openai-whisper技能
echo "正在安装openai-whisper技能..."
npx skills add https://github.com/steipete/clawdis --skill openai-whisper

if [ $? -ne 0 ]; then
    echo "警告: openai-whisper技能安装可能失败"
fi

# 安装convert-plaintext-to-md技能
echo "正在安装convert-plaintext-to-md技能..."
npx skills add https://github.com/github/awesome-copilot --skill convert-plaintext-to-md

if [ $? -ne 0 ]; then
    echo "警告: convert-plaintext-to-md技能安装可能失败"
fi

# 安装mermaid-diagrams技能
echo "正在安装mermaid-diagrams技能..."
npx skills add https://github.com/softaworks/agent-toolkit --skill mermaid-diagrams

if [ $? -ne 0 ]; then
    echo "警告: mermaid-diagrams技能安装可能失败"
fi

echo "技能安装完成"