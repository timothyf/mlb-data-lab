import sys
import os
import argparse

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from mlb_data_lab.player.player import Player
from mlb_data_lab.config import DATA_DIR
from mlb_data_lab.utils import Utils
from mlb_data_lab.team.roster import Roster

# Suppress MarkupResemblesLocatorWarning
#warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

players_not_found = []

def save_statcast_data(player_name: str, year: int=2024):
    player = Player.create_from_mlb(player_name = player_name)
    if player is None:
        print(f"Player {player_name} not found.")
        players_not_found.append(player_name)
        return
    
    player.save_statcast_data(year)


# import debugpy

# # 5678 is the default attach port in the VS Code debug configurations. Unless a host and port are specified, host defaults to 127.0.0.1
# debugpy.listen(5678)
# print("Waiting for debugger attach")
# debugpy.wait_for_client()

# Example Usage
# if __name__ == "__main__":
#     pitchers = ['Tarik Skubal']
#     for pitcher in pitchers:
#         save_statcast_data(pitcher)

#     batters = ['Kerry Carpenter', 'Riley Greene']
#     for batter in batters:
#         save_statcast_data(batter)

if __name__ == "__main__":
    # Initialize the parser
    parser = argparse.ArgumentParser(description="Save statscast data.")

    # Add --players and --teams options
    parser.add_argument(
        '--players',
        nargs='+',  # Allows multiple player names to be passed
        help='List of player names to save data for'
    )

    parser.add_argument(
        '--teams',
        nargs='+',  # Allows multiple team names to be passed
        help='List of team names to save data for'
    )

    # Add --year option
    parser.add_argument(
        '--year',
        type=int,  # Ensure year is an integer
        default=2024,  # Set default year to 2024
        help='Specify the year for which the player stats should be saved (default: 2024)'
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    players = []
    teams = None

    # Get players from --players argument
    if args.players:
        players = args.players

    # Get teams from --teams argument
    if args.teams:
        teams = args.teams
    elif not args.players:
        print("No players or teams provided.")
        # Optionally, set default players or teams here if needed
        players = ['Tarik Skubal', 'Riley Greene']
        print(f"Using default players: {players}")

    # If teams are provided, get active roster for each team
    if teams:
        for team in teams:
            players += Roster.get_season_roster(team_name=team, year=args.year)

    # Use the specified year (or the default year 2024)
    year = args.year
    print(f"Year: {year}")

    print(f"Player names: {players}")
    print(f"Team names: {teams}")

    # Generate player summary sheets for each player with the given year
    for player in players:
        save_statcast_data(player, year)

    for player in players_not_found:
        print(f"Player {player} not found.")






    

