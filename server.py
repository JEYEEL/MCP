from mcp.server.fastmcp import FastMCP
from tools import files, search, git_lite

mcp = FastMCP("file-server")
files.register(mcp)
search.register(mcp)
git_lite.register(mcp)

if __name__ == "__main__":
    mcp.run()