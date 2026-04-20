#!/bin/bash
# 从视频中提取音频并转换为文本
# 该脚本使用openai-whisper技能从视频中提取音频并转换为文本
# 所有路径通过环境变量配置，不再硬编码

if [ $# -ne 2 ]; then
    echo "用法: $0 <video_file> <output_txt_file>"
    exit 1
fi

VIDEO_FILE=$1
OUTPUT_TXT_FILE=$2

echo "正在从视频中提取音频并转换为文本: $VIDEO_FILE"

# 确保输出目录存在
OUTPUT_DIR=$(dirname "$OUTPUT_TXT_FILE")
mkdir -p "$OUTPUT_DIR"

# 验证输入文件是否存在
if [ ! -f "$VIDEO_FILE" ]; then
    echo "错误: 视频文件不存在: $VIDEO_FILE"
    exit 1
fi

# 动态查找 Python 解释器
find_python() {
    local candidates=(
        "${PYTHON_PATH:-}"
        "${VIDEOBOOK_PYTHON_PATH:-}"
        "C:/Users/${USERNAME:-wuyan}/.conda/envs/picproject/python.exe"
        "$HOME/.conda/envs/picproject/python.exe"
        "python"
        "python3"
    )
    for p in "${candidates[@]}"; do
        [ -z "$p" ] && continue
        p="${p/#\~/$HOME}"
        if [ -f "$p" ] && "$p" --version &>/dev/null 2>&1; then
            echo "$p"
            return
        fi
    done
    if command -v python &>/dev/null; then
        echo "python"
        return
    fi
    echo ""
}

# 动态查找 FFmpeg
find_ffmpeg() {
    if [ -n "$FFMPEG_BINARY" ] && [ -f "$FFMPEG_BINARY" ]; then
        dirname "$FFMPEG_BINARY"
        return
    fi
    if [ -n "$FFMPEG_PATH" ] && [ -d "$FFMPEG_PATH" ]; then
        echo "$FFMPEG_PATH"
        return
    fi
    local candidates=(
        "D:/mydoc/workskill/ffmpeg-8.0/bin"
        "/d/mydoc/workskill/ffmpeg-8.0/bin"
        "$HOME/workskill/ffmpeg-8.0/bin"
        "C:/Program Files/ffmpeg/bin"
        "/usr/local/bin"
        "/usr/bin"
    )
    for dir in "${candidates[@]}"; do
        dir="${dir/#\~/$HOME}"
        if [ -f "$dir/ffmpeg.exe" ] || [ -f "$dir/ffmpeg" ]; then
            echo "$dir"
            return
        fi
    done
    if command -v ffmpeg &>/dev/null; then
        echo "system"
        return
    fi
    echo ""
}

PYTHON_CMD="$(find_python)"
FFMPEG_DIR="$(find_ffmpeg)"

if [ -z "$PYTHON_CMD" ]; then
    echo "错误: 未找到可用的 Python 解释器"
    exit 1
fi

echo "使用 Python: $PYTHON_CMD"
echo "使用 FFmpeg 目录: ${FFMPEG_DIR:-系统PATH}"

# 检查whisper是否已安装
if ! "$PYTHON_CMD" -c "import whisper" 2>/dev/null; then
    echo "Whisper未安装，正在尝试安装..."
    "$PYTHON_CMD" -m pip install --upgrade pip
    if ! "$PYTHON_CMD" -m pip install openai-whisper; then
        echo "错误: Whisper安装失败"
        exit 1
    fi
    echo "Whisper安装成功"
fi

# 设置 FFmpeg 环境变量
if [ -n "$FFMPEG_DIR" ] && [ "$FFMPEG_DIR" != "system" ]; then
    export PATH="$PATH:$FFMPEG_DIR"
    export FFMPEG_BINARY="$FFMPEG_DIR/ffmpeg.exe"
    FFMPEG_EXE="$FFMPEG_DIR/ffmpeg.exe"
else
    FFMPEG_EXE="ffmpeg"
fi

echo "使用FFmpeg: $FFMPEG_EXE"

# 获取 Whisper 模型（可通过环境变量配置）
WHISPER_MODEL="${VIDEOBOOK_WHISPER_MODEL:-tiny}"

# 使用 Python 执行 whisper
if "$PYTHON_CMD" -c "
import os
import whisper

# 设置FFmpeg路径（如果指定了自定义路径）
ffmpeg_path = '$FFMPEG_EXE'
if ffmpeg_path and ffmpeg_path != 'ffmpeg':
    os.environ['FFMPEG_BINARY'] = ffmpeg_path

print('正在加载模型...')
model = whisper.load_model('$WHISPER_MODEL')
print('开始转录...')
result = model.transcribe('$VIDEO_FILE')
print('转录完成，写入文件...')
with open('$OUTPUT_TXT_FILE', 'w', encoding='utf-8') as f:
    f.write(result['text'])
print('音频转文本成功完成')
"; then
    if [ -f "$OUTPUT_TXT_FILE" ]; then
        echo "音频转文本成功: $OUTPUT_TXT_FILE"
    else
        echo "错误: Python脚本执行完成但输出文件未创建"
        ls -la "$(dirname "$OUTPUT_TXT_FILE")/"
        exit 1
    fi
else
    echo "错误: Whisper转录失败"
    echo "尝试使用命令行方式执行whisper..."
    if "$PYTHON_CMD" -m whisper "$VIDEO_FILE" --output_dir "$(dirname "$OUTPUT_TXT_FILE")" --output_format txt --model "$WHISPER_MODEL"; then
        POSSIBLE_TXT_FILE="$(dirname "$OUTPUT_TXT_FILE")/$(basename "$VIDEO_FILE" .mp4).txt"
        if [ -f "$POSSIBLE_TXT_FILE" ]; then
            mv "$POSSIBLE_TXT_FILE" "$OUTPUT_TXT_FILE"
            echo "音频转文本成功（通过命令行）: $OUTPUT_TXT_FILE"
        else
            echo "错误: Whisper命令行执行完成但未找到输出文件"
            find "$(dirname "$OUTPUT_TXT_FILE")" -type f -name "*.txt" -exec ls -la {} \;
            exit 1
        fi
    else
        echo "错误: 两种Whisper执行方式都失败了"
        exit 1
    fi
fi