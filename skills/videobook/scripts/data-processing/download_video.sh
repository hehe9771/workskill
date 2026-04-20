#!/bin/bash
# 从视频链接下载视频（使用 opencli 或 yt-dlp）
# 输出：视频文件路径（写入 stdout 最后一行）
set -e

if [ $# -lt 1 ]; then
    echo "用法: $0 <video_url> [output_dir]" >&2
    echo "  video_url: 视频链接" >&2
    echo "  output_dir: 输出目录（可选，默认为 output）" >&2
    exit 1
fi

VIDEO_URL="$1"
OUTPUT_DIR="${2:-output}"
mkdir -p "$OUTPUT_DIR"

echo "正在下载视频: $VIDEO_URL"

# 查找 FFmpeg（优先环境变量，再尝试常见位置）
find_ffmpeg() {
    # 环境变量优先
    if [ -n "$FFMPEG_BINARY" ] && [ -f "$FFMPEG_BINARY" ]; then
        echo "$FFMPEG_BINARY"
        return
    fi
    if [ -n "$FFMPEG_PATH" ]; then
        if [ -f "$FFMPEG_PATH/ffmpeg.exe" ]; then
            echo "$FFMPEG_PATH/ffmpeg.exe"
            return
        elif [ -f "$FFMPEG_PATH/ffmpeg" ]; then
            echo "$FFMPEG_PATH/ffmpeg"
            return
        fi
    fi
    # 系统命令
    if command -v ffmpeg &> /dev/null; then
        echo "ffmpeg"
        return
    fi
    # 常见位置候选（最后备用）
    local candidates=(
        "D:/mydoc/workskill/ffmpeg-8.0/bin/ffmpeg.exe"
        "/d/mydoc/workskill/ffmpeg-8.0/bin/ffmpeg.exe"
        "$HOME/workskill/ffmpeg-8.0/bin/ffmpeg.exe"
        "C:/Program Files/ffmpeg/bin/ffmpeg.exe"
        "/usr/local/bin/ffmpeg"
        "/usr/bin/ffmpeg"
    )
    for f in "${candidates[@]}"; do
        f="${f/#\~/$HOME}"
        if [ -f "$f" ]; then
            echo "$f"
            return
        fi
    done
    echo ""
}

# 清理标题为合法文件名（移除特殊字符）
sanitize_filename() {
    local title="$1"
    # 移除或替换非法字符
    echo "$title" | sed 's/[\/\\:*?"<>|]/_/g' | sed 's/\s+/_/g' | sed 's/__*/_/g' | sed 's/^_//' | sed 's/_$//'
}

# 获取视频标题
get_video_title() {
    local url="$1" title=""
    # 使用 yt-dlp 获取标题（最可靠的方式）
    if command -v yt-dlp &> /dev/null; then
        title="$(yt-dlp --get-title "$url" 2>/dev/null | head -n1)"
    fi
    # 如果获取失败，尝试从 URL 提取 BV 号作为备用
    if [ -z "$title" ]; then
        if [[ "$url" =~ bilibili\.com ]] || [[ "$url" =~ b23\.tv ]]; then
            title="$(echo "$url" | grep -oE 'BV[a-zA-Z0-9]{10}' | head -n1)"
        elif [[ "$url" =~ youtube\.com ]] || [[ "$url" =~ youtu\.be ]]; then
            title="$(echo "$url" | grep -oE '(v=|youtu\.be/)[a-zA-Z0-9_-]{11}' | sed 's/v=//' | sed 's/youtu\.be\//')"
        else
            title="video_$(date +%Y%m%d_%H%M%S)"
        fi
    fi
    sanitize_filename "$title"
}

# 合并分离的视频和音频流
merge_streams() {
    local dir="$1" base="$2" ffmpeg_path
    ffmpeg_path="$(find_ffmpeg)"
    [ -z "$ffmpeg_path" ] && return

    local video_file="" audio_file=""
    for f in "$dir"/"${base}"*.mp4 "$dir"/"${base}"*.m4a "$dir"/"${base}"*.mkv; do
        [ -f "$f" ] || continue
        case "$f" in
            *.m4a|*.aac|*.opus) audio_file="$f" ;;
            *) video_file="$f" ;;
        esac
    done

    if [ -n "$video_file" ] && [ -n "$audio_file" ]; then
        echo "检测到分离的音视频流，使用 ffmpeg 合并..."
        local merged="${dir}/${base}_merged.mp4"
        "$ffmpeg_path" -y -i "$video_file" -i "$audio_file" -c copy "$merged" 2>/dev/null
        if [ -f "$merged" ]; then
            rm -f "$video_file" "$audio_file"
            mv "$merged" "$OUTPUT_FILE"
        fi
    fi
}

