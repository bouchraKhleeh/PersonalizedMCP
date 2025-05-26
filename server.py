import json
import asyncio
from typing import Any, Dict, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool, CallToolRequest

# Sample F1 data - in a real application, this could come from a database
F1_DATA = {
    "drivers": {
        "max_verstappen": {
            "name": "Max Verstappen",
            "team": "Red Bull Racing",
            "nationality": "Dutch",
            "world_championships": 4,
            "race_wins": 63,
            "pole_positions": 40,
            "fastest_laps": 33,
            "current_points": 0  # 2025 season
        },
        "lewis_hamilton": {
            "name": "Lewis Hamilton",
            "team": "Ferrari",
            "nationality": "British",
            "world_championships": 7,
            "race_wins": 105,
            "pole_positions": 104,
            "fastest_laps": 67,
            "current_points": 0
        },
        "charles_leclerc": {
            "name": "Charles Leclerc",
            "team": "Ferrari",
            "nationality": "Monegasque",
            "world_championships": 0,
            "race_wins": 7,
            "pole_positions": 25,
            "fastest_laps": 9,
            "current_points": 0
        }
    },
    "teams": {
        "red_bull": {
            "name": "Red Bull Racing",
            "base": "Milton Keynes, UK",
            "team_principal": "Christian Horner",
            "constructors_championships": 6,
            "engine_supplier": "Honda RBPT",
            "founded": 2005
        },
        "ferrari": {
            "name": "Scuderia Ferrari",
            "base": "Maranello, Italy",
            "team_principal": "Fred Vasseur",
            "constructors_championships": 16,
            "engine_supplier": "Ferrari",
            "founded": 1950
        },
        "mercedes": {
            "name": "Mercedes-AMG Petronas",
            "base": "Brackley, UK",
            "team_principal": "Toto Wolff",
            "constructors_championships": 8,
            "engine_supplier": "Mercedes",
            "founded": 2010
        }
    },
    "circuits": {
        "monaco": {
            "name": "Circuit de Monaco",
            "location": "Monte Carlo, Monaco",
            "length_km": 3.337,
            "laps": 78,
            "lap_record": "1:12.909",
            "lap_record_holder": "Lewis Hamilton",
            "first_gp": 1950
        },
        "silverstone": {
            "name": "Silverstone Circuit",
            "location": "Silverstone, UK",
            "length_km": 5.891,
            "laps": 52,
            "lap_record": "1:27.097",
            "lap_record_holder": "Max Verstappen",
            "first_gp": 1950
        }
    }
}

# Initialize the MCP server
server = Server("f1-data-server")

# Helper functions for each tool
async def get_driver_info(driver_id: str) -> Dict[str, Any]:
    """Get detailed information about an F1 driver."""
    if driver_id in F1_DATA["drivers"]:
        return {
            "success": True,
            "data": F1_DATA["drivers"][driver_id]
        }
    else:
        return {
            "success": False,
            "error": f"Driver '{driver_id}' not found. Available drivers: {', '.join(F1_DATA['drivers'].keys())}"
        }

async def get_team_info(team_id: str) -> Dict[str, Any]:
    """Get detailed information about an F1 team."""
    if team_id in F1_DATA["teams"]:
        return {
            "success": True,
            "data": F1_DATA["teams"][team_id]
        }
    else:
        return {
            "success": False,
            "error": f"Team '{team_id}' not found. Available teams: {', '.join(F1_DATA['teams'].keys())}"
        }

async def get_circuit_info(circuit_id: str) -> Dict[str, Any]:
    """Get detailed information about an F1 circuit."""
    if circuit_id in F1_DATA["circuits"]:
        return {
            "success": True,
            "data": F1_DATA["circuits"][circuit_id]
        }
    else:
        return {
            "success": False,
            "error": f"Circuit '{circuit_id}' not found. Available circuits: {', '.join(F1_DATA['circuits'].keys())}"
        }

