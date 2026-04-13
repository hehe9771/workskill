#!/bin/bash
# 设置环境变量
# 该脚本设置处理视频所需的环境变量

set -e  # 遇到错误立即退出

# 检测操作系统并设置相应的临时目录
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows 系统
    export VIDEO_TEMP_DIR="$(mktemp -d 2>/dev/null || mktemp -d -t videobook_temp_)"
    if [ -z "$VIDEO_TEMP_DIR" ] || [ "$VIDEO_TEMP_DIR" = "/tmp" ]; then
        # 如果 mktemp 失败，使用 Windows 临时目录
        VIDEO_TEMP_DIR="/c/Users/$USER/AppData/Local/Temp/videobook_temp_$$"
    fi
else
    # Unix/Linux 系统
    export VIDEO_TEMP_DIR="/tmp/videobook_temp_$$"
fi

mkdir -p "$VIDEO_TEMP_DIR"
echo "设置临时目录: $VIDEO_TEMP_DIR"

# 设置输出目录
if [ -z "$TEXT_OUTPUT_DIR" ]; then
    export TEXT_OUTPUT_DIR="$VIDEO_TEMP_DIR/text_output"
    mkdir -p "$TEXT_OUTPUT_DIR"
fi

if [ -z "$MD_OUTPUT_DIR" ]; then
    export MD_OUTPUT_DIR="$VIDEO_TEMP_DIR/md_output"
    mkdir -p "$MD_OUTPUT_DIR"
fi

# 设置日志级别
if [ -z "$LOG_LEVEL" ]; then
    export LOG_LEVEL="INFO"
fi

# 验证必要的工具是否可用
MISSING_TOOLS=()

# 检查是否可以通过标准路径访问命令，如果没有，则添加自定义路径
for cmd in opencli; do
    if ! command -v "$cmd" &> /dev/null; then
        MISSING_TOOLS+=("$cmd")
    fi
done

# 特别处理FFmpeg，因为它可能不在标准路径中
if ! command -v ffmpeg &> /dev/null; then
    # 尝试使用预设的路径
    CUSTOM_FFMPEG_PATH="/d/mydoc/workskill/ffmpeg-8.0/bin"
    if [ -f "$CUSTOM_FFMPEG_PATH/ffmpeg.exe" ]; then
        # 将FFmpeg路径添加到当前会话的PATH
        export PATH="$PATH:$CUSTOM_FFMPEG_PATH"
        echo "FFmpeg已添加到PATH: $CUSTOM_FFMPEG_PATH"
    else
        MISSING_TOOLS+=("ffmpeg")
    fi
fi

if [ ${#MISSING_TOOLS[@]} -ne 0 ]; then
    echo "警告: 以下必要工具未找到，某些功能可能不可用:"
    printf '%s\n' "${MISSING_TOOLS[@]}"
fi

echo "环境设置完成"