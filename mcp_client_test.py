import asyncio
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PATH = os.path.join(os.path.dirname(__file__), "mcp_server.py")


async def main():
    import sys
    server_params = StdioServerParameters(
        command=sys.executable, args=[SERVER_PATH], env=os.environ.copy()
    )

    print("Launching mcp_server.py as a subprocess and connecting...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()
            print("[1] initialize() complete -- MCP handshake done.\n")

            tools_result = await session.list_tools()
            print(f"[2] list_tools() discovered {len(tools_result.tools)} tools:")
            for t in tools_result.tools:
                print(f"    - {t.name}: {t.description}")
            print()

            resources_result = await session.list_resources()
            print(f"    Resources: {[r.uri for r in resources_result.resources] if resources_result.resources else '(template-based, not listed directly)'}")

            prompts_result = await session.list_prompts()
            print(f"    Prompts: {[p.name for p in prompts_result.prompts]}\n")

            print("[3] call_tool('search_repositories', ...) -- a REAL call to api.github.com:")
            result = await session.call_tool(
                "search_repositories", arguments={"query": "agentic ai framework"}
            )
            for item in result.content:
                if hasattr(item, "text"):
                    print(item.text)


if __name__ == "__main__":
    asyncio.run(main())
