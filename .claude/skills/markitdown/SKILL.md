---
name: markitdown
description: Builds markitdown-mcp Docker container, configures Claude Code MCP server, and converts documents (DOCX, PDF, PPTX, XLSX, etc.) to Markdown via Docker CLI. Zero hardcoding, cross-platform support, production-tested.
version: 2.0.0
source: production-experience
---

# markitdown Skill

## Skill Objective

Automates the complete markitdown-mcp document conversion pipeline:

1. **Docker Build** — Build a Docker container from markitdown-mcp PyPI package
2. **MCP Configuration** — Configure Claude Code global MCP server settings
3. **Document Conversion** — Convert documents to Markdown via Docker containerized CLI
4. **Validation** — Verify conversion success (non-empty output file)

Proven in production: converted 796 wind power project documents (345 successful, 48 archives, 403 failed due to scanned PDFs/size limits).

## Prerequisites

- Docker Desktop installed and running
- Claude Code installed with MCP support
- Python 3.10+ available (for test scripts)
- Network access to Docker Hub and PyPI
- (Optional) 7-Zip for RAR extraction (Windows)

## Execution Flow

### Phase 1: Docker Container Build

Run: `bash scripts/deployment/build-docker.sh`

1. Clean up stale containers
2. Find local Python base image (avoid pulling if possible)
3. Create Dockerfile from template (`assets/templates/code/dockerfile.tmpl`)
4. Build image as `markitdown-mcp:latest`
5. Verify image works

### Phase 2: MCP Configuration

Run: `bash scripts/setup/configure-mcp.sh [attachments_dir]`

1. Locate Claude Code config (`~/.claude.json`)
2. Check if markitdown already configured
3. Add markitdown MCP entry using template (`assets/templates/configs/mcp-config.tmpl`)
4. Validate JSON config

### Phase 3: Batch Document Conversion

Run: `python scripts/data-processing/convert-batch.py <source_directory>`

**This is the primary conversion method** (CLI mode, not HTTP).

1. Start persistent Docker container with volume mount to source directory
2. For each convertible file, execute `markitdown` CLI via `docker exec`
3. Capture stdout and save as `.md` adjacent to original
4. Archive files (zip/rar) are extracted in-container and internal files converted
5. Generate conversion report with success/fail/skip statistics

**Environment Variables (all optional):**

| Variable | Default | Description |
|----------|---------|-------------|
| MARKITDOWN_CONTAINER | markitdown-convert | Container name |
| MARKITDOWN_IMAGE | markitdown-mcp:latest | Docker image tag |
| CONVERSION_TIMEOUT | 120 | Per-file timeout (seconds) |
| MARKITDOWN_PORT | 8765 | Container HTTP port |

### Phase 4: Validation

Run: `bash scripts/validation/test-conversion.sh <file_or_directory>`

- Single file: test conversion of specific document
- Directory: scan all `.md` files, verify non-empty, report statistics

## Critical Production Lessons

### 1. MCP HTTP is Unreliable — Use CLI Mode

The MCP HTTP endpoint (`/mcp/`) has known issues:
- `RemoteDisconnected: Remote end closed connection`
- `HTTP 406: Not Acceptable` without specific headers
- SSE streaming instability

**Solution:** Always use CLI mode:
```bash
docker exec markitdown-convert markitdown "/workdir/file.pdf"
```

### 2. Windows Docker Path Requirements

Docker on Windows requires Linux-style paths:
- Use: `/d/mydoc/workskill/an/风电附件`
- Not: `D:\mydoc\workskill\an\风电附件`

From Git Bash, use `MSYS_NO_PATHCONV=1` to prevent path mangling.

### 3. Encoding: Always UTF-8

Windows defaults to GBK encoding. Always specify:
- Python: `sys.stdout.reconfigure(encoding='utf-8')`
- Subprocess: `encoding='utf-8', errors='replace'`

### 4. Volume Mount Required

Container MUST have volume mount to access host files:
```bash
docker run -d -v "/d/path:/workdir" --name markitdown-convert markitdown-mcp:latest
```

### 5. Scanned PDFs and Large Files

markitdown cannot extract text from:
- Image-based/scanned PDFs (require OCR)
- Very large files (>50MB may timeout)

These are expected failures, not bugs.

## Supported File Types

| Type | Extensions |
|------|-----------|
| Documents | pdf, docx, doc, pptx, ppt, xlsx, xls |
| Images | jpg, jpeg, png |
| Archives | zip, rar (extracted first) |

## Dependencies

| File | Purpose |
|------|---------|
| `scripts/deployment/build-docker.sh` | Docker image build |
| `scripts/setup/configure-mcp.sh` | MCP configuration |
| `scripts/data-processing/convert-batch.py` | Batch conversion (primary method) |
| `scripts/validation/test-conversion.sh` | Validation testing |
| `assets/templates/code/dockerfile.tmpl` | Docker build template |
| `assets/templates/configs/mcp-config.tmpl` | MCP config template |
| `references/specifications/mcp-protocol.md` | MCP protocol reference |

## Output Artifacts

| Artifact | Location |
|----------|----------|
| Docker image | Local registry: `markitdown-mcp:latest` |
| MCP config | `~/.claude.json` → `mcpServers.markitdown` |
| Markdown files | `<source>/**/*.md` (adjacent to originals) |
| Conversion report | `<source>/conversion-report.txt` |

## Success Criteria

1. Docker image `markitdown-mcp:latest` exists and responds to commands
2. `~/.claude.json` contains valid `markitdown` MCP entry
3. At least 60% of convertible documents produce non-empty `.md` files
4. Archives extracted and internal documents converted
5. Conversion report generated with statistics
