# python generate_sheets.py 'Tarik Skubal' 'Kerry Carpenter'

import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from mlb_summary_sheets import Player
from mlb_summary_sheets.pitching.pitcher_summary_sheet import PitcherSummarySheet
from mlb_summary_sheets.batting.batter_summary_sheet import BatterSummarySheet
from mlb_summary_sheets.roster import Roster
import warnings
from bs4 import MarkupResemblesLocatorWarning
import argparse


# Suppress MarkupResemblesLocatorWarning
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


def generate_player_sheet(player_name: str, year: int=2024):
    player = Player.create_from_mlb(player_name=player_name)
    if player is None:
        print(f"Player {player_name} not found.")
        return
    if player.player_info.primary_position == 'P':
        summary = PitcherSummarySheet(player, year)
    else:
        summary = BatterSummarySheet(player, year)
    summary.generate_plots()   

# import debugpy

# # 5678 is the default attach port in the VS Code debug configurations. Unless a host and port are specified, host defaults to 127.0.0.1
# debugpy.listen(5678)
# print("Waiting for debugger attach")
# debugpy.wait_for_client()


if __name__ == "__main__":
    # Initialize the parser
    parser = argparse.ArgumentParser(description="Generate player sheets.")

    # Add --players and --teams options
    parser.add_argument(
        '--players',
        nargs='+',  # Allows multiple player names to be passed
        help='List of player names to generate sheets for'
    )

    parser.add_argument(
        '--teams',
        nargs='+',  # Allows multiple team names to be passed
        help='List of team names to generate sheets for'
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    if args.players:
        players = args.players

    teams = None
    if args.teams:
        teams = args.teams
    elif not args.players:
        print("No players or teams provided.")
        # Optionally, set default players or teams here if needed
        players = ['Tarik Skubal', 'Riley Greene']

        print(f"Using default players: {players}")

    if teams:
        for team in teams:
            players = Roster.get_active_roster(team_name = team)

    print(f"Player names: {players}")
    print(f"Team names: {teams}")

    # Generate pitcher summary sheets
    for player in players:
        generate_player_sheet(player)



    

