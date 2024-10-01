import pandas as pd
import matplotlib.pyplot as plt
import pybaseball as pyb
from data_fetcher import FANGRAPHS_BASE_URL
from data_fetcher import DataFetcher
from fangraphs_stats import fangraphs_stats_dict


def format_stat(value, format_spec):
    """Function to apply appropriate formatting to a stat."""
    if format_spec == 'percent':
        return f"{value * 100:.1f}%"
    else:
        return format(value, format_spec)


class PitchingStats:
    def __init__(self, pitcher_id: int, season: int):
        self.pitcher_id = pitcher_id
        self.season = season
        self.standard_stats = ['W', 'L', 'ERA', 'G', 'GS', 'QS', 'CG', 'ShO', 'SV', 'HLD', 'BS', 'IP', 
                               'TBF', 'H', 'R', 'ER', 'HR', 'BB', 'IBB', 'HBP', 'WP', 'BK', 'SO']
        self.advanced_stats =['K/9', 'BB/9', 'K/BB', 'H/9', 'HR/9', 'K%', 'BB%', 'K-BB%', 'AVG', 'WHIP', 'BABIP', 
                              'LOB%', 'ERA-', 'FIP-','FIP', 'RS/9', 'Swing%']

    def display_standard_stats(self, ax: plt.Axes, fontsize: int = 20):
        df_fangraphs = DataFetcher.fetch_fangraphs_pitching_leaderboards(season=self.season)
        df_fangraphs_pitcher = df_fangraphs[df_fangraphs['xMLBAMID'] == self.pitcher_id][self.standard_stats].reset_index(drop=True)

        # Ensure the column can hold strings (object dtype)
        df_fangraphs_pitcher = df_fangraphs_pitcher.astype('object')

        # Assign the formatted values
        df_fangraphs_pitcher.loc[0] = [
            format_stat(df_fangraphs_pitcher[x][0], fangraphs_stats_dict[x]['format'])
            if df_fangraphs_pitcher[x][0] != '---' else '---' 
            for x in df_fangraphs_pitcher
        ]

        table_fg = ax.table(cellText=df_fangraphs_pitcher.values, colLabels=self.standard_stats, cellLoc='center', bbox=[0.00, 0.0, 1, 1])
        table_fg.set_fontsize(fontsize)

        # Adjust column headers
        new_column_names = [
            fangraphs_stats_dict[x]['table_header'] if x in df_fangraphs_pitcher else '---' for x in self.standard_stats
        ]
        for i, col_name in enumerate(new_column_names):
            table_fg.get_celld()[(0, i)].get_text().set_text(col_name)

        ax.set_title("Standard Pitching Stats", fontsize=18, pad=10, fontweight='bold')

        ax.axis('off')

    def display_advanced_stats(self, ax: plt.Axes, fontsize: int = 20):
        df_fangraphs = DataFetcher.fetch_fangraphs_pitching_leaderboards(season=self.season)
        df_fangraphs_pitcher = df_fangraphs[df_fangraphs['xMLBAMID'] == self.pitcher_id][self.advanced_stats].reset_index(drop=True)

        # Ensure the column can hold strings (object dtype)
        df_fangraphs_pitcher = df_fangraphs_pitcher.astype('object')

        # Assign the formatted values
        df_fangraphs_pitcher.loc[0] = [
            format_stat(df_fangraphs_pitcher[x][0], fangraphs_stats_dict[x]['format'])
            if df_fangraphs_pitcher[x][0] != '---' else '---' 
            for x in df_fangraphs_pitcher
        ]

        table_fg = ax.table(cellText=df_fangraphs_pitcher.values, colLabels=self.advanced_stats, cellLoc='center', bbox=[0.00, 0.0, 1, 1])
        table_fg.set_fontsize(fontsize)

        # Adjust column headers
        new_column_names = [
            fangraphs_stats_dict[x]['table_header'] if x in df_fangraphs_pitcher else '---' for x in self.advanced_stats
        ]
        for i, col_name in enumerate(new_column_names):
            table_fg.get_celld()[(0, i)].get_text().set_text(col_name)

        ax.set_title("Advanced Pitching Stats", fontsize=18, pad=10, fontweight='bold')

        ax.axis('off')
