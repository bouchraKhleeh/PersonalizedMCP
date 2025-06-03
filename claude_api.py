import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python claude_api.py server.py")
        return

    # Connect to MCP server
    server_params = StdioServerParameters(command="python", args=[sys.argv[1]])
    async with stdio_client(server_params) as (stdio, write):
        async with ClientSession(stdio, write) as session:
            await session.initialize()

            # Get tools
            tools_response = await session.list_tools()
            tools = [{
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            } for tool in tools_response.tools]

            print(f"Available tools: {[t['name'] for t in tools]}")

            # Claude client
            claude = Anthropic()

            # Chat loop
            while True:
                question = input("\nF1 Question (or 'quit'): ").strip()
                if question.lower() == 'quit':
                    break

                # Ask Claude
                # The question part
                response = claude.messages.create(
                    #model="claude-3-5-haiku-20241022",
                    #model="claude-3-opus-20240229",
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    system="You are an F1 expert. Use tools when needed for precise data.",
                    messages=[{"role": "user", "content": question}],
                    tools=tools
                )

                # Handle response
                # The answer part
                for content in response.content:
                    if content.type == 'text':
                        print(f"\nClaude: {content.text}")

                    elif content.type == 'tool_use':
                        # Use tool
                        result = await session.call_tool(content.name, content.input)
                        tool_result = result.content[0].text if result.content else "No result"

                        # Claude's interpretation
                        final_response = claude.messages.create(
                            #model="claude-3-5-haiku-20241022",
                            #model="claude-3-opus-20240229",
                            model="claude-3-5-sonnet-20241022",
                            max_tokens=1000,
                            system="You are an F1 expert. Interpret the tool results.",
                            messages=[
                                {"role": "user", "content": question},
                                {"role": "assistant", "content": [content]},
                                {"role": "user", "content": [{"type": "tool_result", "tool_use_id": content.id, "content": tool_result}]}
                            ]
                        )

                        print(f"\nClaude: {final_response.content[0].text}")

if __name__ == "__main__":
    asyncio.run(main())