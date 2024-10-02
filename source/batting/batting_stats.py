import pandas as pd
import matplotlib.pyplot as plt
import pybaseball as pyb
from data_fetcher import FANGRAPHS_BASE_URL
from data_fetcher import DataFetcher
from fangraphs_stats import fangraphs_batting_stats_dict


def format_stat(value, format_spec):
    """Function to apply appropriate formatting to a stat."""
    if format_spec == 'percent':
        return f"{value * 100:.1f}%"
    else:
        return format(value, format_spec)


class BattingStats:
    def __init__(self, batter_id: int, season: int):
        self.batter_id = batter_id
        self.season = season
        self.standard_stats = ['G', 'PA', 'AB', 'H', '1B', '2B', '3B', 'HR', 'R', 'RBI', 'BB', 'IBB', 'SO', 'HBP', 
                               'SF', 'SH', 'GDP', 'SB', 'CS', 'AVG']
        self.advanced_stats =['BB%', 'K%', 'BB/K', 'AVG', 'OBP', 'SLG', 'OPS', 'ISO', 'Spd', 'BABIP', 'UBR', 'XBR',
                              'wRC', 'wRAA',
                              'wOBA', 'wRC+', 'WAR']
        self.fangraphs_batting_stats = DataFetcher.fetch_fangraphs_batting_leaderboards(season=self.season)
        

    def display_standard_stats(self, ax: plt.Axes, fontsize: int = 20):
        df_fangraphs = self.fangraphs_batting_stats
        df_fangraphs_batter = df_fangraphs[df_fangraphs['xMLBAMID'] == self.batter_id][self.standard_stats].reset_index(drop=True)

        # Ensure the column can hold strings (object dtype)
        df_fangraphs_batter = df_fangraphs_batter.astype('object')

        # Assign the formatted values
        df_fangraphs_batter.loc[0] = [
            format_stat(df_fangraphs_batter[x][0], fangraphs_batting_stats_dict[x]['format'])
            if df_fangraphs_batter[x][0] != '---' else '---' 
            for x in df_fangraphs_batter
        ]

        table_fg = ax.table(cellText=df_fangraphs_batter.values, colLabels=self.standard_stats, cellLoc='center', bbox=[0.00, 0.0, 1, 1])
        table_fg.set_fontsize(fontsize)

        # Adjust column headers
        new_column_names = [
            fangraphs_batting_stats_dict[x]['table_header'] if x in df_fangraphs_batter else '---' for x in self.standard_stats
        ]
        for i, col_name in enumerate(new_column_names):
            table_fg.get_celld()[(0, i)].get_text().set_text(col_name)

        ax.set_title("Standard Batting Stats", fontsize=18, pad=10, fontweight='bold')

        ax.axis('off')


    def display_advanced_stats(self, ax: plt.Axes, fontsize: int = 20):
        df_fangraphs = self.fangraphs_batting_stats
        df_fangraphs_batter = df_fangraphs[df_fangraphs['xMLBAMID'] == self.batter_id][self.advanced_stats].reset_index(drop=True)

        # Ensure the column can hold strings (object dtype)
        df_fangraphs_batter = df_fangraphs_batter.astype('object')

        # Assign the formatted values
        df_fangraphs_batter.loc[0] = [
            format_stat(df_fangraphs_batter[x][0], fangraphs_batting_stats_dict[x]['format'])
            if df_fangraphs_batter[x][0] != '---' else '---' 
            for x in df_fangraphs_batter
        ]

        table_fg = ax.table(cellText=df_fangraphs_batter.values, colLabels=self.advanced_stats, cellLoc='center', bbox=[0.00, 0.0, 1, 1])
        table_fg.set_fontsize(fontsize)

        # Adjust column headers
        new_column_names = [
            fangraphs_batting_stats_dict[x]['table_header'] if x in df_fangraphs_batter else '---' for x in self.advanced_stats
        ]
        for i, col_name in enumerate(new_column_names):
            table_fg.get_celld()[(0, i)].get_text().set_text(col_name)

        ax.set_title("Advanced Batting Stats", fontsize=18, pad=10, fontweight='bold')

        ax.axis('off')
