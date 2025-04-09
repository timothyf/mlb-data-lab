import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.ticker import MaxNLocator
import seaborn as sns

from mlb_data_lab.config import FontConfig, pitch_colors


class RollingPitchUsagePlot:
    def __init__(self, player):
        self.pitcher = player
        self.config = FontConfig()

    def get_color_mapping(self):
        """Return a dictionary mapping pitch types to colors."""
        return {key: pitch_colors[key]['color'] for key in pitch_colors}

    def build_complete_pitch_data(self, pitch_data: pd.DataFrame):
        """
        Calculate game-level pitch type proportions and return a DataFrame 
        with all game-pitch_type combinations.
        Also returns the unique list of game ids (in order of game_date).
        """
        # Calculate the proportion of each pitch type per game.
        game_pitch_distribution = (
            pitch_data.groupby(['game_pk', 'game_date', 'pitch_type'])['release_speed']
            .count() /
            pitch_data.groupby(['game_pk', 'game_date'])['release_speed']
            .count()
        ).reset_index(name='release_speed')

        # Get the list of all games and all pitch types.
        all_games = pd.Series(game_pitch_distribution['game_pk'].unique())
        all_pitch_types = pd.Series(game_pitch_distribution['pitch_type'].unique())

        # Create a DataFrame with all combinations.
        all_combinations = pd.MultiIndex.from_product(
            [all_games, all_pitch_types],
            names=['game_pk', 'pitch_type']
        ).to_frame(index=False)

        # Merge to ensure every combination appears.
        complete_pitch_data = pd.merge(
            all_combinations,
            game_pitch_distribution,
            on=['game_pk', 'pitch_type'],
            how='left'
        )
        # Fill missing values with 0.
        complete_pitch_data['release_speed'] = complete_pitch_data['release_speed'].fillna(0)

        # Create mappings for game numbers and dates.
        game_list = pitch_data.sort_values(by='game_date')['game_pk'].unique()
        game_to_range = dict(zip(game_list, range(1, len(game_list) + 1)))
        game_to_date = pitch_data.set_index('game_pk')['game_date'].to_dict()

        complete_pitch_data['game_date'] = complete_pitch_data['game_pk'].map(game_to_date)
        complete_pitch_data = complete_pitch_data.sort_values(by='game_date')
        complete_pitch_data['game_number'] = complete_pitch_data['game_pk'].map(game_to_range)

        return complete_pitch_data, game_list

    def plot_rolling_usage(self, complete_pitch_data: pd.DataFrame, pitch_data: pd.DataFrame,
                             window: int, ax: plt.Axes, dict_color: dict):
        """
        Plot a rolling average of pitch usage for each pitch type.
        Returns a list of maximum rolling averages (one per pitch type) for setting the y-axis limit.
        """
        # Determine pitch types ordered by overall frequency.
        sorted_value_counts = pitch_data['pitch_type'].value_counts().sort_values(ascending=False)
        pitch_types_ordered = sorted_value_counts.index.tolist()

        max_roll_values = []
        for pitch in pitch_types_ordered:
            subset = complete_pitch_data[complete_pitch_data['pitch_type'] == pitch]
            game_nums = subset['game_number']
            # Calculate the rolling average usage (sum over window divided by window).
            rolling_usage = subset['release_speed'].rolling(window).sum() / window

            # Use the pitch-type's color.
            color = dict_color.get(pitch, 'black')
            # Plot the line. The x-axis should span the game number range.
            sns.lineplot(
                x=range(1, int(max(game_nums)) + 1),
                y=rolling_usage,
                color=color,
                ax=ax,
                linewidth=3,
                label=pitch
            )
            max_roll_values.append(np.nanmax(rolling_usage))
        return max_roll_values

    def set_axes_limits_and_labels(self, ax: plt.Axes, game_list, window: int, max_roll_values):
        """
        Adjusts the axes limits and sets labels/titles on the given axes.
        """
        # Set x-axis to start at the window and end at the total number of games.
        ax.set_xlim(window, len(game_list))

        # Determine and set the y-axis limits.
        max_value = max(max_roll_values) if max_roll_values else 1
        if not np.isnan(max_value):
            ax.set_ylim(0, math.ceil(max_value * 10) / 10)
        else:
            ax.set_ylim(0, 1)

        # Set axis labels and title.
        ax.set_xlabel('Game', fontdict=self.config.font_properties['axes'])
        ax.set_ylabel('Pitch Usage', fontdict=self.config.font_properties['axes'])
        ax.set_title(f"{window} Game Rolling Pitch Usage", fontdict=self.config.font_properties['titles'], pad=15)

        # Configure tick formatting.
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=0))

    def plot(self, pitch_data: pd.DataFrame, ax: plt.Axes, window: int):
        """Top-level method to generate the rolling pitch usage plot."""
        dict_color = self.get_color_mapping()

        # Prepare the complete pitch data with all game-pitch_type combinations.
        complete_pitch_data, game_list = self.build_complete_pitch_data(pitch_data)

        # Plot the rolling usage lines for each pitch type.
        max_roll_values = self.plot_rolling_usage(complete_pitch_data, pitch_data, window, ax, dict_color)
        if not max_roll_values:
            return

        # Adjust axes limits and labels.
        self.set_axes_limits_and_labels(ax, game_list, window, max_roll_values)
