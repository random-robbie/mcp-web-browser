from typing import Optional, Union, Any
import asyncio
import base64
import sys
from mcp.server import FastMCP

# Create an MCP server for web browsing
mcp = FastMCP("Web Browser")

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
        _browser_context = await _browser.new_context(
            ignore_https_errors=True,  # Ignore SSL certificate errors
        )
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
async def browse_to(url: str, context: Optional[Any] = None) -> str:
    """
    Navigate to a specific URL and return the page's HTML content.
    
    Args:
        url: The full URL to navigate to
        context: Optional context object for logging (ignored)
    
    Returns:
        The full HTML content of the page
    """
    global _current_page, _browser, _browser_context
    
    # Ensure browser is launched with SSL validation disabled
    _, browser_context = await _ensure_browser()
    
    # Close any existing page
    await _close_current_page()
    
    # Optional logging, but do nothing with context
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
        page_content = await _current_page.content()
        
        # Optional: extract additional metadata
        try:
            title = await _current_page.title()
            print(f"Page title: {title}", file=sys.stderr)
        except Exception:
            pass
        
        return page_content
    
    except Exception as e:
        print(f"Error navigating to {url}: {e}", file=sys.stderr)
        raise

@mcp.tool()
async def extract_text_content(
    selector: Optional[str] = None, 
    context: Optional[Any] = None
) -> str:
    """
    Extract text content from the current page, optionally using a CSS selector.
    
    Args:
        selector: Optional CSS selector to target specific elements
        context: Optional context object for logging (ignored)
    
    Returns:
        Extracted text content
    """
    global _current_page
    
    if not _current_page:
        raise ValueError("No page is currently loaded. Use browse_to first.")
    
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
        raise ValueError(f"Error extracting text: {e}")

@mcp.tool()
async def click_element(
    selector: str, 
    context: Optional[Any] = None
) -> str:
    """
    Click an element on the current page.
    
    Args:
        selector: CSS selector for the element to click
        context: Optional context object for logging (ignored)
    
    Returns:
        Confirmation message or error details
    """
    global _current_page
    
    if not _current_page:
        raise ValueError("No page is currently loaded. Use browse_to first.")
    
    try:
        element = await _current_page.query_selector(selector)
        if not element:
            raise ValueError(f"No element found with selector: {selector}")
        
        await element.click()
        print(f"Clicked element: {selector}", file=sys.stderr)
        
        return f"Successfully clicked element: {selector}"
    
    except Exception as e:
        print(f"Error clicking element: {e}", file=sys.stderr)
        raise ValueError(f"Error clicking element: {e}")

@mcp.tool()
async def get_page_screenshots(
    full_page: bool = False, 
    selector: Optional[str] = None,
    context: Optional[Any] = None
) -> str:
    """
    Capture screenshot of the current page.
    
    Args:
        full_page: Whether to capture the entire page or just the viewport
        selector: Optional CSS selector to screenshot a specific element
        context: Optional context object for logging (ignored)
    
    Returns:
        Base64 encoded screenshot image
    """
    global _current_page
    
    if not _current_page:
        raise ValueError("No page is currently loaded. Use browse_to first.")
    
    try:
        if selector:
            element = await _current_page.query_selector(selector)
            if not element:
                raise ValueError(f"No element found with selector: {selector}")
            screenshot_bytes = await element.screenshot()
        else:
            screenshot_bytes = await _current_page.screenshot(full_page=full_page)
        
        # Convert to base64 for easy transmission
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        
        print(f"Screenshot captured: {'full page' if full_page else 'viewport'}", file=sys.stderr)
        
        return screenshot_base64
    
    except Exception as e:
        print(f"Error capturing screenshot: {e}", file=sys.stderr)
        raise ValueError(f"Error capturing screenshot: {e}")

@mcp.tool()
async def get_page_links(context: Optional[Any] = None) -> list[str]:
    """
    Extract all links from the current page.
    
    Args:
        context: Optional context object for logging (ignored)
    
    Returns:
        List of links found on the page
    """
    global _current_page
    
    if not _current_page:
        raise ValueError("No page is currently loaded. Use browse_to first.")
    
    try:
        # Use JavaScript to extract all links
        links = await _current_page.evaluate("""
            () => {
                const links = document.querySelectorAll('a');
                return Array.from(links).map(link => link.href);
            }
        """)
        
        print(f"Extracted {len(links)} links from the page", file=sys.stderr)
        
        return links
    
    except Exception as e:
        print(f"Error extracting links: {e}", file=sys.stderr)
        raise ValueError(f"Error extracting links: {e}")

@mcp.tool()
async def input_text(
    selector: str, 
    text: str, 
    context: Optional[Any] = None
) -> str:
    """
    Input text into a specific element on the page.
    
    Args:
        selector: CSS selector for the input element
        text: Text to input
        context: Optional context object for logging (ignored)
    
    Returns:
        Confirmation message
    """
    global _current_page
    
    if not _current_page:
        raise ValueError("No page is currently loaded. Use browse_to first.")
    
    try:
        element = await _current_page.query_selector(selector)
        if not element:
            raise ValueError(f"No element found with selector: {selector}")
        
        await element.fill(text)
        
        print(f"Input text into element: {selector}", file=sys.stderr)
        
        return f"Successfully input text into element: {selector}"
    
    except Exception as e:
        print(f"Error inputting text: {e}", file=sys.stderr)
        raise ValueError(f"Error inputting text: {e}")

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
