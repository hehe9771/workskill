#!/bin/bash
# 检查 videobook 技能的依赖项
# 所有路径通过环境变量配置，不再硬编码
set -e

# Python路径：优先环境变量，再尝试常见位置
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

# FFmpeg路径：优先环境变量，再尝试常见位置
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
FFMPEG_PATH="$(find_ffmpeg)"

echo "正在检查 videobook 依赖项..."
echo "检测到的路径配置:"
echo "  Python: ${PYTHON_CMD:-未找到}"
echo "  FFmpeg: ${FFMPEG_PATH:-未找到}"
echo ""
MISSING=()

# 检查 opencli
if command -v opencli &> /dev/null; then
    echo "[OK] opencli: 已安装"
else
    echo "[WARN] opencli: 未安装（将使用 yt-dlp 降级）"
    MISSING+=("opencli")
fi

# 检查 yt-dlp
if command -v yt-dlp &> /dev/null; then
    echo "[OK] yt-dlp: 已安装"
else
    echo "[FAIL] yt-dlp: 未安装"
    MISSING+=("yt-dlp")
fi

# 检查 Python + whisper
if [ -f "$PYTHON_CMD" ]; then
    if "$PYTHON_CMD" -c "import whisper" 2>/dev/null; then
        echo "[OK] openai-whisper: 已安装 (Python: $PYTHON_CMD)"
    else
        echo "[FAIL] openai-whisper: 未安装在指定Python环境中"
        MISSING+=("openai-whisper")
    fi
else
    echo "[FAIL] Python: 解释器不存在 ($PYTHON_CMD)"
    MISSING+=("python")
fi

# 检查 FFmpeg
FFMPEG_EXE="$FFMPEG_PATH/ffmpeg.exe"
if [ -f "$FFMPEG_EXE" ]; then
    echo "[OK] FFmpeg: 已安装 ($FFMPEG_PATH)"
elif command -v ffmpeg &> /dev/null; then
    echo "[OK] FFmpeg: 已安装 (系统PATH)"
else
    echo "[FAIL] FFmpeg: 未安装"
    MISSING+=("ffmpeg")
fi

# 总结
if [ ${#MISSING[@]} -gt 0 ]; then
    echo ""
    echo "缺少以下依赖，请先安装:"
    printf '  - %s\n' "${MISSING[@]}"
    echo ""
    echo "安装命令参考:"
    echo "  npm install -g @jackwener/opencli"
    echo "  pip install yt-dlp"
    echo "  pip install openai-whisper"
    exit 1
fi

echo ""
echo "所有依赖项均已就绪"
