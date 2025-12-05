#!/usr/bin/env python3
"""
Splunk SOAR MCP Server - Remote HTTP Version
This version uses HTTP transport for use with Claude.ai web interface.

To run: python mcp_server_remote.py
Server will start on http://localhost:8080

For Claude.ai integration, you need to expose this server publicly
using ngrok or deploy to a cloud service.
"""

import os
import json
import urllib.request
import urllib.error
import ssl
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import threading


# Configuration from environment variables
SPLUNK_URL = os.getenv("SPLUNK_SOAR_URL", "").rstrip("/")
SPLUNK_TOKEN = os.getenv("SPLUNK_SOAR_TOKEN", "")
PORT = int(os.getenv("MCP_PORT", "8080"))

# SSL context for SOAR API calls
ssl_context = ssl.create_unverified_context()


def soar_api_request(endpoint: str, method: str = "GET", data: dict = None) -> dict:
      """Make an API request to Splunk SOAR."""
      if not SPLUNK_URL or not SPLUNK_TOKEN:
                raise ValueError("SPLUNK_SOAR_URL and SPLUNK_SOAR_TOKEN must be set")

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


# MCP Tool definitions
TOOLS = [
      {"name": "test_connection", "description": "Test connection to SOAR"},
      {"name": "list_containers", "description": "List containers/incidents"},
      {"name": "get_container", "description": "Get container details"},
      {"name": "list_playbooks", "description": "List available playbooks"},
      {"name": "run_playbook", "description": "Run a playbook"},
      {"name": "list_actions", "description": "List available actions"},
      {"name": "get_action_run", "description": "Get action run status"},
      {"name": "list_assets", "description": "List configured assets"},
      {"name": "get_system_info", "description": "Get system information"}
]


def execute_tool(name: str, args: dict) -> str:
      """Execute an MCP tool and return the result."""
      try:
                if name == "test_connection":
                              result = soar_api_request("/version")
                              return f"Connected! Version: {json.dumps(result)}"
elif name == "list_containers":
            page = args.get("page", 0)
            page_size = args.get("page_size", 10)
            result = soar_api_request(f"/container?page={page}&page_size={page_size}")
            return json.dumps(result, indent=2)
elif name == "get_container":
            container_id = args.get("container_id")
            result = soar_api_request(f"/container/{container_id}")
            return json.dumps(result, indent=2)
elif name == "list_playbooks":
            result = soar_api_request("/playbook?page_size=100")
            return json.dumps(result, indent=2)
elif name == "run_playbook":
            data = {
                              "container_id": args.get("container_id"),
                              "playbook_id": args.get("playbook_id"),
                              "scope": args.get("scope", "all"),
                              "run": True
            }
            result = soar_api_request("/playbook_run", method="POST", data=data)
            return f"Playbook started: {json.dumps(result)}"
elif name == "list_actions":
            result = soar_api_request("/action?page_size=100")
            return json.dumps(result, indent=2)
elif name == "get_action_run":
            action_run_id = args.get("action_run_id")
            result = soar_api_request(f"/action_run/{action_run_id}")
            return json.dumps(result, indent=2)
elif name == "list_assets":
            result = soar_api_request("/asset?page_size=100")
            return json.dumps(result, indent=2)
elif name == "get_system_info":
            result = soar_api_request("/system_info")
            return json.dumps(result, indent=2)
else:
            return f"Unknown tool: {name}"
except Exception as e:
          return f"Error: {str(e)}"


class MCPHandler(BaseHTTPRequestHandler):
      """HTTP handler for MCP protocol."""

    def send_json(self, data, status=200):
              self.send_response(status)
              self.send_header("Content-Type", "application/json")
              self.send_header("Access-Control-Allow-Origin", "*")
              self.end_headers()
              self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
              self.send_response(200)
              self.send_header("Access-Control-Allow-Origin", "*")
              self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
              self.send_header("Access-Control-Allow-Headers", "Content-Type")
              self.end_headers()

    def do_GET(self):
              if self.path == "/health":
                            self.send_json({"status": "ok"})
elif self.path == "/tools":
            self.send_json({"tools": TOOLS})
else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
              content_length = int(self.headers.get("Content-Length", 0))
              body = self.rfile.read(content_length).decode()

        try:
                      data = json.loads(body) if body else {}

            if self.path == "/execute":
                              tool_name = data.get("tool")
                              args = data.get("arguments", {})
                              result = execute_tool(tool_name, args)
                              self.send_json({"result": result})
else:
                  self.send_json({"error": "Not found"}, 404)
except Exception as e:
            self.send_json({"error": str(e)}, 500)


def main():
      print(f"Starting MCP Server on port {PORT}")
      print(f"SOAR URL: {SPLUNK_URL or 'NOT SET'}")
      print(f"SOAR Token: {'SET' if SPLUNK_TOKEN else 'NOT SET'}")

    server = HTTPServer(("0.0.0.0", PORT), MCPHandler)
    print(f"Server running at http://localhost:{PORT}")
    print("Endpoints: /health, /tools, /execute")
    server.serve_forever()


if __name__ == "__main__":
      main()
