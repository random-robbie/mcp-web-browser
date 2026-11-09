import asyncio
import os
import sys

from mcp.server.mcpserver import Image, MCPServer
from mcp.server.mcpserver.tools.base import ToolError

# Create an MCP server for web browsing
mcp = MCPServer("Web Browser")

# Global browser and page management
_browser = None
_browser_context = None
_current_page = None
_playwright_instance = None

# Dynamic import of Playwright to avoid early import errors
def _import_playwright():
    from playwright.async_api import async_playwright
    return async_playwright

async def _ensure_browser():
    """Ensure a browser instance is available with SSL validation disabled"""
    global _browser, _browser_context, _playwright_instance

    if _browser is None:
        playwright_module = _import_playwright()
        _playwright_instance = await playwright_module().start()
        _browser = await _playwright_instance.chromium.launch()

        # Create a browser context that ignores HTTPS errors
        context_kwargs: dict = {
            "ignore_https_errors": True,  # Ignore SSL certificate errors
        }
        user_agent = os.environ.get("MCP_BROWSER_UA")
        if user_agent:
            context_kwargs["user_agent"] = user_agent
        viewport = os.environ.get("MCP_BROWSER_VIEWPORT")
        if viewport:
            width, _, height = viewport.lower().partition("x")
            context_kwargs["viewport"] = {"width": int(width), "height": int(height)}
        _browser_context = await _browser.new_context(**context_kwargs)
    return _browser, _browser_context

async def _close_current_page():
    """Close the current page if it exists"""
    global _current_page
    if _current_page:
        try:
            await _current_page.close()
        except Exception:
            pass
        _current_page = None

async def _page_summary() -> str:
    """Return the current URL and title so agents can see where an action landed."""
    if not _current_page:
        return ""
    try:
        return f" [page: {_current_page.url} | {await _current_page.title()}]"
    except Exception:
        return ""

async def _safe_cleanup():
    """Safely clean up browser resources"""
    global _browser, _current_page, _browser_context, _playwright_instance

    try:
        if _current_page:
            try:
                await _current_page.close()
            except Exception:
                pass

        if _browser_context:
            try:
                await _browser_context.close()
            except Exception:
                pass

        if _browser:
            try:
                await _browser.close()
            except Exception:
                pass

        if _playwright_instance:
            try:
                await _playwright_instance.stop()
            except Exception:
                pass
    except Exception as e:
        # Log the error, but don't re-raise
        print(f"Error during cleanup: {e}", file=sys.stderr)
    finally:
        # Reset global variables
        _browser = None
        _browser_context = None
        _current_page = None
        _playwright_instance = None

@mcp.tool()
async def browse_to(url: str, mode: str = "text") -> str:
    """
    Navigate to a specific URL and return the page's text or HTML content.

    Args:
        url: The full URL to navigate to
        mode: "text" returns the visible text of the page (default, cheaper
            for LLM use); "html" returns the full HTML content

    Returns:
        The page content in the requested mode, plus the current URL and title
    """
    global _current_page, _browser, _browser_context

    # Ensure browser is launched with SSL validation disabled
    _, browser_context = await _ensure_browser()

    # Close any existing page
    await _close_current_page()

    print(f"Navigating to {url}", file=sys.stderr)

    try:
        # Create a new page and navigate
        _current_page = await browser_context.new_page()

        # Additional options to handle various SSL/security issues
        await _current_page.goto(url,
            wait_until='networkidle',
            timeout=30000,  # 30 seconds timeout
        )

        # Get full page content including dynamically loaded JavaScript
        if mode == "text":
            page_content = await _current_page.inner_text("body")
        elif mode == "html":
            page_content = await _current_page.content()
        else:
            raise ToolError(f"unknown mode {mode!r}: use 'text' or 'html'")

        # Optional: extract additional metadata
        try:
            title = await _current_page.title()
            print(f"Page title: {title}", file=sys.stderr)
        except Exception:
            pass

        return page_content + await _page_summary()

    except Exception as e:
        print(f"Error navigating to {url}: {e}", file=sys.stderr)
        raise

@mcp.tool()
async def extract_text_content(
    selector: str | None = None,
) -> str:
    """
    Extract text content from the current page, optionally using a CSS selector.

    Args:
        selector: Optional CSS selector to target specific elements

    Returns:
        Extracted text content
    """
    global _current_page

    if not _current_page:
        raise ToolError("No page is currently loaded. Use browse_to first.")

    try:
        if selector:
            # If selector is provided, extract text from matching elements
            elements = await _current_page.query_selector_all(selector)
            text_content = "\n".join([await el.inner_text() for el in elements])
            print(f"Extracted text from selector: {selector}", file=sys.stderr)
        else:
            # If no selector, extract all visible text from the page
            text_content = await _current_page.inner_text('body')

        return text_content

    except Exception as e:
        print(f"Error extracting text: {e}", file=sys.stderr)
        raise ToolError(f"Error extracting text: {e}")

@mcp.tool()
async def click_element(
    selector: str,
) -> str:
    """
    Click an element on the current page.

    Args:
        selector: CSS selector for the element to click

    Returns:
        Confirmation message or error details
    """
    global _current_page

    if not _current_page:
        raise ToolError("No page is currently loaded. Use browse_to first.")

    try:
        element = await _current_page.query_selector(selector)
        if not element:
            raise ToolError(f"No element found with selector: {selector}")

        await element.click()
        print(f"Clicked element: {selector}", file=sys.stderr)

        return f"Successfully clicked element: {selector}"

    except Exception as e:
        print(f"Error clicking element: {e}", file=sys.stderr)
        raise ToolError(f"Error clicking element: {e}")

