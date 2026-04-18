#!/usr/bin/env bash
# Configure Claude Code global MCP server for markitdown
# Usage: bash configure-mcp.sh [ATTACHMENTS_DIR]
# ATTACHMENTS_DIR defaults to current working directory's .vibe-attachments

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Resolve attachments directory
if [ $# -ge 1 ]; then
    ATTACHMENTS_DIR="$1"
else
    ATTACHMENTS_DIR="$(pwd)/.vibe-attachments"
fi

# Convert to absolute path with forward slashes (Docker on Windows requirement)
case "$(uname -s)" in
    CYGWIN*|MINGW*|MSYS*)
        # Windows: ensure forward slashes
        ATTACHMENTS_DIR="$(echo "$ATTACHMENTS_DIR" | sed 's/\\/\//g')"
        # Handle drive letter: /d/... -> D:/...
        if [[ "$ATTACHMENTS_DIR" =~ ^/([a-zA-Z])/ ]]; then
            DRIVE="${BASH_REMATCH[1]}"
            ATTACHMENTS_DIR="$(echo "$ATTACHMENTS_DIR" | sed "s|^/[a-zA-Z]/|${DRIVE}:/|")"
        fi
        ;;
esac

# Resolve to absolute path
ATTACHMENTS_DIR="$(cd "$(dirname "$ATTACHMENTS_DIR")" 2>/dev/null && pwd)/$(basename "$ATTACHMENTS_DIR")" || {
    echo "ERROR: Attachments directory does not exist: $ATTACHMENTS_DIR"
    exit 1
}

# Find Claude Code config file
CONFIG_FILE=""
for candidate in "$HOME/.claude.json" "$HOME/.claude/config.json"; do
    if [ -f "$candidate" ]; then
        CONFIG_FILE="$candidate"
        break
    fi
done

if [ -z "$CONFIG_FILE" ]; then
    echo "ERROR: Claude Code config file not found in $HOME/.claude.json or $HOME/.claude/config.json"
    exit 1
fi

echo "=== Configuring markitdown MCP server ==="
echo "Config file: $CONFIG_FILE"
echo "Attachments: $ATTACHMENTS_DIR"

# Check if markitdown already configured
if grep -q '"markitdown"' "$CONFIG_FILE" 2>/dev/null; then
    echo "markitdown MCP server already configured."
    echo "Current config:"
    $PYTHON_CMD -c "
import json, sys
try:
    with open('$CONFIG_FILE', 'r') as f:
        data = json.load(f)
    print(json.dumps(data.get('mcpServers', {}).get('markitdown', {}), indent=2))
except Exception as e:
    print(f'Error reading config: {e}')
    sys.exit(1)
" 2>/dev/null
    exit 0
fi

# Determine Python command
PYTHON_CMD=""
if [ -n "${PYTHON_PATH:-}" ] && [ -f "${PYTHON_PATH:-}" ]; then
    PYTHON_CMD="$PYTHON_PATH"
elif [ -n "${CONDA_PREFIX:-}" ] && [ -f "${CONDA_PREFIX}/bin/python" ]; then
    PYTHON_CMD="${CONDA_PREFIX}/bin/python"
else
    # Check conda environments on Windows
    for conda_py in \
        "$HOME/.conda/envs/picproject/python.exe" \
        "$HOME/anaconda3/python.exe" \
        "$HOME/miniconda3/python.exe" \
        ; do
        if [ -f "$conda_py" ]; then
            PYTHON_CMD="$conda_py"
            break
        fi
    done
    if [ -z "$PYTHON_CMD" ]; then
        for cmd in "python3" "python"; do
            if command -v "$cmd" &>/dev/null; then
                PYTHON_CMD="$cmd"
                break
            fi
        done
    fi
    # Windows: use where command
    if [ -z "$PYTHON_CMD" ] && command -v where &>/dev/null; then
        for search in "python3.exe" "python.exe"; do
            FOUND=$(where "$search" 2>/dev/null | head -1)
            if [ -n "$FOUND" ] && [ -f "$FOUND" ]; then
                PYTHON_CMD="$FOUND"
                break
            fi
        done
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "ERROR: No Python interpreter found. Set PYTHON_PATH env var."
    exit 1
fi

echo "Python: $PYTHON_CMD"

# Add markitdown MCP config
CLAUDE_CONFIG_PATH="$CONFIG_FILE" MCP_ATTACHMENTS_DIR="$ATTACHMENTS_DIR" $PYTHON_CMD -c "
import json, sys, os

config_path = os.environ['CLAUDE_CONFIG_PATH']
attachments = os.environ['MCP_ATTACHMENTS_DIR']

try:
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    print(f'ERROR: Failed to read config: {e}')
    sys.exit(1)

data.setdefault('mcpServers', {})['markitdown'] = {
    'command': 'docker',
    'args': [
        'run',
        '--rm',
        '-i',
        '-v',
        f'{attachments}:/workdir',
        'markitdown-mcp:latest'
    ]
}

try:
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print('MCP server configured successfully.')
    print(json.dumps(data['mcpServers']['markitdown'], indent=2))
except Exception as e:
    print(f'ERROR: Failed to write config: {e}')
    sys.exit(1)
"
