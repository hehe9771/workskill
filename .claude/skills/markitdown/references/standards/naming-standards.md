# markitdown-mcp Standards

## Naming Conventions

- Docker image: `markitdown-mcp:latest`
- MCP server name in config: `markitdown`
- Container names (temporary): `markitdown-conv`, `markitdown-test`

## File Organization

- Input files must be in the mounted `/workdir` directory
- Output `.md` files use the same base name as the input (e.g., `report.docx` → `report.md`)

## Port Standards

- Default HTTP port in container: `3001`
- Temporary test ports: `3001`–`3010` (available range)
- Always clean up containers after use

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `MARKITDOWN_DOCKERFILE_DIR` | Directory for Dockerfile generation | Current directory |
| `MCP_TEST_PORT` | Port for temporary MCP HTTP server | 3005 |
| `PYTHON_PATH` | Python interpreter path for scripts | Auto-detected |

## Supported Formats

MarkItDown supports conversion from:
- Word documents (DOCX)
- PowerPoint presentations (PPTX)
- Excel spreadsheets (XLSX, XLS)
- PDF documents
- Images (with OCR)
- Audio files (with transcription)
- HTML, CSV, JSON, XML
- EPUB, Outlook messages
