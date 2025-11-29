import os
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from mcp.server import Server
import uvicorn
import lancedb_mcp_utils as utils
import lancedb_query_utils as query_utils

SERVICE_NAME = os.environ.get("SERVICE_NAME", "lancedb")

mcp_server = FastMCP(SERVICE_NAME)

@mcp_server.tool()
def run_query(query: str):
    """
    Queries the LanceDB GraphRAG index using the provided prompt.

    Args:

        query (str): The prompt input.

    Returns:

        str: Results containing a JSON-formatted list of prompt results.
    """
    return query_utils.query_index(query)

if __name__ == "__main__":

    if os.getenv("INIT_DB"):
        print("Initializing LanceDB GraphRAG index...")
        query_utils.initialize_index()

    else:

        print(f"MCP Transport: {os.getenv('MCP_TRANSPORT')}")

        if os.getenv("MCP_TRANSPORT")=="streamable-http":

            print(f"Starting MCP Server on 0.0.0.0:8000/mcp...")

            mcp_server.run(transport=os.getenv("MCP_TRANSPORT"))

        else:
            mcp_sse_server = mcp_server._mcp_server

            import argparse

            parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
            parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
            parser.add_argument('--port', type=int, default=8000,
                                help='Port to listen on')
            args = parser.parse_args()

            print(f"Starting MCP Server on {args.host}:{args.port}")
            print(f"SSE endpoint: http://{args.host}:{args.port}/sse")

            starlette_app = utils.create_starlette_app(mcp_sse_server, debug=True)

            uvicorn.run(starlette_app, host=args.host, port=args.port)
