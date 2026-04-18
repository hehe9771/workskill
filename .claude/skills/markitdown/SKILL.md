---
name: markitdown
description: Builds markitdown-mcp Docker container, configures Claude Code MCP server, and converts documents (DOCX, PDF, PPTX, XLSX, etc.) to Markdown via MCP protocol.
---

# markitdown Skill

## Skill Objective

Automates the complete markitdown-mcp pipeline:
1. Build a Docker container from the official Microsoft markitdown repository
2. Configure Claude Code global MCP server settings
3. Convert uploaded document attachments to Markdown via MCP protocol
4. Validate conversion success (non-empty output file)

## Prerequisites

- Docker Desktop installed and running
- Claude Code installed with MCP support
- Python 3.10+ available (for test scripts)
- Network access to Docker Hub and PyPI

## Execution Flow

### Phase 1: Docker Container Build

1. Check if `markitdown-mcp:latest` image already exists and is valid
2. If not, create a Dockerfile in the current working directory based on the official markitdown-mcp Dockerfile template
3. Clean up any stale containers (`markitdown-convert`, `markitdown-test`, etc.)
4. Build the Docker image using an existing local Python base image if available, otherwise pull from Docker Hub
5. Verify the built image can start and respond to MCP initialize requests

### Phase 2: Claude Code MCP Configuration

1. Locate the Claude Code global config file (`~/.claude.json` on all platforms)
2. Check if `markitdown` MCP server is already configured
3. If not, add a new `markitdown` entry that:
   - Runs Docker container with STDIO transport
   - Mounts the project's `.vibe-attachments` directory to `/workdir` in the container
   - Uses the `markitdown-mcp:latest` image
4. Validate the JSON config is valid after modification

### Phase 3: Document Conversion

1. Start a temporary Docker container in HTTP mode with port mapping
2. Call the `convert_to_markdown` tool via MCP HTTP endpoint
3. Use URL-encoded filenames for non-ASCII characters (Chinese, etc.)
4. Save the resulting Markdown content to the `.vibe-attachments` directory
5. Verify the output file is non-empty
6. Clean up the temporary container and temp files

## Key Troubleshooting Notes

### Known Issues (保留踩坑经验)

1. **Docker Hub network issues**: If `python:3.13-slim-bullseye` fails to pull (connection timeout), fall back to any locally cached Python image (e.g., `python:3.11-slim`). Check with `docker images python:*`.

2. **Chinese filename encoding**: When calling MCP tools with Chinese filenames in the URI, the HTTP endpoint may fail with `'utf-8' codec can't decode byte` errors. **Solution**: URL-encode the filename (e.g., `审决会纪要.docx` → `%E5%AE%A1%E5%86%B3%E4%BC%9A%E7%BA%AA%E8%A6%81.docx`).

3. **Docker volume path format on Windows**: Docker on Windows requires absolute paths for volume mounts. Relative paths like `.vibe-attachments` will fail. **Solution**: Always resolve to absolute path before mounting. Use forward slashes (`D:/path/to/dir`).

4. **Container port mapping**: For HTTP-based testing, ensure port is mapped (`-p HOST_PORT:CONTAINER_PORT`). Without port mapping, `curl` to `127.0.0.1:PORT` will get "Connection refused".

5. **MCP HTTP endpoint path**: The markitdown-mcp HTTP server returns a 307 redirect from `/mcp` to `/mcp/` (with trailing slash). **Solution**: Always include the trailing slash in URLs.

6. **pip SSL errors during build**: The `pip install` step may show SSL errors for pypi.org but still succeed. These warnings can be ignored if the install completes.

7. **Windows console encoding**: When processing MCP responses on Windows, Python's default `gbk` encoding may fail on Unicode characters. **Solution**: Always use `encoding='utf-8'` when opening files and `ensure_ascii=False` when dumping JSON.

## Inputs

| Parameter | Description | Required |
|-----------|-------------|----------|
| File path | Path to document to convert | Yes (for conversion step) |
| Output dir | Directory to save converted files | No (defaults to `.vibe-attachments`) |
| Docker tag | Docker image tag | No (defaults to `markitdown-mcp:latest`) |

## Dependencies

| File | Path (relative to skill root) | Purpose |
|------|-------------------------------|---------|
| Dockerfile template | `assets/templates/code/dockerfile.tmpl` | Docker build recipe |
| Build script | `scripts/deployment/build-docker.sh` | Build Docker image |
| Configure script | `scripts/setup/configure-mcp.sh` | Configure Claude Code MCP |
| Test script | `scripts/validation/test-conversion.sh` | Validate conversion |
| MCP protocol spec | `references/specifications/mcp-protocol.md` | Protocol reference |

## Output Artifacts

| Artifact | Location | Description |
|----------|----------|-------------|
| Docker image | Docker local registry (`markitdown-mcp:latest`) | Built container image |
| MCP config | `~/.claude.json` (mcpServers.markitdown) | Global MCP server config |
| Markdown file | `.vibe-attachments/{original_name}.md` | Converted document |

## Success Criteria

1. Docker image `markitdown-mcp:latest` exists and can respond to MCP initialize
2. `~/.claude.json` contains a valid `markitdown` MCP server entry
3. Converted `.md` file exists and is non-empty
4. MCP protocol communication succeeds (no encoding or connection errors)
