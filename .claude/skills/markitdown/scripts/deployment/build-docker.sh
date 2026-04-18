#!/usr/bin/env bash
# Build markitdown-mcp Docker image
# Usage: bash build-docker.sh [IMAGE_TAG]
# IMAGE_TAG defaults to markitdown-mcp:latest

set -euo pipefail

IMAGE_TAG="${1:-markitdown-mcp:latest}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=== Building markitdown-mcp Docker image ==="
echo "Image tag: $IMAGE_TAG"
echo "Skill root: $SKILL_ROOT"

# Step 1: Clean up stale containers
echo ""
echo "--- Cleaning stale containers ---"
for container in markitdown-mcp-server markitdown-mcp-http markitdown-test markitdown-convert markitdown-conv; do
    docker rm -f "$container" 2>/dev/null || true
done

# Step 2: Check if valid image already exists
echo ""
echo "--- Checking existing image ---"
if docker inspect "$IMAGE_TAG" &>/dev/null; then
    echo "Image $IMAGE_TAG already exists."
    # Test if it can start
    if docker run --rm "$IMAGE_TAG" --help &>/dev/null; then
        echo "Existing image is valid. Skipping build."
        exit 0
    fi
    echo "Existing image is invalid. Rebuilding..."
    docker rmi "$IMAGE_TAG" 2>/dev/null || true
fi

# Step 3: Determine base image
echo ""
echo "--- Determining base image ---"
BASE_IMAGE=""

# Try to find a local Python slim image
for candidate in "python:3.11-slim" "python:3.12-slim" "python:3.13-slim" "python:3.10-slim"; do
    if docker inspect "$candidate" &>/dev/null; then
        BASE_IMAGE="$candidate"
        echo "Found local image: $BASE_IMAGE"
        break
    fi
done

if [ -z "$BASE_IMAGE" ]; then
    BASE_IMAGE="python:3.11-slim"
    echo "No local Python image found. Will pull $BASE_IMAGE."
fi

# Step 4: Create Dockerfile
echo ""
echo "--- Creating Dockerfile ---"
DOCKERFILE_DIR="${DOCKERFILE_DIR:-.}"
DOCKERFILE_PATH="$DOCKERFILE_DIR/Dockerfile"

cat > "$DOCKERFILE_PATH" <<EOF
FROM $BASE_IMAGE

ENV DEBIAN_FRONTEND=noninteractive
ENV EXIFTOOL_PATH=/usr/bin/exiftool
ENV FFMPEG_PATH=/usr/bin/ffmpeg
ENV MARKITDOWN_ENABLE_PLUGINS=True

# Runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libimage-exiftool-perl \
    && rm -rf /var/lib/apt/lists/*

# Install markitdown-mcp from PyPI
RUN pip install --no-cache-dir markitdown-mcp

WORKDIR /workdir

ARG USERID=nobody
ARG GROUPID=nogroup

USER \$USERID:\$GROUPID

ENTRYPOINT ["markitdown-mcp"]
EOF

echo "Dockerfile created at: $DOCKERFILE_PATH"

# Step 5: Build
echo ""
echo "--- Building image ---"
docker build -t "$IMAGE_TAG" "$DOCKERFILE_DIR"

echo ""
echo "=== Build complete ==="
echo "Image: $IMAGE_TAG"
docker images "$IMAGE_TAG"
