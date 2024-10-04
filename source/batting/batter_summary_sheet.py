import matplotlib.pyplot as plt
from player import Player
from team import Team
import seaborn as sns
import matplotlib as mpl
import matplotlib.gridspec as gridspec
from stats.base_stats import BattingStats
from batting.batting_spray_chart import BattingSprayChart

from pybaseball import statcast_batter
from constants import statcast_events
from plotting import Plotting


class BatterSummarySheet:

    def __init__(self, player: Player, season: int):
        self.player = player
        self.team = Team(player.team_id)
        self.season = season

        self.start_date = f'{self.season}-03-28'
        self.end_date = f'{self.season}-10-01'
        self.statcast_data = statcast_batter(self.start_date, self.end_date, self.player.player_id)  

        self.setup()

        # Create a 20 by 20 figure
        #self.df = df_processing(df)
        self.fig = plt.figure(figsize=(20, 25))

        # Create a gridspec layout with 8 columns and 6 rows
        # Include border plots for the header, footer, left, and right
        # self.gs = gridspec.GridSpec(7, 8,
        #                 height_ratios=[2,20,9,9,36,36,7],
        #                 width_ratios=[1,18,18,18,18,18,18,1])
        
        self.gs = gridspec.GridSpec(8, 8,
                    height_ratios=[2, 20, 9, 9, 36, 36, 2, 10],  # header, bio, stats, stats, charts, table, spacer, footer
                    width_ratios=[1, 18, 18, 18, 18, 18, 18, 1])

        # Define the positions of each subplot in the grid
        self.ax_headshot = self.fig.add_subplot(self.gs[1,1:3])
        self.ax_bio = self.fig.add_subplot(self.gs[1,3:5])
        self.ax_logo = self.fig.add_subplot(self.gs[1,5:7])
        self.ax_standard_stats = self.fig.add_subplot(self.gs[2,1:7])
        self.ax_advanced_stats = self.fig.add_subplot(self.gs[3,1:7])
        self.ax_chart1 = self.fig.add_subplot(self.gs[4,1:3])
        self.ax_chart2 = self.fig.add_subplot(self.gs[4,3:5])
        self.ax_chart3 = self.fig.add_subplot(self.gs[4,5:7])
        self.ax_pitch_breakdown = self.fig.add_subplot(self.gs[5,1:7])

        self.ax_footer = self.fig.add_subplot(self.gs[-1,1:7])
        self.ax_header = self.fig.add_subplot(self.gs[0,1:7])
        self.ax_left = self.fig.add_subplot(self.gs[:,0])
        self.ax_right = self.fig.add_subplot(self.gs[:,-1])

        # Hide axes for footer, header, left, and right
        self.ax_footer.axis('off')
        self.ax_header.axis('off')
        self.ax_left.axis('off')
        self.ax_right.axis('off')


    def setup(self):
        # Set the theme for seaborn plots
        sns.set_theme(style='whitegrid', 
                    palette='deep', 
                    font='DejaVu Sans', 
                    font_scale=1.5, 
                    color_codes=True, 
                    rc=None)

        # Set the resolution of the figures to 300 DPI
        mpl.rcParams['figure.dpi'] = 50


    def generate_plots(self):
        Plotting.plot_image(self.ax_headshot, self.player.get_headshot())
        Plotting.plot_bio(self.ax_bio, self.player.bio, 'Season Batting Summary', self.season)
        Plotting.plot_image(self.ax_logo, self.team.get_logo())

        batting_stats = BattingStats(player=self.player, season=self.season)
        batting_stats.display_standard_stats(self.ax_standard_stats)
        batting_stats.display_advanced_stats(self.ax_advanced_stats)

        #self.plot_spraychart(self.ax_chart1)
        self.plot_spraychart(self.ax_chart2, statcast_events['batted_ball_events'])
        self.plot_spraychart(self.ax_chart3, statcast_events['hit_events'])

        # Add footer text
        self.ax_footer.text(0, 1, 'Code by: Timothy Fisher', ha='left', va='top', fontsize=24)
        self.ax_footer.text(0.5, 1, 'Color Coding Compares to League Average By Pitch', ha='center', va='top', fontsize=16)
        self.ax_footer.text(1, 1, 'Data: MLB, Fangraphs\nImages: MLB, ESPN', ha='right', va='top', fontsize=24)

        # Adjust the spacing between subplots
        plt.tight_layout()

        plt.savefig(f'batter_summary_{self.player.bio.name.lower().replace(" ", "_")}.png')
        #plt.show()


    def plot_spraychart(self, ax: plt.Axes, events):
        # Assuming `new_ax` is the Axes object returned by your function
        spraychart = BattingSprayChart(self.player.player_id, self.season, events)
        spraychart.plot(ax, self.statcast_data)

        # Replace ax_pitch_break with the new subplot in the same grid position
        # new_ax.set_position(self.gs[5, 5:7].get_position(self.fig))
        # new_ax.set_subplotspec(self.gs[5, 5:7])

        
        
    