# 验证下载结果：找到实际生成的视频文件
validate_download() {
    local dir="$1" expected="$2"
    if [ -f "$expected" ] && [ -s "$expected" ]; then
        echo "$expected"
        return
    fi
    local base
    base="$(basename "$expected" | sed 's/\.[^.]*$//')"
    local found="" max_size=0
    for f in "$dir"/"${base}"*; do
        [ -f "$f" ] || continue
        case "$f" in
            *.mp4|*.mkv|*.flv|*.mov|*.avi) ;;
            *) continue ;;
        esac
        local sz
        sz="$(stat -c%s "$f" 2>/dev/null || wc -c < "$f" 2>/dev/null || echo 0)"
        if [ "$sz" -gt "$max_size" ]; then
            max_size=$sz
            found="$f"
        fi
    done
    if [ -n "$found" ] && [ "$found" != "$expected" ]; then
        mv "$found" "$expected"
    fi
    if [ -f "$expected" ] && [ -s "$expected" ]; then
        echo "$expected"
    else
        echo "错误: 没有找到有效的视频文件" >&2
        return 1
    fi
}

# 根据平台下载视频
download_video() {
    local url="$1" output="$2" dir
    dir="$(dirname "$output")"

    if [[ "$url" =~ bilibili\.com ]] || [[ "$url" =~ b23\.tv ]]; then
        local bvid
        bvid="$(echo "$url" | grep -oE 'BV[a-zA-Z0-9]{10}' | head -n1)"
        [ -z "$bvid" ] && { echo "错误: 无法提取B站视频ID" >&2; return 1; }
        echo "检测到B站视频: $bvid"
        if opencli doctor 2>&1 | grep -q "\[OK\].*Extension"; then
            opencli bilibili download "$bvid" --output "$dir"
        else
            echo "Browser Bridge不可用，使用yt-dlp..."
            yt-dlp -o "$output" "$url"
        fi
    elif [[ "$url" =~ youtube\.com ]] || [[ "$url" =~ youtu\.be ]]; then
        if opencli doctor 2>&1 | grep -q "\[OK\].*Extension"; then
            opencli youtube download "$url" -o "$output"
        else
            echo "Browser Bridge不可用，使用yt-dlp..."
            yt-dlp -o "$output" "$url"
        fi
    else
        opencli download "$url" -o "$output" 2>/dev/null || \
        opencli browser download "$url" -o "$output" 2>/dev/null || \
        yt-dlp -o "$output" "$url"
    fi
}

# 获取视频标题并生成输出文件路径
VIDEO_TITLE="$(get_video_title "$VIDEO_URL")"
OUTPUT_FILE="${OUTPUT_DIR}/${VIDEO_TITLE}.mp4"
echo "视频标题: $VIDEO_TITLE"
echo "输出文件: $OUTPUT_FILE"

# 执行下载
if command -v opencli &> /dev/null; then
    echo "使用opencli下载视频..."
    download_video "$VIDEO_URL" "$OUTPUT_FILE"
elif command -v yt-dlp &> /dev/null; then
    echo "使用yt-dlp下载视频..."
    yt-dlp -o "$OUTPUT_FILE" "$VIDEO_URL"
else
    echo "错误: 未找到可用的下载工具 (需要opencli或yt-dlp)" >&2
    exit 1
fi

# 尝试合并分离的音视频流
BASENAME="$(basename "$OUTPUT_FILE" | sed 's/\.[^.]*$//')"
merge_streams "$OUTPUT_DIR" "$BASENAME"

# 验证下载结果
ACTUAL_FILE="$(validate_download "$OUTPUT_DIR" "$OUTPUT_FILE")" || exit 1
FILE_SIZE="$(stat -c%s "$ACTUAL_FILE" 2>/dev/null || wc -c < "$ACTUAL_FILE" 2>/dev/null || echo 0)"
echo "下载完成: $ACTUAL_FILE (${FILE_SIZE} 字节)"

# 输出视频基础名称供后续步骤使用
echo ""
echo "VIDEO_BASENAME=$VIDEO_TITLE"
echo "OUTPUT_FILE=$ACTUAL_FILE"
