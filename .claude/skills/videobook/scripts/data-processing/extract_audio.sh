#!/bin/bash
# 从视频中提取音频并转换为文本
# 该脚本使用openai-whisper技能从视频中提取音频并转换为文本
# 严格按照要求：whisper技能必须调用成功，不能使用备选方案

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

# 检查Python是否可用
SPECIFIC_PYTHON="C:/Users/wuyan/.conda/envs/picproject/python.exe"
if [ -f "$SPECIFIC_PYTHON" ]; then
    # 检查whisper是否已安装在特定Python环境中
    if "$SPECIFIC_PYTHON" -c "import whisper" 2>/dev/null; then
        echo "Whisper已安装，正在处理音频..."
        PYTHON_CMD="$SPECIFIC_PYTHON"
    else
        echo "错误: Whisper未安装在指定环境中。正在尝试安装..."
        # 尝试安装whisper
        echo "正在使用pip安装whisper..."
        "$SPECIFIC_PYTHON" -m pip install --upgrade pip
        if "$SPECIFIC_PYTHON" -m pip install openai-whisper; then
            PYTHON_CMD="$SPECIFIC_PYTHON"
            echo "Whisper安装成功"
        else
            echo "错误: Whisper安装失败"
            exit 1
        fi
    fi
else
    echo "错误: 指定的Python解释器不存在: $SPECIFIC_PYTHON"
    exit 1
fi

# 确保FFmpeg在系统中可用
CUSTOM_FFMPEG_PATH="/d/mydoc/workskill/ffmpeg-8.0/bin"

# 检查FFmpeg是否在路径中可用
if ! command -v ffmpeg &> /dev/null; then
    # 如果不在路径中，尝试添加到路径
    export PATH="$PATH:$CUSTOM_FFMPEG_PATH"
fi

# 设置环境变量给Python使用
export PATH="$PATH:$CUSTOM_FFMPEG_PATH"
export FFMPEG_BINARY="$CUSTOM_FFMPEG_PATH/ffmpeg.exe"

echo "使用FFmpeg路径: $FFMPEG_BINARY"

# 使用经过验证的手动测试方法执行whisper
if $PYTHON_CMD -c "
import os
# 设置FFmpeg路径
os.environ['FFMPEG_BINARY'] = '$CUSTOM_FFMPEG_PATH/ffmpeg.exe'

import whisper
print('正在加载模型...')
model = whisper.load_model('tiny')
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
        echo "检查 $(dirname "$OUTPUT_TXT_FILE") 目录内容:"
        ls -la "$(dirname "$OUTPUT_TXT_FILE")/"
        exit 1
    fi
else
    echo "错误: Whisper转录失败"
    # 作为备选方案，使用命令行方式
    echo "尝试使用命令行方式执行whisper..."
    if $PYTHON_CMD -m whisper "$VIDEO_FILE" --output_dir "$(dirname "$OUTPUT_TXT_FILE")" --output_format txt --model tiny; then
        # 查找生成的txt文件并移动到期望位置
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