import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gridspec

from pybaseball import statcast_batter

from mlb_summary_sheets.player import Player
from mlb_summary_sheets.team import Team
from mlb_summary_sheets.stats.stats_display import BattingStats
from mlb_summary_sheets.batting.batting_spray_chart import BattingSprayChart
from mlb_summary_sheets.constants import statcast_events
from mlb_summary_sheets.plotting import Plotting


class TeamBattingSheet:

    def __init__(self, team: Team, season: int):
        self.team = Team
        self.season = season

        self.start_date = f'{self.season}-03-28'
        self.end_date = f'{self.season}-10-01'
        self.statcast_data = statcast_batter(self.start_date, self.end_date, self.player.mlbam_id)  

        # Set the resolution of the figures to 300 DPI
        mpl.rcParams['figure.dpi'] = 300

        self.fig = plt.figure(figsize=(20, 25))

        # Create a gridspec layout with 8 columns and 6 rows
        self.gs = gridspec.GridSpec(8, 8,
                    height_ratios=[2, 20, 5, 5, 16, 46, 1, 8],
                    width_ratios=[1, 18, 18, 18, 18, 18, 18, 1])

        # Define the positions of each subplot in the grid
        self.ax_headshot = self.fig.add_subplot(self.gs[1,1:3])
        self.ax_bio = self.fig.add_subplot(self.gs[1,3:5])
        self.ax_logo = self.fig.add_subplot(self.gs[1,5:7])
        self.ax_standard_stats = self.fig.add_subplot(self.gs[2,1:7])
        self.ax_advanced_stats = self.fig.add_subplot(self.gs[3,1:7])
        self.ax_splits_stats = self.fig.add_subplot(self.gs[4,1:7])
        self.ax_chart1 = self.fig.add_subplot(self.gs[5,1:4])
        self.ax_chart2 = self.fig.add_subplot(self.gs[5,4:7])

        self.ax_footer = self.fig.add_subplot(self.gs[-1,1:7])
        self.ax_header = self.fig.add_subplot(self.gs[0,1:7])
        self.ax_left = self.fig.add_subplot(self.gs[:,0])
        self.ax_right = self.fig.add_subplot(self.gs[:,-1])

        # Hide axes for footer, header, left, and right
        self.ax_footer.axis('off')
        self.ax_header.axis('off')
        self.ax_left.axis('off')
        self.ax_right.axis('off')
        

    def generate_plots(self):
        Plotting.plot_image(self.ax_headshot, self.player.get_headshot())
        Plotting.plot_bio(self.ax_bio, self.player, 'Season Batting Summary', self.season)
        Plotting.plot_image(self.ax_logo, self.player.team.get_logo())

        batting_stats = BattingStats(player=self.player, season=self.season)
        batting_stats.display_standard_stats(self.ax_standard_stats)
        batting_stats.display_advanced_stats(self.ax_advanced_stats)
        batting_stats.display_splits_stats(self.ax_splits_stats)

        BattingSprayChart(self.player.mlbam_id, statcast_events['batted_ball_events']).plot(self.ax_chart1, self.statcast_data, "Batted Balls")
        BattingSprayChart(self.player.mlbam_id, statcast_events['hit_events']).plot(self.ax_chart2, self.statcast_data, "Hits")

        # Add footer text
        self.ax_footer.text(0, 1, 'Code by: Timothy Fisher', ha='left', va='top', fontsize=24)
        self.ax_footer.text(0.5, 1, 'Color Coding Compares to League Average By Pitch', ha='center', va='top', fontsize=16)
        self.ax_footer.text(1, 1, 'Data: MLB, Fangraphs\nImages: MLB, ESPN', ha='right', va='top', fontsize=24)

        plt.tight_layout()
        plt.savefig(f'output/batter_summary_{self.player.player_bio.full_name.lower().replace(" ", "_")}.png')
        plt.close()

