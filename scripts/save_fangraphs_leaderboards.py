import sys
import os
import json


# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mlb_summary_sheets.apis.fangraphs_client import FangraphsClient
from mlb_summary_sheets.config import DATA_DIR

# Constants
SEASON = 2024  # Replace with the desired season
BATTING_FILE_PATH = f"{DATA_DIR}/fangraphs_leaderboards/batting_leaderboard.json"
PITCHING_FILE_PATH = f"{DATA_DIR}/fangraphs_leaderboards/pitching_leaderboard.json"

# Ensure the directory exists
def ensure_directory_exists(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

# Save data to JSON file
def save_data_to_json(file_path, data):
    try:
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data successfully saved to {file_path}")
    except Exception as e:
        print(f"Failed to save data to {file_path}: {e}")

# Fetch and save leaderboard data
def fetch_and_save_leaderboards(season):
    ensure_directory_exists(BATTING_FILE_PATH)

    try:
        # Fetch and save batting leaderboard data
        batting_data = FangraphsClient.fetch_batting_leaderboards_as_json(season)
        save_data_to_json(BATTING_FILE_PATH, batting_data)

        # Fetch and save pitching leaderboard data
        pitching_data = FangraphsClient.fetch_pitching_leaderboards_as_json(season)
        save_data_to_json(PITCHING_FILE_PATH, pitching_data)
    except Exception as e:
        print(f"Error fetching leaderboard data for season {season}: {e}")

if __name__ == "__main__":
    fetch_and_save_leaderboards(SEASON)
