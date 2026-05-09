#!/usr/bin/env bash
# validate-backup.sh - 验证备份归档完整性
# 检查归档文件是否存在、大小合理、可解压。

set -euo pipefail

ARCHIVE_PATH="${1:-}"

if [ -z "$ARCHIVE_PATH" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    SKILL_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
    BACKUP_DIR="${BFDATA_OUTPUT_DIR:-$SKILL_ROOT/../backup}"

    LATEST=$(find "$BACKUP_DIR" -name "bfdata-backup-*" -type f 2>/dev/null | sort -r | head -1)
    if [ -z "$LATEST" ]; then
        echo "[ERROR] 未找到备份归档" >&2
        exit 1
    fi
    ARCHIVE_PATH="$LATEST"
fi

# 通过环境变量传递路径（避免 Windows 路径转义问题）
export _BFDATA_ARCHIVE_PATH="$ARCHIVE_PATH"
PYTHON_CMD="${BFDATA_PYTHON:-python}"

$PYTHON_CMD -c "
import os, sys, tarfile

path = os.environ['_BFDATA_ARCHIVE_PATH']

if not os.path.isfile(path):
    print(f'[FAIL] 文件不存在: {path}')
    sys.exit(1)

size = os.path.getsize(path)
if size == 0:
    print('[FAIL] 归档为空')
    sys.exit(1)

mb = round(size / 1048576, 1)
print(f'[OK] 文件大小: {mb} MB')

try:
    with tarfile.open(path, 'r:gz') as t:
        members = t.getmembers()
        print(f'[OK] 归档条目: {len(members)} 个文件')
        top = sorted(set(m.name.split('/')[0] for m in members))
        print(f'[OK] 备份源: {\", \".join(top)}')
except Exception as e:
    print(f'[FAIL] 归档损坏: {e}')
    sys.exit(1)

print(f'[OK] 备份验证通过: {path}')
" 2>&1
