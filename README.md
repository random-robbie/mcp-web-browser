# MCP Web Browser Server

An advanced web browsing server for the Model Context Protocol (MCP) powered by Playwright, enabling headless browser interactions through a flexible API.

<a href="https://glama.ai/mcp/servers/lwqlaw6k6d"><img width="380" height="200" src="https://glama.ai/mcp/servers/lwqlaw6k6d/badge" alt="Web Browser Server MCP server" /></a>

## Features

- **Headless Web Browsing**: Navigate to any website with SSL certificate validation bypass
- **Full Page Content Extraction**: Retrieve complete HTML content, including dynamically loaded JavaScript
- **Text Extraction**: Extract all visible text or text from specific elements
- **Web Interaction Tools**:
  - Click page elements
  - Input text into form fields
  - Capture screenshots (full page, viewport, or specific elements)
  - Extract page links
- **Resource Management**: Automatic cleanup of browser resources on shutdown

## Quick Start

### Prerequisites

- Python 3.10+
- Playwright (with Chromium installed)

### Installation

```bash
# Clone the repository
git clone https://github.com/random-robbie/mcp-web-browser.git
cd mcp-web-browser

# Install the package and its dependencies (mcp[cli] and playwright)
pip install -e .

# Install the Chromium browser binary
playwright install chromium
```

### Configuration for Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "web-browser": {
      "command": "mcp-web-browser"
    }
  }
}
```

Alternatively, you can run the server module directly:

```json
{
  "mcpServers": {
    "web-browser": {
      "command": "python",
      "args": ["-m", "mcp_web_browser.server"]
    }
  }
}
```

## Usage Examples

### Basic Web Navigation

```python
# Browse to a website (returns the full page HTML)
page_content = browse_to("https://example.com")

# Extract all visible page text
text_content = extract_text_content()

# Extract text from specific elements
title_text = extract_text_content("h1.title")
```

### Web Interaction

```python
# Navigate to a page
browse_to("https://example.com/login")

# Input text into a form
input_text("#username", "your_username")
input_text("#password", "your_password")

# Click a login button
click_element("#login-button")
```

### Screenshot Capture

```python
# Capture full page screenshot (returns PNG image content)
full_page_screenshot = get_page_screenshots(full_page=True)

# Capture viewport only
viewport_screenshot = get_page_screenshots()

# Capture a specific element
element_screenshot = get_page_screenshots(selector="#main-content")
```

### Link Extraction

```python
# Get all links on the current page
page_links = get_page_links()
```

## Security Features

- SSL certificate validation bypass (`ignore_https_errors=True` on the browser context)
- Configurable via environment variables: `MCP_BROWSER_UA` (custom User-Agent)
  and `MCP_BROWSER_VIEWPORT` (e.g. `1920x1080`)
- Browser resources closed and cleaned up on server shutdown

## Troubleshooting

### Common Issues

- **SSL Certificate Errors**: Automatically bypassed
- **Slow Page Load**: `browse_to()` uses a fixed 30-second timeout and waits for `networkidle`
- **Element Not Found**: Verify CSS selectors carefully; tools raise an error if no page is loaded, so call `browse_to()` first

### Logging

Significant events (navigation, extraction, errors, cleanup) are logged to stderr for easy debugging.

## Tool Parameters

### `browse_to(url: str, mode: str = "text")`
- `url`: Full URL to navigate to
- `mode`: `"text"` (default) returns the visible page text — cheaper for LLM
  use; `"html"` returns the full HTML content
- Returns the page content plus the current URL and page title

### `extract_text_content(selector: Optional[str] = None)`
- `selector`: Optional CSS selector to extract text from matching elements

### `click_element(selector: str)`
- `selector`: CSS selector of the element to click

### `get_page_screenshots(full_page: bool = False, selector: Optional[str] = None)`
- `full_page`: Capture the entire page rather than just the viewport
- `selector`: Optional CSS selector to screenshot a specific element
- Returns the screenshot as PNG image content

### `get_page_links()`
- Returns a list of `{"text": label, "href": absolute URL}` objects

### `input_text(selector: str, text: str)`
- `selector`: CSS selector of the input element
- `text`: Text to input

### `press_key(selector: str, key: str)`
- `selector`: CSS selector of the element to focus
- `key`: Key to press, e.g. `"Enter"` to submit a form, `"Escape"`, `"Tab"`
- Returns a confirmation plus the current URL and title (a key press may
  trigger navigation)

### `select_option(selector: str, values: str | list[str])`
- `selector`: CSS selector of the `<select>` dropdown
- `values`: Value or label to select (or a list for multi-select)
- Returns a confirmation plus the current URL and title

`click_element`, `input_text`, `press_key` and `select_option` all append the
current page URL and title to their result, so an agent can see where an
action landed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/random-robbie/mcp-web-browser.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -e .[dev]
```

## License

MIT License

## Related Projects

- [Model Context Protocol](https://modelcontextprotocol.io)
- [Playwright](https://playwright.dev)
- [Claude Desktop](https://claude.ai/desktop)

## Support

For issues and questions, please [open an issue](https://github.com/random-robbie/mcp-web-browser/issues) on GitHub.

## Author

Robbie Wiggins — [What-Security](https://www.what-security.co.uk) · [GitHub](https://github.com/random-robbie)
