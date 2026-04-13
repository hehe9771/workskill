#!/bin/bash
# 验证视频URL格式和可访问性
# 该脚本验证提供的视频URL是否有效

set -e  # 遇到错误立即退出

if [ $# -ne 1 ]; then
    echo "用法: $0 <video_url>"
    exit 1
fi

VIDEO_URL=$1

echo "正在验证视频URL: $VIDEO_URL"

# 检查URL格式
if [[ ! "$VIDEO_URL" =~ ^https?:// ]]; then
    echo "错误: URL格式无效，必须以http://或https://开头"
    exit 1
fi

# 验证是否为支持的平台
SUPPORTED_PLATFORMS=("youtube.com" "youtu.be" "bilibili.com" "vimeo.com" "tiktok.com" "twitter.com" "instagram.com")

DOMAIN=$(echo "$VIDEO_URL" | sed -e 's|^[^/]*//||' -e 's|/.*$||' | tr '[:upper:]' '[:lower:]')

SUPPORTED=false
for platform in "${SUPPORTED_PLATFORMS[@]}"; do
    if [[ "$DOMAIN" == *"$platform"* ]]; then
        SUPPORTED=true
        break
    fi
done

if [ "$SUPPORTED" != true ]; then
    echo "警告: 检测到非标准平台 ($DOMAIN)，但仍尝试处理"
fi

# 尝试获取页面头部信息以验证URL可达性
if command -v curl &> /dev/null; then
    RESPONSE=$(curl -I --connect-timeout 10 --max-time 30 --silent "$VIDEO_URL" 2>/dev/null)
    if echo "$RESPONSE" | grep -qi "HTTP/[12]\.[012] [23][0-9][0-9]" || echo "$RESPONSE" | grep -qi "HTTP/2 [23][0-9][0-9]"; then
        echo "视频URL验证成功"
    else
        echo "错误: 无法访问视频URL"
        echo "$RESPONSE" >&2  # 输出响应内容以供调试
        exit 1
    fi
elif command -v wget &> /dev/null; then
    if wget --spider --timeout=30 --tries=2 "$VIDEO_URL" 2>/dev/null; then
        echo "视频URL验证成功"
    else
        echo "错误: 无法访问视频URL"
        exit 1
    fi
else
    echo "警告: 未找到curl或wget，跳过URL可达性检查"
fi

echo "视频URL格式验证完成"