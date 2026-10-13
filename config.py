import os
from dotenv import load_dotenv

load_dotenv()  # reads .env if present

MCP_TOKEN = os.environ.get("MCP_TOKEN", "")
PORT = int(os.environ.get("PORT", "8000"))