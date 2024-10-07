from matplotlib.ticker import MaxNLocator
import matplotlib.ticker as mtick
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from mlb_summary_sheets.constants import pitch_colors
import math
import numpy as np
from mlb_summary_sheets.config import FontConfig



class RollingPitchUsagePlot:

    def __init__(self, player):
        self.pitcher = player
        self.config = FontConfig()


    def plot(self, df: pd.DataFrame, ax: plt.Axes, window: int):

        # Create a dictionary mapping pitch types to their colors
        dict_colour = dict(zip(pitch_colors.keys(), [pitch_colors[key]['colour'] for key in pitch_colors]))
        
        # Calculate the proportion of each pitch type per game
        df_game_group = pd.DataFrame((df.groupby(['game_pk', 'game_date', 'pitch_type'])['release_speed'].count() /
                                df.groupby(['game_pk', 'game_date'])['release_speed'].count()).reset_index())

        # Create a complete list of games
        all_games = pd.Series(df_game_group['game_pk'].unique())

        # Create a complete list of pitch types
        all_pitch_types = pd.Series(df_game_group['pitch_type'].unique())

        # Create a DataFrame with all combinations of games and pitch types
        all_combinations = pd.MultiIndex.from_product([all_games, all_pitch_types], names=['game_pk', 'pitch_type']).to_frame(index=False)

        # Merge this DataFrame with your original DataFrame to ensure all combinations are included
        df_complete = pd.merge(all_combinations, df_game_group, on=['game_pk', 'pitch_type'], how='left')

        # Fill missing values with 0
        df_complete['release_speed'] = df_complete['release_speed'].fillna(0)

        # Create mappings for game numbers and game dates
        game_list = df.sort_values(by='game_date')['game_pk'].unique()
        range_list = list(range(1, len(game_list) + 1))
        game_to_range = dict(zip(game_list, range_list))
        game_to_date = df.set_index('game_pk')['game_date'].to_dict()

        # Map game dates and game numbers to the complete DataFrame
        df_complete['game_date'] = df_complete['game_pk'].map(game_to_date)
        df_complete = df_complete.sort_values(by='game_date')
        df_complete['game_number'] = df_complete['game_pk'].map(game_to_range)

        # Plot the rolling pitch usage for each pitch type
        sorted_value_counts = df['pitch_type'].value_counts().sort_values(ascending=False)
        items_in_order = sorted_value_counts.index.tolist()
        max_roll = []

        for i in items_in_order:
                sns.lineplot(x=range(1, max(df_complete[df_complete['pitch_type'] == i]['game_number']) + 1),
                        y=df_complete[df_complete['pitch_type'] == i]['release_speed'].rolling(window).sum() / window,
                        color=dict_colour[df[df['pitch_type'] == i]['pitch_type'].values[0]],
                        ax=ax, linewidth=3)
                max_roll.append(np.max(df_complete[df_complete['pitch_type'] == i]['release_speed'].rolling(window).sum() / window))

        # Adjust x-axis limits to start from the window size
        ax.set_xlim(window, len(game_list))

        # Check if the maximum value is NaN
        max_value = max(max_roll)
        if not np.isnan(max_value):
            ax.set_ylim(0, math.ceil(max_value * 10) / 10)
        else:
            ax.set_ylim(0, 1)  # Set a default range if max_value is NaN

        # Set axis labels and title
        ax.set_xlabel('Game', fontdict=self.config.font_properties['axes'])
        ax.set_ylabel('Pitch Usage', fontdict=self.config.font_properties['axes'])
        ax.set_title(f"{window} Game Rolling Pitch Usage", fontdict=self.config.font_properties['titles'], pad=15)

        # Set x-axis to show integer values only
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        # Set y-axis ticks as percentages
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=0))


