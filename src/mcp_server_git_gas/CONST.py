import os


USER_HOME_DIR = os.environ.get("HOME", "/tmp")
MCP_HOME_DIR = os.path.join(USER_HOME_DIR, "mcp_github_advanced_search")
DEBUG_PNG_PATH = os.path.join(MCP_HOME_DIR, "debug.png")
