
import time
import argparse
from pathlib import Path

# Ensure the package can be imported when running from the examples directory
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

from baseball_data_lab.stats.save_season_stats import SeasonStatsDownloader


if __name__ == "__main__":
    # Initialize the parser
    parser = argparse.ArgumentParser(description="Save Season Stats.")
    # Add --year option
    parser.add_argument(
        '--season',
        type=int,  # Ensure year is an integer
        default=2024,  # Set default year to 2024
        help='Specify the season for which stats should be saved (default: 2024)'
    )
    parser.add_argument(
        '--league',
        type=str,  # Ensure year is an integer
        default=None,  
        help='Specify the league for which stats should be saved'
    )
    parser.add_argument(
        '--player_type',
        type=str,  # Ensure year is an integer
        default='batters',  # Set default player_type to 'batters'
        help='Specify the batters or pitcher for which stats should be saved'
    )


    # Parse the command-line arguments
    args = parser.parse_args()

    season = args.season
    league = args.league

    start_time = time.perf_counter()

    downloader = SeasonStatsDownloader(
        season = season,
        output_dir = 'output/season_stats',
        max_workers = 10,
        retry_attempts = 2,
        chunk_size = 300,
        league = league,
        player_type=args.player_type
    )
    downloader.download()

    end_time = time.perf_counter()

    elapsed_time = end_time - start_time
    print(f"Total time elapsed: {elapsed_time:.2f} seconds")

