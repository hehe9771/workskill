#!/bin/bash
# 从视频链接下载视频（使用 opencli 或 yt-dlp）
set -e

if [ $# -ne 2 ]; then
    echo "用法: $0 <video_url> <output_file>"
    exit 1
fi

VIDEO_URL="$1"
OUTPUT_FILE="$2"
OUTPUT_DIR="$(dirname "$OUTPUT_FILE")"
mkdir -p "$OUTPUT_DIR"

echo "正在下载视频: $VIDEO_URL"

# 查找 FFmpeg
find_ffmpeg() {
    if command -v ffmpeg &> /dev/null; then
        echo "ffmpeg"
        return
    fi
    local candidates=(
        "D:/mydoc/workskill/ffmpeg-8.0/bin/ffmpeg.exe"
        "/d/mydoc/workskill/ffmpeg-8.0/bin/ffmpeg.exe"
        "C:/Program Files/ffmpeg/bin/ffmpeg.exe"
    )
    for f in "${candidates[@]}"; do
        if [ -f "$f" ]; then
            echo "$f"
            return
        fi
    done
    echo ""
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
