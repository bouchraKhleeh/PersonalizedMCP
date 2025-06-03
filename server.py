from __future__ import annotations
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP

from f1_data import F1_DATA

# Initialize the MCP server
mcp = FastMCP("f1-data-server")

@mcp.tool()
async def get_driver_info(driver_id: str) -> str:
    """
    Get detailed information about an F1 driver.

    Args:
        driver_id: Driver identifier (e.g., 'max_verstappen', 'lewis_hamilton')

    Returns:
        Formatted driver information or error message
    """
    if driver_id not in F1_DATA["drivers"]:
        return f"Driver '{driver_id}' not found. Available drivers: {', '.join(F1_DATA['drivers'].keys())}"

    driver = F1_DATA["drivers"][driver_id]
    return f"""
Driver: {driver['name']}
Team: {driver['team']}
Nationality: {driver['nationality']}
World Championships: {driver['world_championships']}
Race Wins: {driver['race_wins']}
Pole Positions: {driver['pole_positions']}
Fastest Laps: {driver['fastest_laps']}
Current Points: {driver['current_points']}
"""

@mcp.tool()
async def get_team_info(team_id: str) -> str:
    """
    Get detailed information about an F1 team.

    Args:
        team_id: Team identifier (e.g., 'red_bull', 'ferrari', 'mercedes')

    Returns:
        Formatted team information or error message
    """
    if team_id not in F1_DATA["teams"]:
        return f"Team '{team_id}' not found. Available teams: {', '.join(F1_DATA['teams'].keys())}"

    team = F1_DATA["teams"][team_id]
    return f"""
Team: {team['name']}
Base: {team['base']}
Team Principal: {team['team_principal']}
Constructors Championships: {team['constructors_championships']}
Engine Supplier: {team['engine_supplier']}
Founded: {team['founded']}
"""

@mcp.tool()
async def get_circuit_info(circuit_id: str) -> str:
    """
    Get detailed information about an F1 circuit.

    Args:
        circuit_id: Circuit identifier (e.g., 'monaco', 'silverstone')

    Returns:
        Formatted circuit information or error message
    """
    if circuit_id not in F1_DATA["circuits"]:
        return f"Circuit '{circuit_id}' not found. Available circuits: {', '.join(F1_DATA['circuits'].keys())}"

    circuit = F1_DATA["circuits"][circuit_id]
    return f"""
Circuit: {circuit['name']}
Location: {circuit['location']}
Length: {circuit['length_km']} km
Race Laps: {circuit['laps']}
Lap Record: {circuit['lap_record']} by {circuit['lap_record_holder']}
First GP: {circuit['first_gp']}
"""

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

# Entry point
if __name__ == "__main__":
    # Run the server using stdio transport
    mcp.run(transport='stdio')