async def compare_drivers(driver1_id: str, driver2_id: str) -> Dict[str, Any]:
    """Compare statistics between two F1 drivers."""
    if driver1_id not in F1_DATA["drivers"]:
        return {"success": False, "error": f"Driver '{driver1_id}' not found"}
    if driver2_id not in F1_DATA["drivers"]:
        return {"success": False, "error": f"Driver '{driver2_id}' not found"}

    driver1 = F1_DATA["drivers"][driver1_id]
    driver2 = F1_DATA["drivers"][driver2_id]

    comparison = {
        "driver1": {
            "name": driver1["name"],
            "world_championships": driver1["world_championships"],
            "race_wins": driver1["race_wins"],
            "pole_positions": driver1["pole_positions"]
        },
        "driver2": {
            "name": driver2["name"],
            "world_championships": driver2["world_championships"],
            "race_wins": driver2["race_wins"],
            "pole_positions": driver2["pole_positions"]
        },
        "analysis": {
            "more_championships": driver1["name"] if driver1["world_championships"] > driver2["world_championships"]
            else driver2["name"] if driver2["world_championships"] > driver1["world_championships"]
            else "Equal",
            "more_wins": driver1["name"] if driver1["race_wins"] > driver2["race_wins"]
            else driver2["name"] if driver2["race_wins"] > driver1["race_wins"]
            else "Equal",
            "more_poles": driver1["name"] if driver1["pole_positions"] > driver2["pole_positions"]
            else driver2["name"] if driver2["pole_positions"] > driver1["pole_positions"]
            else "Equal"
        }
    }

    return {"success": True, "data": comparison}

async def list_all_data() -> Dict[str, Any]:
    """List all available drivers, teams, and circuits."""
    return {
        "success": True,
        "data": {
            "drivers": list(F1_DATA["drivers"].keys()),
            "teams": list(F1_DATA["teams"].keys()),
            "circuits": list(F1_DATA["circuits"].keys())
        }
    }

# Define tools
@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_driver_info",
            description="Get detailed information about an F1 driver",
            inputSchema={
                "type": "object",
                "properties": {
                    "driver_id": {
                        "type": "string",
                        "description": "Driver identifier (e.g., 'max_verstappen', 'lewis_hamilton')"
                    }
                },
                "required": ["driver_id"]
            }
        ),
        Tool(
            name="get_team_info",
            description="Get detailed information about an F1 team",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {
                        "type": "string",
                        "description": "Team identifier (e.g., 'red_bull', 'ferrari', 'mercedes')"
                    }
                },
                "required": ["team_id"]
            }
        ),
        Tool(
            name="get_circuit_info",
            description="Get detailed information about an F1 circuit",
            inputSchema={
                "type": "object",
                "properties": {
                    "circuit_id": {
                        "type": "string",
                        "description": "Circuit identifier (e.g., 'monaco', 'silverstone')"
                    }
                },
                "required": ["circuit_id"]
            }
        ),
        Tool(
            name="compare_drivers",
            description="Compare statistics between two F1 drivers",
            inputSchema={
                "type": "object",
                "properties": {
                    "driver1_id": {
                        "type": "string",
                        "description": "First driver identifier"
                    },
                    "driver2_id": {
                        "type": "string",
                        "description": "Second driver identifier"
                    }
                },
                "required": ["driver1_id", "driver2_id"]
            }
        ),
        Tool(
            name="list_all_data",
            description="List all available drivers, teams, and circuits",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

# Handle tool calls
@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if request.name == "get_driver_info":
            result = await get_driver_info(request.arguments["driver_id"])
        elif request.name == "get_team_info":
            result = await get_team_info(request.arguments["team_id"])
        elif request.name == "get_circuit_info":
            result = await get_circuit_info(request.arguments["circuit_id"])
        elif request.name == "compare_drivers":
            result = await compare_drivers(
                request.arguments["driver1_id"],
                request.arguments["driver2_id"]
            )
        elif request.name == "list_all_data":
            result = await list_all_data()
        else:
            result = {"success": False, "error": f"Unknown tool: {request.name}"}

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        error_result = {"success": False, "error": str(e)}
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

# Main function to run the server
async def main():
    """Run the MCP server using stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())