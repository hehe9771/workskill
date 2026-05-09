#!/usr/bin/env bash
# init-env.sh - 初始化 bfdata 环境变量
# 从模板生成 .env 文件，支持交互式填写或静默复制。

set -euo pipefail

# 从脚本位置推导技能根目录（跨平台）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

ENV_TEMPLATE="$SKILL_ROOT/assets/static/.env.tmpl"
ENV_OUTPUT="$SKILL_ROOT/assets/static/.env"
CONFIG_TEMPLATE="$SKILL_ROOT/assets/configs/backup-config.tmpl"
CONFIG_OUTPUT="$SKILL_ROOT/assets/configs/backup-config.json"

if [ -f "$ENV_OUTPUT" ]; then
    echo "[INFO] .env 文件已存在: $ENV_OUTPUT"
    echo "[INFO] 如需重新生成，请先删除现有文件"
    exit 0
fi

if [ ! -f "$ENV_TEMPLATE" ]; then
    echo "[ERROR] 模板文件不存在: $ENV_TEMPLATE" >&2
    exit 1
fi

# 复制模板
cp "$ENV_TEMPLATE" "$ENV_OUTPUT"
echo "[OK] 已生成 .env 文件: $ENV_OUTPUT"

# 生成配置文件
if [ ! -f "$CONFIG_OUTPUT" ]; then
    if [ -f "$CONFIG_TEMPLATE" ]; then
        cp "$CONFIG_TEMPLATE" "$CONFIG_OUTPUT"
        echo "[OK] 已生成配置文件: $CONFIG_OUTPUT"
    fi
fi

echo ""
echo "请编辑 $ENV_OUTPUT 填写以下变量："
echo "  - BFDATA_SOURCES          (备份源路径，JSON 数组)"
echo "  - BFDATA_OUTPUT_DIR       (输出目录)"
echo "  - BFDATA_COMPRESS_CMD     (压缩工具: 7z/tar/auto)"
echo "  - OSS_ENDPOINT            (OSS 端点，可选)"
echo "  - OSS_ACCESS_KEY_ID       (OSS AccessKey，可选)"
echo "  - OSS_ACCESS_KEY_SECRET   (OSS Secret，可选)"
echo "  - OSS_BUCKET              (OSS 存储桶，可选)"
echo ""
echo "然后运行: python scripts/data-processing/bfdata.py"
