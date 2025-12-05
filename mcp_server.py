#!/usr/bin/env python3
"""
Splunk SOAR MCP Server
Connect AI assistants to any Splunk SOAR instance with configurable credentials.

Usage:
    Set environment variables:
        - SPLUNK_SOAR_URL: Base URL of your Splunk SOAR instance (e.g., https://your-soar.example.com)
            - SPLUNK_SOAR_TOKEN: Your Splunk SOAR API authentication token

                    Run: python mcp_server.py
                    """

import os
import json
import urllib.request
import urllib.error
import ssl
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server


# Get configuration from environment variables
SPLUNK_URL = os.getenv("SPLUNK_SOAR_URL", "").rstrip("/")
SPLUNK_TOKEN = os.getenv("SPLUNK_SOAR_TOKEN", "")

# Create SSL context that doesn't verify certificates (for self-signed certs)
ssl_context = ssl.create_unverified_context()


def soar_api_request(endpoint: str, method: str = "GET", data: dict = None) -> dict:
      """Make an API request to Splunk SOAR."""
      if not SPLUNK_URL or not SPLUNK_TOKEN:
                raise ValueError("SPLUNK_SOAR_URL and SPLUNK_SOAR_TOKEN environment variables must be set")

      url = f"{SPLUNK_URL}/rest{endpoint}"
      headers = {
          "ph-auth-token": SPLUNK_TOKEN,
          "Content-Type": "application/json"
      }

    request_data = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=request_data, headers=headers, method=method)

    try:
              with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
                            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
              error_body = e.read().decode() if e.fp else str(e)
              raise Exception(f"API Error {e.code}: {error_body}")
except urllib.error.URLError as e:
          raise Exception(f"Connection Error: {e.reason}")


# Create the MCP server
server = Server("splunk-soar-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
      """List available tools for Splunk SOAR integration."""
      return [
          Tool(
              name="test_connection",
              description="Test the connection to Splunk SOAR instance",
              inputSchema={
                  "type": "object",
                  "properties": {},
                  "required": []
              }
          ),
          Tool(
              name="list_containers",
              description="List containers (incidents/cases) in Splunk SOAR",
              inputSchema={
                  "type": "object",
                  "properties": {
                      "page": {"type": "integer", "description": "Page number (default: 0)"},
                      "page_size": {"type": "integer", "description": "Results per page (default: 10)"}
                  },
                  "required": []
              }
          ),
          Tool(
              name="get_container",
              description="Get details of a specific container by ID",
              inputSchema={
                  "type": "object",
                  "properties": {
                      "container_id": {"type": "integer", "description": "Container ID"}
                  },
                  "required": ["container_id"]
              }
          ),
          Tool(
              name="list_playbooks",
              description="List available playbooks in Splunk SOAR",
              inputSchema={
                  "type": "object",
                  "properties": {},
                  "required": []
              }
          ),
          Tool(
              name="run_playbook",
              description="Run a playbook on a container",
              inputSchema={
                  "type": "object",
                  "properties": {
                      "playbook_id": {"type": "integer", "description": "Playbook ID to run"},
                      "container_id": {"type": "integer", "description": "Container ID to run playbook on"},
                      "scope": {"type": "string", "description": "Scope: 'all' or 'new' (default: 'all')"}
                  },
                  "required": ["playbook_id", "container_id"]
              }
          ),
          Tool(
              name="list_actions",
              description="List available actions in Splunk SOAR",
              inputSchema={
                  "type": "object",
                  "properties": {},
                  "required": []
              }
          ),
          Tool(
              name="get_action_run",
              description="Get the status and results of an action run",
              inputSchema={
                  "type": "object",
                  "properties": {
                      "action_run_id": {"type": "integer", "description": "Action Run ID"}
                  },
                  "required": ["action_run_id"]
              }
          ),
          Tool(
              name="list_assets",
              description="List configured assets in Splunk SOAR",
              inputSchema={
                  "type": "object",
                  "properties": {},
                  "required": []
              }
          ),
          Tool(
              name="get_system_info",
              description="Get Splunk SOAR system information",
              inputSchema={
                  "type": "object",
                  "properties": {},
                  "required": []
              }
          )
      ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
      """Execute a tool and return the result."""
      try:
                if name == "test_connection":
                              result = soar_api_request("/version")
                              return [TextContent(type="text", text=f"Connection successful! SOAR Version: {json.dumps(result, indent=2)}")]

                elif name == "list_containers":
                              page = arguments.get("page", 0)
                              page_size = arguments.get("page_size", 10)
                              result = soar_api_request(f"/container?page={page}&page_size={page_size}")
                              return [TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "get_container":
                              container_id = arguments["container_id"]
                              result = soar_api_request(f"/container/{container_id}")
                              return [TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "list_playbooks":
                              result = soar_api_request("/playbook?page_size=100")
                              return [TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "run_playbook":
                              playbook_id = arguments["playbook_id"]
                              container_id = arguments["container_id"]
                              scope = arguments.get("scope", "all")
                              data = {
                                  "container_id": container_id,
                                  "playbook_id": playbook_id,
                                  "scope": scope,
                                  "run": True
                              }
                              result = soar_api_request("/playbook_run", method="POST", data=data)
                              return [TextContent(type="text", text=f"Playbook started: {json.dumps(result, indent=2)}")]

                elif name == "list_actions":
                              result = soar_api_request("/action?page_size=100")
                              return [TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "get_action_run":
                              action_run_id = arguments["action_run_id"]
                              result = soar_api_request(f"/action_run/{action_run_id}")
                              return [TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "list_assets":
                              result = soar_api_request("/asset?page_size=100")
                              return [TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "get_system_info":
                              result = soar_api_request("/system_info")
                              return [TextContent(type="text", text=json.dumps(result, indent=2))]

                else:
                              return [TextContent(type="text", text=f"Unknown tool: {name}")]

except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
      """Run the MCP server."""
      if not SPLUNK_URL:
                print("Warning: SPLUNK_SOAR_URL environment variable not set")
            if not SPLUNK_TOKEN:
                      print("Warning: SPLUNK_SOAR_TOKEN environment variable not set")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
      import asyncio
    asyncio.run(main())
