import matplotlib.pyplot as plt
import pandas as pd
from mlb_summary_sheets.config import StatsConfig
from mlb_summary_sheets.apis.fangraphs_client import FangraphsClient
from mlb_summary_sheets.components.stats_table import StatsTable
from mlb_summary_sheets.player import Player
from mlb_summary_sheets.apis.pybaseball_client import PybaseballClient
from mlb_summary_sheets.apis.mlb_stats_client import MlbStatsClient


class StatsDisplay:
    def __init__(self, player: Player, season: int, stat_type: str):
        self.player = player
        self.season = season
        self.stat_type = stat_type
        self.standard_stats = StatsConfig().stat_lists[stat_type]['standard']
        self.advanced_stats = StatsConfig().stat_lists[stat_type]['advanced']
        self.splits_stats_list = StatsConfig().stat_lists[stat_type]['splits']
        if stat_type == 'batting':
            self.standard_stat_data = MlbStatsClient.fetch_player_stats(player.mlbam_id, season)
            self.advanced_stat_data = FangraphsClient.fetch_leaderboards(season=self.season, stat_type=self.stat_type)
            self.splits_stats = PybaseballClient.fetch_batting_splits_leaderboards(player_bbref=self.player.bbref_id, season=self.season)
        else:
            self.stats = FangraphsClient.fetch_leaderboards(season=self.season, stat_type=self.stat_type)
            self.splits_stats = PybaseballClient.fetch_pitching_splits_leaderboards(player_bbref=self.player.bbref_id, season=self.season)


    def display_standard_stats(self, ax: plt.Axes):
        # Handle batting stats
        if self.stat_type == 'batting':
            if self.standard_stat_data is None:
                return
            
            df = self._flatten_batting_stats()

            if df is None or df.empty:
                print("No valid data available for plotting.")
                return

            missing_columns = [col for col in self.standard_stats if col not in df.columns]
            if missing_columns:
                print(f"Warning: The following columns are missing from the DataFrame: {missing_columns}")
                # You can decide whether to raise an error, fill missing columns with default values, or skip processing
                # For example, you could skip missing columns:
                available_columns = [col for col in self.standard_stats if col in df.columns]
                if not available_columns:
                    print("No valid columns available for plotting.")
                    return

                # Only keep available columns
                df = df[available_columns].reset_index(drop=True)           

            df = df[self.standard_stats].reset_index(drop=True)
            df_player = df
        # Handle pitching stats
        else:
            if self.stats is None:
                return
            df = self.stats[self.stats['xMLBAMID'] == self.player.mlbam_id]

            if df.empty:
                print("No valid data found for player.")
                return      
            
         # Filter and prepare for plotting
        df_player = self._filter_columns(df)
        
        # Display the stats table
        stats_table = StatsTable(df_player, self.standard_stats, self.stat_type)
        stats_table.create_table(ax, f"Standard {self.stat_type.capitalize()}")


    def display_advanced_stats(self, ax: plt.Axes):
        # Determine which stats data to use (batting or other stat types)
        stats = self.advanced_stat_data if self.stat_type == 'batting' else self.stats

        # Return early if there's no data available
        if stats is None:
            print("No stats data available.")
            return

        # Filter the data for the specific player
        df_player = stats[stats['xMLBAMID'] == self.player.mlbam_id]

        # Check if any advanced stats columns are missing
        missing_columns = [col for col in self.advanced_stats if col not in df_player.columns]
        if missing_columns:
            print(f"Warning: The following columns are missing from the DataFrame: {missing_columns}")
            # Optionally handle missing columns (e.g., skip or fill with default values)
            available_columns = [col for col in self.advanced_stats if col in df_player.columns]
            
            if not available_columns:
                print("No valid advanced stats columns available for plotting.")
                return
            
            # Keep only the available columns
            df_player = df_player[available_columns]

        # Handle the case where no data is available after filtering by the player ID
        if df_player.empty:
            print(f"No advanced stats available for player {self.player.mlbam_id}.")
            return

        # Reset index for the DataFrame
        df_player = df_player.reset_index(drop=True)

        # Display the stats table
        stats_table = StatsTable(df_player, self.advanced_stats, self.stat_type)
        stats_table.create_table(ax, f"Advanced {self.stat_type.capitalize()}")


    def display_splits_stats(self, ax: plt.Axes):
        if self.splits_stats is None:
            return
        stats_table = StatsTable(self.splits_stats, self.splits_stats_list, self.stat_type)
        stats_table.create_table(ax, "Splits {}".format(self.stat_type.capitalize()), True)


    def _flatten_batting_stats(self):
        """
        Flattens the batting stats data for easier DataFrame creation.
        """
        flattened_data = [
            {
                **entry['stat'],
                'season': entry['season'],
                'player': entry['player']['fullName'],
                'gameType': entry['gameType']
            }
            for entry in self.standard_stat_data
        ]
        
        return pd.DataFrame(flattened_data) if flattened_data else None
    
    def _filter_columns(self, df):
        """
        Filters the DataFrame to keep only the available columns from self.standard_stats.
        Handles missing columns gracefully.
        """
        missing_columns = [col for col in self.standard_stats if col not in df.columns]
        
        if missing_columns:
            print(f"Warning: The following columns are missing from the DataFrame: {missing_columns}")
            available_columns = [col for col in self.standard_stats if col in df.columns]

            if not available_columns:
                return None  # No valid columns available
            
            df = df[available_columns]
        else:
            df = df[self.standard_stats]

        return df.reset_index(drop=True)
