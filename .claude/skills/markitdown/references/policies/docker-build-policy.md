# markitdown-mcp Docker Build Policy

## Base Image Selection

1. **Prefer local images**: Check for cached Python slim images before pulling from Docker Hub
2. **Fallback order**: `python:3.11-slim` → `python:3.12-slim` → `python:3.13-slim` → pull required image
3. **Never use bullseye**: Debian bullseye repositories have connectivity issues; use bookworm or slim variants

## Dependency Installation

- Install `ffmpeg` and `libimage-exiftool-perl` (not `exiftool` package name on newer Debian)
- Always clean apt lists: `rm -rf /var/lib/apt/lists/*`
- Use `--no-cache-dir` for pip installs

## Security

- Run as non-root user (`nobody:nogroup`)
- Bind to localhost only when using HTTP mode
- Do not expose the server to non-localhost interfaces

## Image Verification

After build, verify the image can start:
```bash
docker run --rm markitdown-mcp:latest --help
```
