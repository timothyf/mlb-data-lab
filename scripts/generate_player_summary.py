# python generate_player_summary.py --players 'Tarik Skubal' 'Kerry Carpenter' --year 2024

import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mlb_data_lab.player.player import Player
from mlb_data_lab.summary_sheets.pitcher_summary_sheet import PitcherSummarySheet
from mlb_data_lab.summary_sheets.batter_summary_sheet import BatterSummarySheet
from mlb_data_lab.team.roster import Roster
from mlb_data_lab.team.team import Team
import warnings
from bs4 import MarkupResemblesLocatorWarning
import argparse

# Suppress MarkupResemblesLocatorWarning
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

players_not_found = []

def generate_player_sheet(player_name: str, year: int=2024):
    player = Player.create_from_mlb(player_name=player_name)
    if player is None:
        print(f"Player {player_name} not found.")
        players_not_found.append(player_name)
        return
    if player.player_info.primary_position == 'P':
        summary = PitcherSummarySheet(player, year)
    else:
        summary = BatterSummarySheet(player, year)
    summary.generate_plots()


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

    # Add --year option
    parser.add_argument(
        '--year',
        type=int,  # Ensure year is an integer
        default=2024,  # Set default year to 2024
        help='Specify the year for which the player stats should be generated (default: 2024)'
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
    if teams:
        print(f"Teams: {teams}")

    # Generate player summary sheets for each player with the given year
    for player in players:
        generate_player_sheet(player, year)

    if teams:
        for team in teams:
            team = Team.create_from_mlb(team_name=team)
            team.save_season_roster(year)

    for player in players_not_found:
        print(f"Player {player} not found.")
