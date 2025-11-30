import os
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.sse import SseServerTransport
from mcp.server import Server
import uvicorn
import lancedb_mcp_utils as utils
import lancedb_query_utils as query_utils

SERVICE_NAME = os.environ.get("SERVICE_NAME", "lancedb")

mcp_server = FastMCP(SERVICE_NAME, host=os.getenv("FASTMCP_HOST"), port=int(
    os.getenv("FASTMCP_PORT")))

@mcp_server.tool()
async def run_query(query: str, ctx: Context):
    """
    Queries the LanceDB GraphRAG index using the provided prompt.

    Args:

        query (str): The prompt input.

    Returns:

        str: Results containing a JSON-formatted list of prompt results.
    """
    for result in query_utils.query_index(query):

        if result and str(result).isalpha():

            await ctx.report_progress(progress=1_000, total=1_000,
                                      message="Processing complete!")

            return result

        else:

            await ctx.report_progress(progress=int(result), total=1_000,
                                      message=f"Processing items...#{result}")

if __name__ == "__main__":

    if os.getenv("INIT_DB"):
        print("Initializing LanceDB GraphRAG index...")
        query_utils.initialize_index()

    else:

        print(f"MCP Transport: {os.getenv('MCP_TRANSPORT')}")

        if os.getenv("MCP_TRANSPORT")=="streamable-http":

            print(f"Starting MCP Server...")

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
