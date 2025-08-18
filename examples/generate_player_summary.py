"""CLI for generating player summary sheets."""

import argparse
import warnings
from bs4 import MarkupResemblesLocatorWarning

from baseball_data_lab.player.player import Player
from baseball_data_lab.summary_sheets.pitcher_summary_sheet import PitcherSummarySheet
from baseball_data_lab.summary_sheets.batter_summary_sheet import BatterSummarySheet
from baseball_data_lab.team.roster import Roster
from baseball_data_lab.team.team import Team

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


def main():
    """Entry point for the generate-player-summary CLI."""
    parser = argparse.ArgumentParser(description="Generate player sheets.")

    parser.add_argument(
        "--players",
        nargs="+",
        help="List of player names to generate sheets for",
    )

    parser.add_argument(
        "--teams",
        nargs="+",
        help="List of team names to generate sheets for",
    )

    parser.add_argument(
        "--year",
        type=int,
        default=2024,
        help="Specify the year for which the player stats should be generated (default: 2024)",
    )

    args = parser.parse_args()

    players = []
    teams = None

    if args.players:
        players = args.players

    if args.teams:
        teams = args.teams
    elif not args.players:
        print("No players or teams provided.")
        players = ["Tarik Skubal", "Riley Greene"]
        print(f"Using default players: {players}")

    if teams:
        for team in teams:
            players += Roster.get_season_roster(team_name=team, year=args.year)

    year = args.year
    print(f"Year: {year}")

    print(f"Player names: {players}")
    if teams:
        print(f"Teams: {teams}")

    for player in players:
        generate_player_sheet(player, year)

    if teams:
        for team in teams:
            team = Team.create_from_mlb(team_name=team)
            team.save_season_roster(year)

    for player in players_not_found:
        print(f"Player {player} not found.")


if __name__ == "__main__":
    main()
