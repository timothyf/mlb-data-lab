import os
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from mlb_data_lab.apis.unified_data_client import UnifiedDataClient
from mlb_data_lab.player.player import Player


def fetch_stats_for_player(player_name: str, team: dict, season: int, client: UnifiedDataClient):
    """
    Given a player's name, team info, and season, create the Player object and
    fetch the appropriate season stats. Returns a tuple:
    (stats DataFrame or None, player_name, status string)
    """
    try:
        # Create the Player object using MLB data
        player = Player.create_from_mlb(player_name=player_name, data_client=client)
        if not player:
            print(f"Skipping player: {player_name}")
            return (None, player_name, "skipped")
    
        try:
            # Check the player's primary position and fetch the appropriate stats
            if player.player_info.primary_position == 'P':
                #print(f"Fetching pitching stats for player {player.mlbam_id} - {team['name']}...")
                stats = client.fetch_pitching_stats(
                    mlbam_id=player.mlbam_id,
                    season=season
                )
            else:
                #print(f"Fetching batting stats for player {player.mlbam_id}...")
                stats = client.fetch_batting_stats(
                    mlbam_id=player.mlbam_id,
                    season=season
                )
        except ValueError as ve:
            print(f"ValueError fetching stats for player {player.mlbam_id}: {ve}")
            return (None, player_name, "valueerror")
        except Exception as e:
            print(f"Error fetching stats for player {player.mlbam_id}: {e}")
            return (None, player_name, "error")
    
        if stats is not None and not stats.empty:
            #print (f"Fetched stats for player {player.mlbam_id}: {stats.head()}")
            # Print teamname column from stats DataFrame
            team_abbrev = stats['TeamName'].iloc[0]
            # if team_abbrev == '- - -':
            #     print(f"Player {player.mlbam_id} played for multiple teams.")

            # Add player ID and season metadata
            stats['mlbam_id'] = player.mlbam_id
            stats['season'] = season
            return (stats, player_name, "success")
        else:
            #print(f"No stats returned for player {player.mlbam_id}.")
            return (None, player_name, "no stats")
    except Exception as exc:
        print(f"Error processing player {player_name}: {exc}")
        return (None, player_name, "error")


def download_and_save_season_stats(season: int, output_dir: str) -> None:
    """
    Downloads season-level stats for all players from all MLB teams for a given season,
    and saves the results to a CSV file. Each row in the resulting CSV corresponds to a
    player's season totals.
    
    Parameters:
        season (int): The season year for which to fetch player stats.
        output_dir (str): The directory in which the CSV file should be saved.
    """
    client = UnifiedDataClient()
    
    # List of MLB team IDs. Adjust this list as needed.
    mlb_team_ids = [
        109, 144, 110, 111, 112, 145, 113, 114, 115, 116,
        117, 118, 108, 119, 146, 158, 142, 121, 147, 133,
        143, 134, 135, 137, 136, 138, 139, 140, 141, 120
    ]
    
    all_stats = []       # To collect the DataFrames returned per player
    skipped_players = [] # For players that could not be processed
    errored_players = [] # For players that encountered an error
    no_stats_players = [] # For players that returned no stats
    no_fangraphs_id = [] # For players that do not have a Fangraphs ID

    # Create a thread pool executor for concurrent fetching of player stats.
    futures = []
   # max_workers = 5  # 378 seconds
   # max_workers = 10  # 170.52 seconds
    max_workers = 15  # 147.15 seconds
   # max_workers = 20  # 147.43 seconds
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Process teams sequentially but fetch each player's stats concurrently.
        for team_id in mlb_team_ids:
            try:
                team = client.fetch_team(team_id)
            except Exception as e:
                print(f"Error fetching team with ID {team_id}: {e}")
                continue

            try:
                roster = client.fetch_team_roster(team_id, season)
            except Exception as e:
                print(f"Error fetching roster for team {team_id}: {e}")
                continue
    
            # Submit each player's stat-fetching task to the thread pool.
            for player_name in roster:
                future = executor.submit(fetch_stats_for_player, player_name, team, season, client)
                futures.append(future)
    
    # Process the futures as they complete.
    for future in as_completed(futures):
        stats, player_name, status = future.result()
        if stats is not None:
            all_stats.append(stats)
            if len(all_stats) % 20 == 0:
                print(f"Fetched stats for {len(all_stats)} players so far...")
        elif status == "skipped":
            skipped_players.append(player_name)
        elif status == "error":
            errored_players.append(player_name)
        elif status == "no stats":
            no_stats_players.append(player_name)
        elif status == "valueerror":
            no_fangraphs_id.append(player_name)
        else:
            print(f"Unknown status for player {player_name}: {status}")
    
    # If stats have been gathered, combine them and save to CSV.
    if all_stats:
        season_stats_df = pd.concat(all_stats, ignore_index=True)
        
        # Ensure the output directory exists.
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"stats_{season}.csv")
        
        season_stats_df.to_csv(file_path, index=False)
        print(f"Season {season} stats saved to {file_path}")
        print(f"Players processed: {len(all_stats)}")
        print(f"Skipped players count: {len(skipped_players)}")
        print(f"Errored players count: {len(errored_players)}")
        print(f"No Fangraphs ID players count: {len(no_fangraphs_id)}")
        print(f"No stats players count: {len(no_stats_players)}")
        print(f"\nSkipped players: \n{skipped_players}")
        print(f"\nErrored players: \n{errored_players}")
        print(f"\nNo stats players: \n{no_stats_players}")
        print(f"\nNo Fangraphs ID players: \n{no_fangraphs_id}")
    else:
        print("No player stats were fetched for this season.")


if __name__ == '__main__':
    # Example usage: Download the 2024 season stats and save to data/season_stats.
    output_directory = os.path.join("data", "season_stats")
    start_time = time.perf_counter()
    download_and_save_season_stats(season=2024, output_dir=output_directory)
    end_time = time.perf_counter()
    
    elapsed_time = end_time - start_time
    print(f"Total time elapsed: {elapsed_time:.2f} seconds")




