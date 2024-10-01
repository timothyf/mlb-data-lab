import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from constants import pitch_colors
from config import FontConfig



class PitchBreakPlot:

    def __init__(self, player):
        self.pitcher = player
        self.config = FontConfig()

    def plot(self, df: pd.DataFrame, ax: plt.Axes):

        # Create a dictionary mapping pitch types to their colors
        dict_colour = dict(zip(pitch_colors.keys(), [pitch_colors[key]['colour'] for key in pitch_colors]))

        # Check if the pitcher throws with the right hand
        if df['p_throws'].values[0] == 'R':
            sns.scatterplot(ax=ax,
                            x=df['pfx_x']*-1,
                            y=df['pfx_z'],
                            hue=df['pitch_type'],
                            palette=dict_colour,
                            ec='black',
                            alpha=1,
                            zorder=2)

        # Check if the pitcher throws with the left hand
        if df['p_throws'].values[0] == 'L':
            sns.scatterplot(ax=ax,
                            x=df['pfx_x'],
                            y=df['pfx_z'],
                            hue=df['pitch_type'],
                            palette=dict_colour,
                            ec='black',
                            alpha=1,
                            zorder=2)

        # Draw horizontal and vertical lines at y=0 and x=0 respectively
        ax.axhline(y=0, color='#808080', alpha=0.5, linestyle='--', zorder=1)
        ax.axvline(x=0, color='#808080', alpha=0.5, linestyle='--', zorder=1)

        # Set the labels for the x and y axes
        ax.set_xlabel('Horizontal Break (in)', fontdict=self.config.font_properties['axes'])
        ax.set_ylabel('Induced Vertical Break (in)', fontdict=self.config.font_properties['axes'])

        # Set the title of the plot
        ax.set_title("Pitch Breaks", fontdict=self.config.font_properties['titles'], pad=15)

        # Remove the legend
        ax.get_legend().remove()

        # Set the tick positions and labels for the x and y axes
        ax.set_xticks(range(-20, 21, 10))
        ax.set_xticklabels(range(-20, 21, 10), fontdict=self.config.font_properties['default'])
        ax.set_yticks(range(-20, 21, 10))
        ax.set_yticklabels(range(-20, 21, 10), fontdict=self.config.font_properties['default'])

        # Set the limits for the x and y axes
        ax.set_xlim((-25, 25))
        ax.set_ylim((-25, 25))

        # Add text annotations based on the pitcher's throwing hand
        if df['p_throws'].values[0] == 'R':
            ax.text(-24.2, -24.2, s='← Glove Side', fontstyle='italic', ha='left', va='bottom',
                    bbox=dict(facecolor='white', edgecolor='black'), fontsize=10, zorder=3)
            ax.text(24.2, -24.2, s='Arm Side →', fontstyle='italic', ha='right', va='bottom',
                    bbox=dict(facecolor='white', edgecolor='black'), fontsize=10, zorder=3)

        if df['p_throws'].values[0] == 'L':
            ax.invert_xaxis()
            ax.text(24.2, -24.2, s='← Arm Side', fontstyle='italic', ha='left', va='bottom',
                    bbox=dict(facecolor='white', edgecolor='black'), fontsize=10, zorder=3)
            ax.text(-24.2, -24.2, s='Glove Side →', fontstyle='italic', ha='right', va='bottom',
                    bbox=dict(facecolor='white', edgecolor='black'), fontsize=10, zorder=3)

        # Set the aspect ratio of the plot to be equal
        ax.set_aspect('equal', adjustable='box')

        # Format the x and y axis tick labels as integers
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: int(x)))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: int(x)))

