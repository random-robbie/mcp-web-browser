"""Tests that do not need a browser: tool registration and naming."""

import asyncio

import pytest

from mcp_web_browser.server import mcp

EXPECTED_TOOLS = {
    "browse_to",
    "extract_text_content",
    "click_element",
    "get_page_screenshots",
    "get_page_links",
    "input_text",
}


def test_six_tools_registered():
    tools = asyncio.run(mcp.list_tools())
    names = {t.name for t in tools}
    assert names == EXPECTED_TOOLS


def test_tool_schemas_have_no_context_parameter():
    tools = asyncio.run(mcp.list_tools())
    for tool in tools:
        props = tool.inputSchema.get("properties", {})
        assert "context" not in props, f"{tool.name} still exposes a context parameter"


@pytest.mark.parametrize(
    "name,required",
    [
        ("browse_to", ["url"]),
        ("click_element", ["selector"]),
        ("input_text", ["selector", "text"]),
        ("get_page_links", []),
        ("extract_text_content", []),
        ("get_page_screenshots", []),
    ],
)
def test_required_parameters(name, required):
    tools = asyncio.run(mcp.list_tools())
    tool = next(t for t in tools if t.name == name)
    assert tool.inputSchema.get("required", []) == required
