# MCP GitHub Advanced Search (G.A.S.) - DeepSeek Integration

This README provides detailed instructions for integrating the MCP GitHub Advanced Search (G.A.S.) server with DeepSeek AI tools, enabling advanced code search and retrieval capabilities within your Python project.

## Overview

The G.A.S. server allows DeepSeek models to perform sophisticated GitHub searches with intelligent filtering, content retrieval, and structured JSON responses. This integration enhances AI-assisted development by providing contextual information directly within your IDE or chat interface.

## Key Features

- **DeepSeek-Optimized Search**: Advanced filters tailored for AI workflows
- **Structured Output**: JSON format compatible with DeepSeek protocols
- **GitHub Interaction**: Seamless web automation using Playwright
- **Content Analysis**: Extracts relevant code patterns and documentation

## Quick Start for DeepSeek Users

1. **Install Dependencies**:

   ```bash
   pip install mcp-server-git-gas playwright
   ```

2. **Configure MCP Server**:
   Add the following to your DeepSeek MCP configuration:

   ```json
   {
     "mcpServers": {
       "gas-deepseek": {
         "command": "mcp-server-git-gas",
         "args": []
       }
     }
   }
   ```

3. **Run a Sample Search**:

   ```python
   from mcp_server_git_gas import GASClient

   client = GASClient()
   results = client.search_code(keyword="async", file_name=".clinerules")
   print(results)
   ```

## Usage Examples with DeepSeek

### Search for DeepSeek-Related Patterns

```
Find all .clinerules files containing "DeepSeek" in the MCP-github-advanced-search-ws project
```

### Analyze Code Patterns

```
Retrieve Python files with async def functions from the last 30 days
```

## Configuration for DeepSeek Integration

### Environment Variables

- `DEEPSEEK_API_KEY`: Your DeepSeek API key (optional for basic searches)
- `MCP_HOME_DIR`: Custom directory for MCP data (default: ~/.mcp_github)

### Advanced Settings

For optimal performance with DeepSeek, enable:

```bash
export ENABLE_DEEPSEEK=true
```

## Troubleshooting

- **Authentication Issues**: Ensure GitHub login in browser session
- **Slow Responses**: Check GitHub rate limits and network connectivity
- **Configuration Errors**: Verify MCP server settings in your DeepSeek config

## Related Documentation

- [Main README](../README.md)
- [MCP Server Details](https://github.com/your-repo/mcp-server-git-gas)
- [DeepSeek Integration Guide](https://docs.deepseek.com/integrations/mcp)

## Contact

For support or feedback, reach out to the MCP community:

- GitHub Issues: https://github.com/your-repo/mcp-server-git-gas/issues
- MCP Servers Directory: https://github.com/modelcontextprotocol/servers
