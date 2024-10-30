# Standard library imports
import matplotlib.pyplot as plt
import pandas as pd

# Application-specific imports
from mlb_stats.config import StatsConfig
from mlb_stats.apis.pybaseball_client import PybaseballClient
from mlb_stats.components.stats_table import StatsTable
from mlb_stats.player.player import Player


class StatsDisplay:
    def __init__(self, player: Player, season: int, stat_type: str):
        self.player = player
        self.stat_type = stat_type
        self.season_stats = StatsConfig().stat_lists[stat_type]
        self.splits_stats = self._fetch_splits_stats(season)


    def display_standard_stats(self, ax: plt.Axes):
        self._plot_stat_data(
            data=self.player.player_standard_stats,
            stat_type='standard',
            ax=ax,
            title='Standard'
        )
 

    def display_advanced_stats(self, ax: plt.Axes):
        if self.player.player_advanced_stats is None:
            print("No stats data available.")
            return

        player_stats_df = self.player.player_advanced_stats[self.player.player_advanced_stats['xMLBAMID'] == self.player.mlbam_id]
        player_stats_df = self._filter_columns(StatsConfig().stat_lists[self.stat_type]['advanced'], player_stats_df)
        if player_stats_df.empty:
            print(f"No advanced stats available for player {self.player.mlbam_id}.")
            return
        
        self._plot_stats_table(player_stats_df, StatsConfig().stat_lists[self.stat_type]['advanced'], ax, 'Advanced', False)


    def plot_splits_stats(self, ax: plt.Axes):
        if self.splits_stats is not None:
            self._plot_stats_table(self.splits_stats, self.season_stats['splits'], ax, 'Splits', is_splits=True)


    def _plot_stat_data(self, data, stat_type: str, ax: plt.Axes, title: str):
        if data is None:
            print(f"No {stat_type} stats data available.")
            return

        filtered_data = self._get_filtered_data(data, stat_type)
        if filtered_data is None or filtered_data.empty:
            print(f"No valid {stat_type} stats available for plotting.")
            return

        self._plot_stats_table(filtered_data, self.season_stats[stat_type], ax, title, is_splits=False)


    def _get_filtered_data(self, data, stat_type):
        """Retrieves and filters data based on `stat_type`."""
        season_data = data.get('season') or next(iter(data.values()))
        stats_df = pd.DataFrame([season_data])

        return self._filter_columns(self.season_stats[stat_type], stats_df)
    

    def _plot_stats_table(self, stats, stat_fields, ax, title=None, is_splits=False):
        stats_table = StatsTable(stats, stat_fields, self.stat_type)
        stats_table.create_table(ax, f"{title} {self.stat_type.capitalize()}", is_splits)

    
    def _filter_columns(self, stat_fields, stats_df):
        """
        Filters the DataFrame to keep only the available columns from stat_fields.
        Handles missing columns gracefully.
        """
        missing_columns = [col for col in stat_fields if col not in stats_df.columns]
        
        if missing_columns:
            print(f"Warning: The following columns are missing from the DataFrame: {missing_columns}")
            available_columns = [col for col in stat_fields if col in stats_df.columns]

            if not available_columns:
                return None  # No valid columns available
            
            stats_df = stats_df[available_columns]
        else:
            stats_df = stats_df[stat_fields]

        return stats_df.reset_index(drop=True)

    def _get_season_stats(self):
        if 'season' in self.player.player_standard_stats:
            return self.player.player_standard_stats['season']
        else:
            # If 'season' key is not present, get the first entry
            first_key = next(iter(self.player.player_standard_stats))
            return self.player.player_standard_stats[first_key]
        
    def _fetch_splits_stats(self, season):
        """Fetches the splits stats based on `stat_type`."""
        if self.stat_type == 'batting':
            return PybaseballClient.fetch_batting_splits_leaderboards(player_bbref=self.player.bbref_id, season=season)
        else:
            return PybaseballClient.fetch_pitching_splits_leaderboards(player_bbref=self.player.bbref_id, season=season)