# Changelog

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
