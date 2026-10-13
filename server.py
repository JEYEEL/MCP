from mcp.server.fastmcp import FastMCP
from tools import files

mcp = FastMCP("file-server")
files.register(mcp)

if __name__ == "__main__":
    mcp.run()