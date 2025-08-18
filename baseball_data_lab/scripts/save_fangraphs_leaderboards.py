"""CLI to fetch and save Fangraphs leaderboard data."""

import json
import os

from baseball_data_lab.apis.unified_data_client import UnifiedDataClient
from baseball_data_lab.config import DATA_DIR

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
        data_client = UnifiedDataClient()
        batting_data = data_client.fetch_batting_leaderboards_as_json(season)
        save_data_to_json(BATTING_FILE_PATH, batting_data)

        pitching_data = data_client.fetch_pitching_leaderboards_as_json(season)
        save_data_to_json(PITCHING_FILE_PATH, pitching_data)
    except Exception as e:
        print(f"Error fetching leaderboard data for season {season}: {e}")


def main():
    """Entry point for the save-fangraphs-leaderboards CLI."""
    fetch_and_save_leaderboards(SEASON)


if __name__ == "__main__":
    main()
