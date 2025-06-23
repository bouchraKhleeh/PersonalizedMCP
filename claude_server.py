from __future__ import annotations
import json
import os
import sys
import logging
from typing import Any, Dict
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
async def reload_data(confirm: bool = False) -> str:
    """
    Reload F1 data from JSON file.

    Args:
        confirm: Boolean flag to confirm reloading

    Returns:
        Status message
    """
    if not confirm:
        return "Reload aborted: please set 'confirm=true' to reload."
    global F1_DATA
    F1_DATA = load_f1_data()
    return "F1 data reloaded successfully."

# Entry point
if __name__ == "__main__":
    # Run the server using stdio transport
    mcp.run(transport='stdio')