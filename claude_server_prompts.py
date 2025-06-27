
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

# MCP PROMPTS
"""
Dans un prompt MCP, vous ne pouvez pas appeler directement d'autres tools. 
Les prompts sont des templates qui génèrent du texte, ils ne peuvent pas exécuter du code.
"""
@mcp.prompt()
async def compare_drivers(driver1_id: str, driver2_id: str) -> str:
    """
    Simple comparison between two F1 drivers

    Args:
        driver1_id: First driver (max_verstappen, lewis_hamilton, charles_leclerc)
        driver2_id: Second driver (max_verstappen, lewis_hamilton, charles_leclerc)
    """
    # Check if drivers exist
    if driver1_id not in F1_DATA.get("drivers", {}) or driver2_id not in F1_DATA.get("drivers", {}):
        available = list(F1_DATA.get("drivers", {}).keys())
        return f"Error: Use these IDs: {available}"

    driver1 = F1_DATA["drivers"][driver1_id]
    driver2 = F1_DATA["drivers"][driver2_id]

    prompt = f"""Compare these two F1 drivers:

**{driver1.get('name', 'N/A')}** vs **{driver2.get('name', 'N/A')}**

Driver 1: {driver1.get('name', 'N/A')} ({driver1.get('team', 'N/A')})
- Championships: {driver1.get('world_championships', 0)}
- Wins: {driver1.get('race_wins', 0)}
- Poles: {driver1.get('pole_positions', 0)}

Driver 2: {driver2.get('name', 'N/A')} ({driver2.get('team', 'N/A')})
- Championships: {driver2.get('world_championships', 0)}
- Wins: {driver2.get('race_wins', 0)}
- Poles: {driver2.get('pole_positions', 0)}

Who is better and why?"""

    return prompt

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

@mcp.resource("f1://stats/summary")
async def get_stats_summary_resource() -> str:
    """Statistical summary of all F1 data"""
    drivers_count = len(F1_DATA.get("drivers", {}))
    teams_count = len(F1_DATA.get("teams", {}))
    circuits_count = len(F1_DATA.get("circuits", {}))

    # Calculate some interesting statistics
    total_championships = sum(
        driver.get("world_championships", 0)
        for driver in F1_DATA.get("drivers", {}).values()
    )

    most_successful_driver = max(
        F1_DATA.get("drivers", {}).items(),
        key=lambda x: x[1].get("world_championships", 0),
        default=("none", {"name": "N/A", "world_championships": 0})
    )

    return json.dumps({
        "resource_type": "stats_summary",
        "summary": {
            "drivers_count": drivers_count,
            "teams_count": teams_count,
            "circuits_count": circuits_count,
            "total_championships_tracked": total_championships,
            "most_successful_driver": {
                "id": most_successful_driver[0],
                "name": most_successful_driver[1].get("name", "N/A"),
                "championships": most_successful_driver[1].get("world_championships", 0)
            }
        }
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
    if driver_id not in F1_DATA["drivers"]:
        return {"error": f"Driver '{driver_id}' not found.", "available": list(F1_DATA['drivers'].keys())}
    return F1_DATA["drivers"][driver_id]

@mcp.tool()
async def get_team_info(team_id: str) -> Dict[str, Any]:
    """
    Get detailed information about an F1 team.

    Args:
        team_id: Team identifier (e.g., 'red_bull', 'ferrari', 'mercedes')

    Returns:
        Formatted team information or error message
    """
    if team_id not in F1_DATA["teams"]:
        return {"error": f"Team '{team_id}' not found.", "available": list(F1_DATA['teams'].keys())}
    return F1_DATA["teams"][team_id]

@mcp.tool()
async def get_circuit_info(circuit_id: str) -> Dict[str, Any]:
    """
    Get detailed information about an F1 circuit.

    Args:
        circuit_id: Circuit identifier (e.g., 'monaco', 'silverstone')

    Returns:
        Formatted circuit information or error message
    """
    if circuit_id not in F1_DATA["circuits"]:
        return {"error": f"Circuit '{circuit_id}' not found.", "available": list(F1_DATA['circuits'].keys())}
    return F1_DATA["circuits"][circuit_id]

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
    return {
        "drivers": list(F1_DATA["drivers"].keys()),
        "teams": list(F1_DATA["teams"].keys()),
        "circuits": list(F1_DATA["circuits"].keys())
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