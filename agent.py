import asyncio
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from gym_server import mcp

# Load environment variables
load_dotenv()

# Initialize OpenAI Client
client = OpenAI()

SYSTEM_PROMPT = """You are helpful Gym Assistant.
Use the supplied tools to help users check class schedules, book classes, and cancel bookings.
Always check the output of tools before responding to the user.
If a tool returns an error, explain it to the user.
Today is Monday 10:00 (Simulated).
"""

async def main():
    print("Gym Assistant CLI (Type 'quit' to exit)")
    print("-" * 30)

    # Get tools from FastMCP
    # result is a dict: {name: FunctionTool}
    mcp_tools_dict = await mcp.get_tools()
    
    # helper to convert to OpenAI format
    openai_tools = []
    for name, tool in mcp_tools_dict.items():
        # FunctionTool usually has 'parameters' as the JSON schema.
        # We try to retrieve it.
        # If FastMCP implementation varies, we might need adjustments.
        try:
             # FastMCP 2.0 FunctionTool adaptation
             # Inspecting previously showed 'parameters' might not be a direct attribute?
             # dir() showed 'schema', 'to_mcp_tool'.
             # mcp_tool = tool.to_mcp_tool() -> has inputSchema
             mcp_tool_def = tool.to_mcp_tool()
             parameters_schema = mcp_tool_def.inputSchema
        except Exception:
             # Fallback if strict access fails, e.g. if parameters is directly available
             parameters_schema = getattr(tool, 'parameters', {})

        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": parameters_schema
            }
        })

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() in ["quit", "exit"]:
                break
            
            messages.append({"role": "user", "content": user_input})

            # Call OpenAI
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=openai_tools,
                tool_choice="auto"
            )

            assistant_msg = response.choices[0].message
            messages.append(assistant_msg)

            if assistant_msg.tool_calls:
                # Handle tool calls
                for tool_call in assistant_msg.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)
                    
                    print(f"[Tool Call] {fn_name}({fn_args})")
                    
                    if fn_name in mcp_tools_dict:
                        tool_instance = mcp_tools_dict[fn_name]
                        # Run the tool
                        # tool.run matches the signature, expects arguments
                        try:
                            # FastMCP FunctionTool.run expects a dictionary 'arguments'
                            result_obj = await tool_instance.run(arguments=fn_args)
                            # Extract text from content list
                            result = ""
                            if hasattr(result_obj, 'content') and isinstance(result_obj.content, list):
                                for item in result_obj.content:
                                    if hasattr(item, 'text'):
                                        result += item.text + "\n"
                            else:
                                result = str(result_obj)
                        except Exception as e:
                            result = str(e)
                    else:
                        result = f"Error: Tool {fn_name} not found."
                    
                    print(f"[Tool Output] {result}")
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    })
                
                # Get final response after tool outputs
                response_final = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages
                )
                final_msg = response_final.choices[0].message
                messages.append(final_msg)
                print(f"Assistant: {final_msg.content}")

            else:
                print(f"Assistant: {assistant_msg.content}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
