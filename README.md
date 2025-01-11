# MCP Web Browser Server

An advanced web browsing server for the Model Context Protocol (MCP) powered by Playwright, enabling headless browser interactions through a flexible, secure API.

## 🌐 Features

- **Headless Web Browsing**: Navigate to any website with SSL certificate validation bypass
- **Full Page Content Extraction**: Retrieve complete HTML content, including dynamically loaded JavaScript
- **Advanced Web Interaction Tools**:
  - Extract text content
  - Click page elements
  - Input text into form fields
  - Capture screenshots
  - Extract page links

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- MCP SDK
- Playwright

### Installation

```bash
# Install MCP and Playwright
pip install mcp playwright

# Install browser dependencies
playwright install
```

### Configuration for Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "web-browser": {
      "command": "python",
      "args": [
        "/path/to/your/server.py"
      ]
    }
  }
}
```

## 💡 Usage Examples

### Basic Web Navigation

```python
# Browse to a website
page_content = browse_to("https://example.com")

# Extract page text
text_content = extract_text_content()

# Extract text from a specific element
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
# Capture full page screenshot
full_page_screenshot = get_page_screenshots(full_page=True)

# Capture specific element screenshot
element_screenshot = get_page_screenshots(selector="#main-content")
```

### Link Extraction

```python
# Get all links on the page
page_links = get_page_links()
```

## 🛡️ Security Features

- SSL certificate validation bypass
- Secure browser context management
- Error handling and logging
- Configurable timeout settings

## 🔧 Troubleshooting

### Common Issues

- **SSL Certificate Errors**: Automatically bypassed
- **Slow Page Load**: Adjust timeout in `browse_to()` method
- **Element Not Found**: Verify selectors carefully

### Logging

All significant events are logged to stderr for easy debugging.

## 📋 Tool Parameters

### `browse_to(url: str, context: Optional[Any] = None)`
- `url`: Website to navigate to
- `context`: Optional context object (currently unused)

### `extract_text_content(selector: Optional[str] = None, context: Optional[Any] = None)`
- `selector`: Optional CSS selector to extract specific content
- `context`: Optional context object (currently unused)

### `click_element(selector: str, context: Optional[Any] = None)`
- `selector`: CSS selector of the element to click
- `context`: Optional context object (currently unused)

### `get_page_screenshots(full_page: bool = False, selector: Optional[str] = None, context: Optional[Any] = None)`
- `full_page`: Capture entire page screenshot
- `selector`: Optional element to screenshot
- `context`: Optional context object (currently unused)

### `get_page_links(context: Optional[Any] = None)`
- `context`: Optional context object (currently unused)

### `input_text(selector: str, text: str, context: Optional[Any] = None)`
- `selector`: CSS selector of input element
- `text`: Text to input
- `context`: Optional context object (currently unused)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-web-browser.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -e .[dev]
```

## 📄 License

MIT License

## 🔗 Related Projects

- [Model Context Protocol](https://modelcontextprotocol.io)
- [Playwright](https://playwright.dev)
- [Claude Desktop](https://claude.ai/desktop)

## 💬 Support

For issues and questions, please [open an issue](https://github.com/yourusername/mcp-web-browser/issues) on GitHub.
