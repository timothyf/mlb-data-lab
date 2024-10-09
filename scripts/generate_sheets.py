# python generate_sheets.py 'Tarik Skubal' 'Kerry Carpenter'

import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from mlb_summary_sheets import Player
from mlb_summary_sheets.pitching.pitcher_summary_sheet import PitcherSummarySheet
from mlb_summary_sheets.batting.batter_summary_sheet import BatterSummarySheet
import warnings
from bs4 import MarkupResemblesLocatorWarning
import argparse


# Suppress MarkupResemblesLocatorWarning
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


def generate_player_sheet(player_name: str, year: int=2024):
    player = Player.create_from_mlb(player_name=player_name)
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
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate player summary sheets.")
    
    # Add player names argument (optional)
    parser.add_argument(
        'player_names', 
        nargs='*',  # Allows passing zero or more player names
        help="List of player names to generate summary sheets for."
    )

    # Parse the arguments
    args = parser.parse_args()

    # Use hardcoded defaults if no player names are passed in
    if not args.player_names:
        # Default list of players if none are provided
        default_pitchers = ['Tarik Skubal']
        default_batters = ['Kerry Carpenter', 'Riley Greene']
        print("No player names passed in, using default names.")
    else:
        # Use command-line provided names
        default_pitchers = args.player_names
        default_batters = []

    # Generate pitcher summary sheets
    for pitcher in default_pitchers:
        generate_player_sheet(pitcher)

    # Generate batter summary sheets if any were hardcoded
    for batter in default_batters:
        generate_player_sheet(batter)



    

