
import asyncio
import sys
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
client = OpenAI()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python gpt_client.py claude_server.py")
        return

    # Launch stdio-based MCP server
    server_params = StdioServerParameters(command="python", args=[sys.argv[1]])
    async with stdio_client(server_params) as (stdio, write):
        async with ClientSession(stdio, write) as session:
            await session.initialize()

            # Extract available tools from the MCP server
            tools_response = await session.list_tools()
            #####
            tools = [{
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            } for tool in tools_response.tools]

            print(f"Available tools: {[t['function']['name'] for t in tools]}")

            # Chat loop
            while True:
                question = input("\nF1 Question (or 'quit'): ").strip()
                if question.lower() == "quit":
                    break

                # First GPT call using Responses API
                response = client.chat.completions.create(
                    model="gpt-4o",
                    #4.1.mini
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.5,
                    messages=[
                        {"role": "system", "content": "You are an F1 expert. Use tools for precise data."},
                        {"role": "user", "content": question}
                    ]
                )

                msg = response.choices[0].message

                if msg.content:
                    # If GPT replies directly with a text answer
                    print(f"\nGPT: {msg.content}")
                elif msg.tool_calls:
                    # If GPT chooses to use a tool
                    tool_call = msg.tool_calls[0]
                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    # Execute the requested tool using MCP
                    tool_result = await session.call_tool(tool_name, arguments)

                    # Second GPT call with tool result included
                    follow_up = client.chat.completions.create(
                        model="gpt-4o",
                        temperature=0.5,
                        messages=[
                            {"role": "system", "content": "You are an F1 expert. Use tools for precise data."},
                            {"role": "user", "content": question},
                            {"role": "assistant", "tool_calls": [tool_call]},
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": tool_result.content[0].text if tool_result.content else "No result"
                            }
                        ]
                    )

                    print(f"\nGPT: {follow_up.choices[0].message.content}")
                else:
                    # Fallback message in case GPT returns nothing
                    print("\nGPT response was empty and did not include any tool calls.")

if __name__ == "__main__":
    asyncio.run(main())
