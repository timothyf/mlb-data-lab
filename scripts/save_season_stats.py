
import time
import argparse
from mlb_data_lab.stats.save_season_stats import download_and_save_season_stats


if __name__ == "__main__":
    # Initialize the parser
    parser = argparse.ArgumentParser(description="Generate player sheets.")
    # Add --year option
    parser.add_argument(
        '--season',
        type=int,  # Ensure year is an integer
        default=2024,  # Set default year to 2024
        help='Specify the season for which stats should be saved (default: 2024)'
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    season = args.season

    start_time = time.perf_counter()
    download_and_save_season_stats(season=season, output_dir='output/season_stats')
    end_time = time.perf_counter()

    elapsed_time = end_time - start_time
    print(f"Total time elapsed: {elapsed_time:.2f} seconds")

