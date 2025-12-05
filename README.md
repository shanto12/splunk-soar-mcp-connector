# Splunk SOAR MCP Server

MCP (Model Context Protocol) Server for Splunk SOAR - Connect AI assistants to any Splunk SOAR instance with configurable base URL and authentication token.

## Features

- **Configurable Connection**: Connect to any Splunk SOAR instance by setting environment variables
- - **Multi-tenant Support**: Different users can connect to different SOAR instances using the same server code
  - - **Secure Authentication**: Uses Splunk SOAR API tokens for authentication
    - - **Comprehensive Tools**: List containers, playbooks, actions, assets, and more
     
      - ## Available Tools
     
      - | Tool | Description |
      - |------|-------------|
      - | `test_connection` | Test connectivity to your SOAR instance |
      - | `list_containers` | List incidents/cases in SOAR |
      - | `get_container` | Get details of a specific container |
      - | `list_playbooks` | List available playbooks |
      - | `run_playbook` | Execute a playbook on a container |
      - | `list_actions` | List available actions |
      - | `get_action_run` | Get status of an action run |
      - | `list_assets` | List configured assets |
      - | `get_system_info` | Get SOAR system information |
     
      - ## Installation
     
      - 1. Clone this repository:
        2. ```bash
           git clone https://github.com/shanto12/splunk-soar-mcp-connector.git
           cd splunk-soar-mcp-connector
           ```

           2. Install dependencies:
           3. ```bash
              pip install -r requirements.txt
              ```

              ## Configuration

              Set the following environment variables before running:

              ```bash
              export SPLUNK_SOAR_URL="https://your-soar-instance.example.com"
              export SPLUNK_SOAR_TOKEN="your-api-token-here"
              ```

              ### Getting Your API Token

              1. Log into your Splunk SOAR instance
              2. 2. Navigate to Administration > User Management
                 3. 3. Select your user and generate an API token
                    4. 4. Copy the token value
                      
                       5. ## Usage with Claude Desktop
                      
                       6. Add to your Claude Desktop MCP configuration (`claude_desktop_config.json`):
                      
                       7. ```json
                          {
                            "mcpServers": {
                              "splunk-soar": {
                                "command": "python",
                                "args": ["/path/to/splunk-soar-mcp-connector/mcp_server.py"],
                                "env": {
                                  "SPLUNK_SOAR_URL": "https://your-soar-instance.example.com",
                                  "SPLUNK_SOAR_TOKEN": "your-api-token"
                                }
                              }
                            }
                          }
                          ```

                          ## Usage with Other MCP Clients

                          The server uses stdio transport. Configure your MCP client to:
                          - Run: `python mcp_server.py`
                          - - Set environment variables for `SPLUNK_SOAR_URL` and `SPLUNK_SOAR_TOKEN`
                           
                            - ## License
                           
                            - MIT License - See LICENSE file for details.
