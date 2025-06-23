from __future__ import annotations
import json
import os
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP

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
        print(f"Error: f1_data.json not found at {json_path}")
        return {"drivers": {}, "teams": {}, "circuits": {}}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return {"drivers": {}, "teams": {}, "circuits": {}}

# Load data at startup
F1_DATA = load_f1_data()

@mcp.tool()
async def get_info(entity_type: str, entity_id: str) -> str:
    """
    Get detailed information about an F1 entity (driver, team, or circuit).

    Args:
        entity_type: Type of entity ('driver', 'team', 'circuit')
        entity_id: Entity identifier (e.g., 'max_verstappen', 'lewis_hamilton', 'red_bull', 'monaco')

    Returns:
        Formatted entity information or error message
    """
    # Validate entity type
    if entity_type == "driver":
        data_key = "drivers"
        if entity_id not in F1_DATA[data_key]:
            return f"Driver '{entity_id}' not found. Available drivers: {', '.join(F1_DATA[data_key].keys())}"

        entity = F1_DATA[data_key][entity_id]
        return f"""
Driver: {entity['name']}
Team: {entity['team']}
Nationality: {entity['nationality']}
World Championships: {entity['world_championships']}
Race Wins: {entity['race_wins']}
Pole Positions: {entity['pole_positions']}
Fastest Laps: {entity['fastest_laps']}
Current Points: {entity['current_points']}
"""

    elif entity_type == "team":
        data_key = "teams"
        if entity_id not in F1_DATA[data_key]:
            return f"Team '{entity_id}' not found. Available teams: {', '.join(F1_DATA[data_key].keys())}"

        entity = F1_DATA[data_key][entity_id]
        return f"""
Team: {entity['name']}
Base: {entity['base']}
Team Principal: {entity['team_principal']}
Constructors Championships: {entity['constructors_championships']}
Engine Supplier: {entity['engine_supplier']}
Founded: {entity['founded']}
"""

    elif entity_type == "circuit":
        data_key = "circuits"
        if entity_id not in F1_DATA[data_key]:
            return f"Circuit '{entity_id}' not found. Available circuits: {', '.join(F1_DATA[data_key].keys())}"

        entity = F1_DATA[data_key][entity_id]
        return f"""
Circuit: {entity['name']}
Location: {entity['location']}
Length: {entity['length_km']} km
Race Laps: {entity['laps']}
Lap Record: {entity['lap_record']} by {entity['lap_record_holder']}
First GP: {entity['first_gp']}
"""

    else:
        return f"Unknown entity type '{entity_type}'. Available types: driver, team, circuit"

@mcp.tool()
async def compare_drivers(driver1_id: str, driver2_id: str) -> str:
    """
    Compare statistics between two F1 drivers.

    Args:
        driver1_id: First driver identifier
        driver2_id: Second driver identifier

    Returns:
        Formatted comparison or error message
    """
    if driver1_id not in F1_DATA["drivers"]:
        return f"Driver '{driver1_id}' not found"
    if driver2_id not in F1_DATA["drivers"]:
        return f"Driver '{driver2_id}' not found"

    driver1 = F1_DATA["drivers"][driver1_id]
    driver2 = F1_DATA["drivers"][driver2_id]

    # Helper function to determine winner
    def compare_stat(stat1: int, stat2: int, name1: str, name2: str) -> str:
        if stat1 > stat2:
            return f"{name1} ({stat1} vs {stat2})"
        elif stat2 > stat1:
            return f"{name2} ({stat2} vs {stat1})"
        else:
            return f"Equal ({stat1})"

    return f"""
{driver1['name']} vs {driver2['name']}

World Championships: {compare_stat(
        driver1['world_championships'], driver2['world_championships'],
        driver1['name'], driver2['name']
    )}

Race Wins: {compare_stat(
        driver1['race_wins'], driver2['race_wins'],
        driver1['name'], driver2['name']
    )}

Pole Positions: {compare_stat(
        driver1['pole_positions'], driver2['pole_positions'],
        driver1['name'], driver2['name']
    )}

Fastest Laps: {compare_stat(
        driver1['fastest_laps'], driver2['fastest_laps'],
        driver1['name'], driver2['name']
    )}
"""

@mcp.tool()
async def list_all_data() -> str:
    """
    List all available drivers, teams, and circuits.

    Returns:
        Formatted list of all available data
    """
    drivers = ", ".join(F1_DATA["drivers"].keys())
    teams = ", ".join(F1_DATA["teams"].keys())
    circuits = ", ".join(F1_DATA["circuits"].keys())

    return f"""
Drivers: {drivers}

Teams: {teams}

Circuits: {circuits}
"""

@mcp.tool()
async def reload_data() -> str:
    """
    Reload F1 data from JSON file.

    Returns:
        Status message
    """
    global F1_DATA
    F1_DATA = load_f1_data()
    return "F1 data reloaded successfully from f1_data.json"

# Entry point
if __name__ == "__main__":
    # Run the server using stdio transport
    mcp.run(transport='stdio')