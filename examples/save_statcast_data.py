"""CLI for saving Statcast data for players."""

import argparse
from pathlib import Path

# Ensure the package can be imported when running from the examples directory
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from baseball_data_lab.player.player import Player
from baseball_data_lab.team.roster import Roster


players_not_found = []


def save_statcast_data(player_name: str, year: int = 2024) -> None:
    """Save Statcast data for a single player."""
    player = Player.create_from_mlb(player_name=player_name)
    if player is None:
        print(f"Player {player_name} not found.")
        players_not_found.append(player_name)
        return

    player.save_statcast_data(year)


def main() -> None:
    """Entry point for the save-statcast-data CLI."""
    parser = argparse.ArgumentParser(description="Save statscast data.")

    parser.add_argument(
        "--players",
        nargs="+",
        help="List of player names to save data for",
    )

    parser.add_argument(
        "--teams",
        nargs="+",
        help="List of team names to save data for",
    )

    parser.add_argument(
        "--year",
        type=int,
        default=2024,
        help="Specify the year for which the player stats should be saved (default: 2024)",
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
    print(f"Team names: {teams}")

    for player in players:
        save_statcast_data(player, year)

    for player in players_not_found:
        print(f"Player {player} not found.")


if __name__ == "__main__":
    main()

