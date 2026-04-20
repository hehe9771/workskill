#!/bin/bash
# 检查 videobook 技能的依赖项
# 脚本自动检测技能目录位置，兼容项目级和全局级安装
set -e

# 自动检测技能目录（脚本位于 scripts/validation/ 下，往上两级是技能根目录）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Python 路径：优先环境变量，其次自动检测
if [ -n "$VIDEOBOOK_PYTHON" ]; then
    PYTHON_CMD="$VIDEOBOOK_PYTHON"
elif [ -n "$CONDA_PREFIX" ]; then
    PYTHON_CMD="$CONDA_PREFIX/python.exe"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD=""  # 将在检查时报错
fi

# FFmpeg 路径：优先环境变量，其次自动检测
if [ -n "$VIDEOBOOK_FFMPEG" ]; then
    FFMPEG_PATH="$VIDEOBOOK_FFMPEG"
elif [ -n "$FFMPEG_BINARY" ]; then
    FFMPEG_PATH="$FFMPEG_BINARY"
elif command -v ffmpeg &> /dev/null; then
    FFMPEG_PATH=""  # 使用系统PATH
else
    FFMPEG_PATH=""  # 将在检查时报错
fi

echo "正在检查 videobook 依赖项..."
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
if [ -n "$FFMPEG_PATH" ] && [ -f "$FFMPEG_PATH/ffmpeg.exe" ]; then
    echo "[OK] FFmpeg: 已安装 ($FFMPEG_PATH)"
elif [ -n "$FFMPEG_PATH" ] && [ -f "$FFMPEG_PATH/ffmpeg" ]; then
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
