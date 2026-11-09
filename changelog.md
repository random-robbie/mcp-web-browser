# Changelog

## 0.3.0

- Migrated to the mcp 2.x SDK: `FastMCP` is now `MCPServer`
  (`from mcp.server.mcpserver import MCPServer`), dependency updated to
  `mcp[cli]>=2,<3`.
- Tool errors are raised as `ToolError`, which the 2.x SDK surfaces as proper
  `CallToolResult(is_error=True)` results — the v1 behaviour, verified over a
  live stdio session.
- `Tool.inputSchema` renamed to `input_schema` in the SDK; tests updated.
- Verified end-to-end over stdio: initialize, list_tools and call_tool error
  handling against the 2.3.0 client.

## 0.2.0

- Removed the phantom `context` parameter from every tool signature and schema.
- `get_page_screenshots` now returns proper MCP image content instead of a
  base64-encoded string.
- Pinned dependencies: `mcp[cli]>=1.9,<2` (the 2.x SDK renamed FastMCP to
  MCPServer — migrate before unpinning) and `playwright>=1.49,<2`.
- Added a test suite (tool registration, schemas, required parameters) and a
  GitHub Actions CI workflow running ruff and pytest.
- Ran ruff across the codebase; lint is now clean.
- Corrected documentation that previously described features the server never
  had (multi-tab management, CSP bypass, custom user agents, JavaScript
  execution restrictions, inactivity timeouts, retry logic, JPEG
  compression). The server has six tools: browse_to, extract_text_content,
  click_element, get_page_screenshots, get_page_links and input_text.

## 0.1.0

- Initial release: Playwright-powered MCP server with six browser tools,
  a single shared browser context with SSL validation bypassed, and
  cleanup on server shutdown.