@mcp.tool()
async def get_page_screenshots(
    full_page: bool = False,
    selector: str | None = None
):
    """
    Capture screenshot of the current page.

    Args:
        full_page: Whether to capture the entire page or just the viewport
        selector: Optional CSS selector to screenshot a specific element

    Returns:
        The screenshot as PNG image content
    """
    global _current_page

    if not _current_page:
        raise ToolError("No page is currently loaded. Use browse_to first.")

    try:
        if selector:
            element = await _current_page.query_selector(selector)
            if not element:
                raise ToolError(f"No element found with selector: {selector}")
            screenshot_bytes = await element.screenshot()
        else:
            screenshot_bytes = await _current_page.screenshot(full_page=full_page)

        print(f"Screenshot captured: {'full page' if full_page else 'viewport'}", file=sys.stderr)

        return Image(data=screenshot_bytes, format='png')

    except Exception as e:
        print(f"Error capturing screenshot: {e}", file=sys.stderr)
        raise ToolError(f"Error capturing screenshot: {e}")

@mcp.tool()
async def get_page_links() -> list[dict[str, str]]:
    """
    Extract all links from the current page with their labels.

    Returns:
        List of {"text": link label, "href": absolute URL} objects
    """
    global _current_page

    if not _current_page:
        raise ToolError("No page is currently loaded. Use browse_to first.")

    try:
        # Use JavaScript to extract links with their labels
        links = await _current_page.evaluate("""
            () => {
                const links = document.querySelectorAll('a');
                return Array.from(links).map(link => ({
                    text: (link.textContent || '').trim(),
                    href: link.href,
                }));
            }
        """)

        print(f"Extracted {len(links)} links from the page", file=sys.stderr)

        return links

    except Exception as e:
        print(f"Error extracting links: {e}", file=sys.stderr)
        raise ToolError(f"Error extracting links: {e}")

@mcp.tool()
async def input_text(
    selector: str,
    text: str,
) -> str:
    """
    Input text into a specific element on the page.

    Args:
        selector: CSS selector for the input element
        text: Text to input

    Returns:
        Confirmation message
    """
    global _current_page

    if not _current_page:
        raise ToolError("No page is currently loaded. Use browse_to first.")

    try:
        element = await _current_page.query_selector(selector)
        if not element:
            raise ToolError(f"No element found with selector: {selector}")

        await element.fill(text)

        print(f"Input text into element: {selector}", file=sys.stderr)

        return f"Successfully input text into element: {selector}" + await _page_summary()

    except Exception as e:
        print(f"Error inputting text: {e}", file=sys.stderr)
        raise ToolError(f"Error inputting text: {e}")

@mcp.tool()
async def press_key(selector: str, key: str) -> str:
    """
    Focus an element and press a keyboard key on it, e.g. "Enter" to submit
    a form, "Escape", "Tab", "ArrowDown". Use this to submit search boxes and
    forms that submit on Enter.

    Args:
        selector: CSS selector of the element to focus
        key: Key name as accepted by Playwright, e.g. "Enter", "Tab", "Escape"

    Returns:
        Confirmation message plus the current page URL and title (the key
        press may trigger navigation)
    """
    global _current_page

    if not _current_page:
        raise ToolError("No page is currently loaded. Use browse_to first.")

    try:
        element = await _current_page.query_selector(selector)
        if not element:
            raise ToolError(f"No element found with selector: {selector}")

        await element.press(key)

        print(f"Pressed {key} on element: {selector}", file=sys.stderr)

        return f"Successfully pressed {key} on element: {selector}" + await _page_summary()

    except ToolError:
        raise
    except Exception as e:
        print(f"Error pressing key: {e}", file=sys.stderr)
        raise ToolError(f"Error pressing key: {e}")

@mcp.tool()
async def select_option(selector: str, values: str | list[str]) -> str:
    """
    Select one or more options in a <select> dropdown element. Options are
    matched by value or label.

    Args:
        selector: CSS selector of the <select> element
        values: A single value/label or a list of values/labels to select

    Returns:
        Confirmation message plus the current page URL and title
    """
    global _current_page

    if not _current_page:
        raise ToolError("No page is currently loaded. Use browse_to first.")

    try:
        element = await _current_page.query_selector(selector)
        if not element:
            raise ToolError(f"No element found with selector: {selector}")

        selected = await element.select_option(values)

        print(f"Selected options in element: {selector}", file=sys.stderr)

        return f"Successfully selected options in element: {selector} ({len(selected)} selected)" + await _page_summary()

    except ToolError:
        raise
    except Exception as e:
        print(f"Error selecting options: {e}", file=sys.stderr)
        raise ToolError(f"Error selecting options: {e}")

def main():
    try:
        mcp.run()
    except Exception as e:
        print(f"Error running MCP server: {e}", file=sys.stderr)
    finally:
        # Use a separate event loop to ensure cleanup
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_safe_cleanup())
            loop.close()
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}", file=sys.stderr)

if __name__ == "__main__":
    main()
