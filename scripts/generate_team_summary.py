# python generate_team_summary.py --teams 'Detroit Tigers' --year 2024

import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mlb_data_lab.team.team import Team
from mlb_data_lab.summary_sheets.team_batting_sheet import TeamBattingSheet
import warnings
from bs4 import MarkupResemblesLocatorWarning
import argparse

# Suppress MarkupResemblesLocatorWarning
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

players_not_found = []

def generate_team_sheet(team_name: str, year: int=2024):
    team = Team.create_from_mlb(team_name=team_name)
    if team is None:
        print(f"Team {team} not found.")
        return

    summary = TeamBattingSheet(team, year)
    summary.generate_plots()


if __name__ == "__main__":
    # Initialize the parser
    parser = argparse.ArgumentParser(description="Generate team sheets.")

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

    teams = None

    # Get teams from --teams argument
    if args.teams:
        teams = args.teams
    else:
        print("No teams provided.")
        teams = ['Detroit Tigers']
        print(f"Using default team: {teams}")

    # Use the specified year (or the default year 2024)
    year = args.year
    print(f"Year: {year}")
    print(f"Team names: {teams}")

    # Generate player summary sheets for each player with the given year
    for team in teams:
        generate_team_sheet(team, year)


