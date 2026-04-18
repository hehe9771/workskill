# MCP Protocol Specification for markitdown-mcp

## Protocol Version

`2024-11-05`

## Transport Modes

### STDIO (Default)

- Input/Output via stdin/stdout
- JSON-RPC 2.0 messages, one per line
- Used for Claude Code integration

### Streamable HTTP

- HTTP POST requests to `/mcp/` (trailing slash required)
- Content-Type: `application/json`
- Accept: `application/json, text/event-stream`

## Available Tools

### convert_to_markdown

Converts a file to Markdown format.

**Arguments:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| uri | string | Yes | File URI. Supports `file:`, `http:`, `https:`, `data:` schemes |

**Returns:**
- `content`: Array of content items
  - `type`: "text"
  - `text`: Markdown content string

**Example Request (HTTP):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "convert_to_markdown",
    "arguments": {"uri": "file:///workdir/document.docx"}
  }
}
```

**Example Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [{"type": "text", "text": "# Title\n\nContent..."}],
    "isError": false
  }
}
```

## Initialize Handshake

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "client", "version": "1.0"}
  }
}
```

## Known Issues

1. **URL encoding required**: Non-ASCII filenames must be URL-encoded in the URI
2. **Trailing slash**: HTTP endpoint requires `/mcp/` not `/mcp`
3. **File paths in Docker**: Files must be within the mounted `/workdir` directory
