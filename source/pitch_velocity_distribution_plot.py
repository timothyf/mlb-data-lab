
import math
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from data_fetcher import DataFetcher
from constants import pitch_colors
from config import FontConfig


class PitchVelocityDistributionPlot:

    def __init__(self, player):
        self.pitcher = player
        self.config = FontConfig()
        

    def plot(self,  df: pd.DataFrame,
                    ax: plt.Axes,
                    gs: gridspec,
                    gs_x: list,
                    gs_y: list,
                    fig: plt.Figure,
                    df_statcast_group: pd.DataFrame):

        # Create a dictionary mapping pitch types to their colors
        dict_colour = dict(zip(pitch_colors.keys(), [pitch_colors[key]['colour'] for key in pitch_colors]))

        # Get the count of each pitch type and sort them in descending order
        sorted_value_counts = df['pitch_type'].value_counts().sort_values(ascending=False)

        # Get the list of pitch types ordered from most to least frequent
        items_in_order = sorted_value_counts.index.tolist()

        # Turn off the axis and set the title for the main plot
        ax.axis('off')
        ax.set_title('Pitch Velocity Distribution', fontdict=self.config.font_properties['titles'], pad=15)

        # Create a grid for the inner subplots
        inner_grid_1 = gridspec.GridSpecFromSubplotSpec(len(items_in_order), 1, subplot_spec=gs[gs_x[0]:gs_x[-1], gs_y[0]:gs_y[-1]])
        ax_top = []

        # Create subplots for each pitch type
        for inner in inner_grid_1:
            ax_top.append(fig.add_subplot(inner))

        ax_number = 0

        # Loop through each pitch type and plot the velocity distribution
        for i in items_in_order:
            # Check if all release speeds for the pitch type are the same
            if np.unique(df[df['pitch_type'] == i]['release_speed']).size == 1:
                # Plot a single line if all values are the same
                ax_top[ax_number].plot([np.unique(df[df['pitch_type'] == i]['release_speed']),
                                        np.unique(df[df['pitch_type'] == i]['release_speed'])], [0, 1], linewidth=4,
                                    color=dict_colour[df[df['pitch_type'] == i]['pitch_type'].values[0]], zorder=20)
            else:
                # Plot the KDE for the release speeds
                sns.kdeplot(df[df['pitch_type'] == i]['release_speed'], ax=ax_top[ax_number], fill=True,
                            clip=(df[df['pitch_type'] == i]['release_speed'].min(), df[df['pitch_type'] == i]['release_speed'].max()),
                            color=dict_colour[df[df['pitch_type'] == i]['pitch_type'].values[0]])
            
            # Plot the mean release speed for the current data
            df_average = df[df['pitch_type'] == i]['release_speed']
            ax_top[ax_number].plot([df_average.mean(), df_average.mean()],
                                [ax_top[ax_number].get_ylim()[0], ax_top[ax_number].get_ylim()[1]],
                                color=dict_colour[df[df['pitch_type'] == i]['pitch_type'].values[0]],
                                linestyle='--')

            # Plot the mean release speed for the statcast group data
            df_average = df_statcast_group[df_statcast_group['pitch_type'] == i]['release_speed']
            ax_top[ax_number].plot([df_average.mean(), df_average.mean()],
                                [ax_top[ax_number].get_ylim()[0], ax_top[ax_number].get_ylim()[1]],
                                color=dict_colour[df[df['pitch_type'] == i]['pitch_type'].values[0]],
                                linestyle=':')

            # Set the x-axis limits
            ax_top[ax_number].set_xlim(math.floor(df['release_speed'].min() / 5) * 5, math.ceil(df['release_speed'].max() / 5) * 5)
            ax_top[ax_number].set_xlabel('')
            ax_top[ax_number].set_ylabel('')

            # Hide the top, right, and left spines for all but the last subplot
            if ax_number < len(items_in_order) - 1:
                ax_top[ax_number].spines['top'].set_visible(False)
                ax_top[ax_number].spines['right'].set_visible(False)
                ax_top[ax_number].spines['left'].set_visible(False)
                ax_top[ax_number].tick_params(axis='x', colors='none')

            # Set the x-ticks and y-ticks
            ax_top[ax_number].set_xticks(range(math.floor(df['release_speed'].min() / 5) * 5, math.ceil(df['release_speed'].max() / 5) * 5, 5))
            ax_top[ax_number].set_yticks([])
            ax_top[ax_number].grid(axis='x', linestyle='--')

            # Add text label for the pitch type
            ax_top[ax_number].text(-0.01, 0.5, i, transform=ax_top[ax_number].transAxes,
                                fontsize=14, va='center', ha='right')
            ax_number += 1

        # Hide the top, right, and left spines for the last subplot
        ax_top[-1].spines['top'].set_visible(False)
        ax_top[-1].spines['right'].set_visible(False)
        ax_top[-1].spines['left'].set_visible(False)

        # Set the x-ticks and x-label for the last subplot
        ax_top[-1].set_xticks(list(range(math.floor(df['release_speed'].min() / 5) * 5, math.ceil(df['release_speed'].max() / 5) * 5, 5)))
        ax_top[-1].set_xlabel('Velocity (mph)')
