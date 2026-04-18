# markitdown-mcp Setup Procedure

## Step 1: Build Docker Image

Run the build script from the skill's `scripts/deployment/` directory:

```bash
bash scripts/deployment/build-docker.sh markitdown-mcp:latest
```

Or manually:
```bash
# Create Dockerfile in current directory
cat > Dockerfile <<'EOF'
FROM python:3.11-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg libimage-exiftool-perl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir markitdown-mcp
WORKDIR /workdir
USER nobody:nogroup
ENTRYPOINT ["markitdown-mcp"]
EOF

docker build -t markitdown-mcp:latest .
```

## Step 2: Configure Claude Code MCP

Run the configure script:
```bash
bash scripts/setup/configure-mcp.sh /path/to/.vibe-attachments
```

Or manually edit `~/.claude.json`:
```json
{
  "mcpServers": {
    "markitdown": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "/path/to/.vibe-attachments:/workdir", "markitdown-mcp:latest"]
    }
  }
}
```

## Step 3: Verify

```bash
bash scripts/validation/test-conversion.sh /path/to/.vibe-attachments/test.docx
```
