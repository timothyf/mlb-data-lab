"""CLI for generating team summary sheets."""

import argparse
import warnings
from bs4 import MarkupResemblesLocatorWarning

from baseball_data_lab.team.team import Team
from baseball_data_lab.summary_sheets.team_batting_sheet import TeamBattingSheet
from baseball_data_lab.summary_sheets.team_pitching_sheet import TeamPitchingSheet

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


def generate_team_sheet(team_name: str, year: int=2024):
    team = Team.create_from_mlb(team_name=team_name)
    if team is None:
        print(f"Team {team} not found.")
        return

    # Generate team batting sheet
    summary = TeamBattingSheet(team, year)
    summary.generate_plots()

    # Generate team pitching sheet
    summary = TeamPitchingSheet(team, year)
    summary.generate_plots()


def main():
    """Entry point for the generate-team-summary CLI."""
    parser = argparse.ArgumentParser(description="Generate team sheets.")

    parser.add_argument(
        "--teams",
        nargs="+",
        help="List of team names to generate sheets for",
    )

    parser.add_argument(
        "--year",
        type=int,
        default=2024,
        help="Specify the year for which the team stats should be generated (default: 2024)",
    )

    args = parser.parse_args()

    teams = None

    if args.teams:
        teams = args.teams
    else:
        print("No teams provided.")
        teams = ["Detroit Tigers"]
        print(f"Using default team: {teams}")

    year = args.year
    print(f"Year: {year}")
    print(f"Team names: {teams}")

    for team in teams:
        generate_team_sheet(team, year)


if __name__ == "__main__":
    main()
