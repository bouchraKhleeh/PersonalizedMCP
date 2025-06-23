from __future__ import annotations
import json
import os
import sys
import logging
from typing import Any, Dict, List
from mcp.server.fastmcp import FastMCP

# Configure logger to write to stderr
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger("f1-server")

# Initialize the MCP server
mcp = FastMCP("f1-data-server")

# Load F1 data from JSON file
def load_f1_data() -> Dict[str, Any]:
    """Load F1 data from JSON file"""
    json_path = os.path.join(os.path.dirname(__file__), 'f1_data.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"f1_data.json not found at {json_path}")
        return {"drivers": {}, "teams": {}, "circuits": {}}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {e}")
        return {"drivers": {}, "teams": {}, "circuits": {}}

# Load data at startup
F1_DATA = load_f1_data()

# MCP RESOURCES

@mcp.resource("f1://drivers")
async def list_drivers_resource() -> str:
    """List of all available F1 drivers"""
    drivers = F1_DATA.get("drivers", {})
    driver_list = []

    for driver_id, driver_data in drivers.items():
        driver_list.append({
            "id": driver_id,
            "name": driver_data.get("name", ""),
            "nationality": driver_data.get("nationality", ""),
            "team": driver_data.get("current_team", ""),
            "championships": driver_data.get("world_championships", 0)
        })

    return json.dumps({
        "resource_type": "drivers_list",
        "count": len(driver_list),
        "drivers": driver_list
    }, indent=2)

@mcp.resource("f1://teams")
async def list_teams_resource() -> str:
    """List of all available F1 teams"""
    teams = F1_DATA.get("teams", {})
    team_list = []

    for team_id, team_data in teams.items():
        team_list.append({
            "id": team_id,
            "name": team_data.get("name", ""),
            "base": team_data.get("base", ""),
            "team_chief": team_data.get("team_chief", ""),
            "championships": team_data.get("constructors_championships", 0)
        })

    return json.dumps({
        "resource_type": "teams_list",
        "count": len(team_list),
        "teams": team_list
    }, indent=2)

@mcp.resource("f1://circuits")
async def list_circuits_resource() -> str:
    """List of all available F1 circuits"""
    circuits = F1_DATA.get("circuits", {})
    circuit_list = []

    for circuit_id, circuit_data in circuits.items():
        circuit_list.append({
            "id": circuit_id,
            "name": circuit_data.get("name", ""),
            "location": circuit_data.get("location", ""),
            "country": circuit_data.get("country", ""),
            "length": circuit_data.get("length", "")
        })

    return json.dumps({
        "resource_type": "circuits_list",
        "count": len(circuit_list),
        "circuits": circuit_list
    }, indent=2)

@mcp.resource("f1://driver/{driver_id}")
async def get_driver_resource(driver_id: str) -> str:
    """Detailed information for a specific driver"""
    if driver_id not in F1_DATA.get("drivers", {}):
        return json.dumps({
            "error": f"Driver '{driver_id}' not found",
            "available_drivers": list(F1_DATA.get("drivers", {}).keys())
        }, indent=2)

    driver_data = F1_DATA["drivers"][driver_id]
    return json.dumps({
        "resource_type": "driver_details",
        "driver_id": driver_id,
        "data": driver_data
    }, indent=2)

@mcp.resource("f1://team/{team_id}")
async def get_team_resource(team_id: str) -> str:
    """Detailed information for a specific team"""
    if team_id not in F1_DATA.get("teams", {}):
        return json.dumps({
            "error": f"Team '{team_id}' not found",
            "available_teams": list(F1_DATA.get("teams", {}).keys())
        }, indent=2)

    team_data = F1_DATA["teams"][team_id]
    return json.dumps({
        "resource_type": "team_details",
        "team_id": team_id,
        "data": team_data
    }, indent=2)

@mcp.resource("f1://circuit/{circuit_id}")
async def get_circuit_resource(circuit_id: str) -> str:
    """Detailed information for a specific circuit"""
    if circuit_id not in F1_DATA.get("circuits", {}):
        return json.dumps({
            "error": f"Circuit '{circuit_id}' not found",
            "available_circuits": list(F1_DATA.get("circuits", {}).keys())
        }, indent=2)

    circuit_data = F1_DATA["circuits"][circuit_id]
    return json.dumps({
        "resource_type": "circuit_details",
        "circuit_id": circuit_id,
        "data": circuit_data
    }, indent=2)

# MCP TOOLS
@mcp.tool()
async def get_driver_info(driver_id: str) -> Dict[str, Any]:
    """
    Get detailed information about an F1 driver.

    Args:
        driver_id: Driver identifier (e.g., 'max_verstappen', 'lewis_hamilton')

    Returns:
        Formatted driver information or error message
    """
    # Use the resource to get the data
    resource_data = await get_driver_resource(driver_id)
    resource_json = json.loads(resource_data)

    # Return in the expected format for tools
    if "error" in resource_json:
        return resource_json
    return resource_json["data"]

@mcp.tool()
async def get_team_info(team_id: str) -> Dict[str, Any]:
    """
    Get detailed information about an F1 team.

    Args:
        team_id: Team identifier (e.g., 'red_bull', 'ferrari', 'mercedes')

    Returns:
        Formatted team information or error message
    """
    # Use the resource to get the data
    resource_data = await get_team_resource(team_id)
    resource_json = json.loads(resource_data)

    # Return in the expected format for tools
    if "error" in resource_json:
        return resource_json
    return resource_json["data"]

@mcp.tool()
async def get_circuit_info(circuit_id: str) -> Dict[str, Any]:
    """
    Get detailed information about an F1 circuit.

    Args:
        circuit_id: Circuit identifier (e.g., 'monaco', 'silverstone')

    Returns:
        Formatted circuit information or error message
    """
    # Use the resource to get the data
    resource_data = await get_circuit_resource(circuit_id)
    resource_json = json.loads(resource_data)

    # Return in the expected format for tools
    if "error" in resource_json:
        return resource_json
    return resource_json["data"]

@mcp.tool()
async def compare_drivers(driver1_id: str, driver2_id: str) -> Dict[str, Any]:
    """
    Compare statistics between two F1 drivers.

    Args:
        driver1_id: First driver identifier
        driver2_id: Second driver identifier

    Returns:
        Formatted comparison or error message
    """
    if driver1_id not in F1_DATA["drivers"] or driver2_id not in F1_DATA["drivers"]:
        return {"error": "One or both driver IDs not found."}

    driver1 = F1_DATA["drivers"][driver1_id]
    driver2 = F1_DATA["drivers"][driver2_id]

    # Helper function to determine winner
    def compare_stat(stat1: int, stat2: int) -> str:
        if stat1 > stat2:
            return "driver1"
        elif stat2 > stat1:
            return "driver2"
        else:
            return "equal"

    return {
        "driver1": driver1["name"],
        "driver2": driver2["name"],
        "comparisons": {
            "world_championships": compare_stat(driver1["world_championships"], driver2["world_championships"]),
            "race_wins": compare_stat(driver1["race_wins"], driver2["race_wins"]),
            "pole_positions": compare_stat(driver1["pole_positions"], driver2["pole_positions"]),
            "fastest_laps": compare_stat(driver1["fastest_laps"], driver2["fastest_laps"])
        }
    }

@mcp.tool()
async def list_all_data() -> Dict[str, Any]:
    """
    List all available drivers, teams, and circuits.

    Returns:
        Formatted list of all available data
    """
    # Use resources to get the data
    drivers_data = await list_drivers_resource()
    teams_data = await list_teams_resource()
    circuits_data = await list_circuits_resource()

    drivers_json = json.loads(drivers_data)
    teams_json = json.loads(teams_data)
    circuits_json = json.loads(circuits_data)

    return {
        "drivers": [driver["id"] for driver in drivers_json["drivers"]],
        "teams": [team["id"] for team in teams_json["teams"]],
        "circuits": [circuit["id"] for circuit in circuits_json["circuits"]]
    }

@mcp.tool()
async def reload_data() -> str:
    """
    Reload F1 data from JSON file.

    Returns:
        Status message
    """
    global F1_DATA
    F1_DATA = load_f1_data()
    return "F1 data reloaded successfully."

# Entry point
if __name__ == "__main__":
    # Run the server using stdio transport
    mcp.run(transport='stdio')