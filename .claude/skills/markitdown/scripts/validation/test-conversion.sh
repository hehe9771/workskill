#!/usr/bin/env bash
# Test markitdown-mcp conversion via MCP HTTP protocol
# Usage: bash test-conversion.sh <input_file_path> [output_dir]
#
# input_file_path: absolute path to the document file to convert
# output_dir: directory to save the output .md file (defaults to parent dir of input)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [ $# -lt 1 ]; then
    echo "Usage: bash test-conversion.sh <input_file_path> [output_dir]"
    echo ""
    echo "Example:"
    echo "  bash test-conversion.sh '/path/to/附件/审决会纪要.docx'"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_DIR="${2:-$(dirname "$INPUT_FILE")}"

if [ ! -f "$INPUT_FILE" ]; then
    echo "ERROR: Input file not found: $INPUT_FILE"
    exit 1
fi

FILENAME="$(basename "$INPUT_FILE")"
BASENAME="${FILENAME%.*}"
INPUT_DIR="$(dirname "$INPUT_FILE")"
OUTPUT_FILE="$OUTPUT_DIR/${BASENAME}.md"

# Convert to forward slashes for Docker (Windows path handling)
case "$(uname -s)" in
    CYGWIN*|MINGW*|MSYS*)
        INPUT_DIR="$(echo "$INPUT_DIR" | sed 's/\\/\//g')"
        if [[ "$INPUT_DIR" =~ ^/([a-zA-Z])/ ]]; then
            DRIVE="${BASH_REMATCH[1]}"
            INPUT_DIR="$(echo "$INPUT_DIR" | sed "s|^/[a-zA-Z]/|${DRIVE}:/|")"
        fi
        OUTPUT_DIR="$(echo "$OUTPUT_DIR" | sed 's/\\/\//g')"
        if [[ "$OUTPUT_DIR" =~ ^/([a-zA-Z])/ ]]; then
            DRIVE="${BASH_REMATCH[1]}"
            OUTPUT_DIR="$(echo "$OUTPUT_DIR" | sed "s|^/[a-zA-Z]/|${DRIVE}:/|")"
        fi
        OUTPUT_FILE="$OUTPUT_DIR/${BASENAME}.md"
        ;;
esac

# Determine Python command - check env var first, then common paths, then system
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
        "$HOME/miniconda3/envs/picproject/python.exe" \
        ; do
        if [ -f "$conda_py" ]; then
            PYTHON_CMD="$conda_py"
            break
        fi
    done

    # Fall back to system python3/python
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

# Port for temporary HTTP server
HTTP_PORT="${MCP_TEST_PORT:-3005}"
CONTAINER_NAME="markitdown-conv"

echo "=== Testing markitdown-mcp conversion ==="
echo "Input:  $INPUT_FILE"
echo "Output: $OUTPUT_FILE"
echo "Port:   $HTTP_PORT"

# Step 1: Clean up any existing containers
echo ""
echo "--- Cleaning up ---"
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

# Step 2: Start container in HTTP mode
echo ""
echo "--- Starting MCP server ---"
docker run --rm -d \
    --name "$CONTAINER_NAME" \
    -p "$HTTP_PORT:3001" \
    -v "${INPUT_DIR}:/workdir" \
    markitdown-mcp:latest \
    --http --host 0.0.0.0 --port 3001

# Wait for server to start
sleep 5

# Step 3: URL-encode the filename for MCP call
export INPUT_FILENAME="$FILENAME"
ENCODED_FILENAME=$($PYTHON_CMD -c "
import urllib.parse, os
filename = os.environ['INPUT_FILENAME']
encoded = urllib.parse.quote(filename, safe='')
print(encoded)
")
unset INPUT_FILENAME

echo "Original filename: $FILENAME"
echo "URL-encoded: $ENCODED_FILENAME"

# Step 4: Call MCP convert_to_markdown tool
echo ""
echo "--- Converting ---"
RESPONSE_FILE="$($PYTHON_CMD -c "import tempfile, os; print(tempfile.gettempdir())")/mcp_response_$$.json"

curl -s -X POST "http://127.0.0.1:${HTTP_PORT}/mcp/" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    --data-raw "{
    \"jsonrpc\": \"2.0\",
    \"id\": 1,
    \"method\": \"tools/call\",
    \"params\": {
        \"name\": \"convert_to_markdown\",
        \"arguments\": {\"uri\": \"file:///workdir/${ENCODED_FILENAME}\"}
    }
}" > "$RESPONSE_FILE"

# Step 5: Process response and save
echo ""
echo "--- Processing response ---"
MCP_RESPONSE_FILE="$RESPONSE_FILE" MCP_OUTPUT_FILE="$OUTPUT_FILE" PYTHONIOENCODING=utf-8 $PYTHON_CMD -c "
import json, sys, os

# Reconfigure stdout for Windows console compatibility
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

response_file = os.environ['MCP_RESPONSE_FILE']
output_file = os.environ['MCP_OUTPUT_FILE']

with open(response_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

if 'error' in data:
    print(f'ERROR: {json.dumps(data[\"error\"], ensure_ascii=False)}')
    sys.exit(1)

content = data['result']['content'][0]['text']
if not content or len(content.strip()) == 0:
    print('ERROR: Conversion returned empty content')
    sys.exit(1)

os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Output file: {output_file}')
print(f'Content length: {len(content)} characters')
print()
print('First 500 characters:')
print('=' * 50)
print(content[:500])
print('=' * 50)
"

# Cleanup
echo ""
echo "--- Cleaning up ---"
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
rm -f "$RESPONSE_FILE" 2>/dev/null || true

# Verify
echo ""
echo "--- Verification ---"
if [ -f "$OUTPUT_FILE" ] && [ -s "$OUTPUT_FILE" ]; then
    echo "SUCCESS: Output file exists and is non-empty"
    echo "File size: $(wc -c < "$OUTPUT_FILE") bytes"
    echo "Path: $OUTPUT_FILE"
    exit 0
else
    echo "FAILED: Output file is empty or does not exist"
    exit 1
fi
