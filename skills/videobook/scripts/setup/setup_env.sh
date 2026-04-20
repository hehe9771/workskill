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

# 特别处理FFmpeg（优先环境变量，再尝试常见位置）
if ! command -v ffmpeg &> /dev/null; then
    # 环境变量优先
    if [ -n "$FFMPEG_BINARY" ] && [ -f "$FFMPEG_BINARY" ]; then
        FFMPEG_DIR="$(dirname "$FFMPEG_BINARY")"
        export PATH="$PATH:$FFMPEG_DIR"
        echo "FFmpeg已添加到PATH (来自FFMPEG_BINARY): $FFMPEG_DIR"
    elif [ -n "$FFMPEG_PATH" ] && [ -d "$FFMPEG_PATH" ]; then
        export PATH="$PATH:$FFMPEG_PATH"
        echo "FFmpeg已添加到PATH (来自FFMPEG_PATH): $FFMPEG_PATH"
    else
        # 常见位置候选
        for dir in "D:/mydoc/workskill/ffmpeg-8.0/bin" "/d/mydoc/workskill/ffmpeg-8.0/bin" "$HOME/workskill/ffmpeg-8.0/bin" "C:/Program Files/ffmpeg/bin"; do
            dir="${dir/#\~/$HOME}"
            if [ -f "$dir/ffmpeg.exe" ] || [ -f "$dir/ffmpeg" ]; then
                export PATH="$PATH:$dir"
                echo "FFmpeg已添加到PATH: $dir"
                break
            fi
        done
        if ! command -v ffmpeg &> /dev/null; then
            MISSING_TOOLS+=("ffmpeg")
        fi
    fi
fi

if [ ${#MISSING_TOOLS[@]} -ne 0 ]; then
    echo "警告: 以下必要工具未找到，某些功能可能不可用:"
    printf '%s\n' "${MISSING_TOOLS[@]}"
fi

echo "环境设置完成"