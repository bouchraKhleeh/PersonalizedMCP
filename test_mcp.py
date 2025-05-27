#!/usr/bin/env python3
"""Test script to check MCP Server capabilities"""

import sys
from mcp.server import Server

# Create a server instance
server = Server("test-server")

# Check available attributes
print("=== MCP Server Attributes ===")
print(f"Python version: {sys.version}")
print(f"Server type: {type(server)}")
print(f"Server module: {server.__module__}")

# List all available methods and attributes
print("\n=== Available methods ===")
for attr in dir(server):
    if not attr.startswith('_'):
        print(f"- {attr}")

# Check specifically for tool-related methods
print("\n=== Tool-related methods ===")
tool_methods = ['tool', 'add_tool', 'list_tools', 'call_tool']
for method in tool_methods:
    if hasattr(server, method):
        print(f"✓ {method} is available")
    else:
        print(f"✗ {method} is NOT available")

# Try to get version info if available
try:
    import mcp
    if hasattr(mcp, '__version__'):
        print(f"\nMCP version: {mcp.__version__}")
except:
    pass