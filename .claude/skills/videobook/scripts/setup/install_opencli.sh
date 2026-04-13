#!/bin/bash
# 安装opencli工具
# 该脚本会安装opencli工具用于视频下载

set -e  # 遇到错误立即退出

echo "正在安装opencli..."

# 检查系统类型
PLATFORM="unknown"
case "$(uname -s)" in
    Linux*)     PLATFORM="linux";;
    Darwin*)    PLATFORM="darwin";;
    CYGWIN*)    PLATFORM="windows";;
    MINGW*)     PLATFORM="windows";;
    *)          PLATFORM="unknown";;
esac

if [ "$PLATFORM" == "unknown" ]; then
    echo "错误: 不支持的操作系统平台"
    exit 1
fi

# 检查是否已安装curl
if ! command -v curl &> /dev/null; then
    echo "错误: 未找到curl，请先安装curl"
    exit 1
fi

# 下载并安装opencli
echo "正在下载opencli..."
DOWNLOAD_URL="https://raw.githubusercontent.com/opencli/opencli/main/install.sh"

# 创建临时目录
TEMP_DIR=$(mktemp -d)
INSTALLER="$TEMP_DIR/install_opencli.sh"

# 下载安装脚本
if ! curl -s -o "$INSTALLER" "$DOWNLOAD_URL"; then
    echo "错误: 无法下载opencli安装脚本"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# 检查下载的脚本是否存在
if [ ! -f "$INSTALLER" ]; then
    echo "错误: 安装脚本下载失败"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# 运行安装脚本
chmod +x "$INSTALLER"
if ! "$INSTALLER"; then
    echo "错误: opencli安装失败"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# 清理临时文件
rm -rf "$TEMP_DIR"

# 验证安装
if command -v opencli &> /dev/null; then
    echo "opencli安装成功: $(opencli --version)"
else
    echo "错误: opencli安装后不可用"
    exit 1
fi