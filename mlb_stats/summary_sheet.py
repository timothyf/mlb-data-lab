import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from mlb_stats.plotting import Plotting
from mlb_stats.config import FOOTER_TEXT
from mlb_stats.apis.mlb_stats_client import MlbStatsClient
from mlb_stats.team import Team


class SummarySheet:
    def __init__(self, player, season=2024):
        self.player = player
        self.season = season
        team_info = MlbStatsClient.fetch_player_team(player.mlbam_id, season)
        self.team_abbrev = team_info.get('abbreviation')
        self.club_name = team_info.get('clubName')

        season_info = MlbStatsClient.get_season_info(season)

        self.start_date = season_info['regularSeasonStartDate']
        self.end_date = season_info['regularSeasonEndDate']

        # Set the resolution of the figures to 300 DPI
        mpl.rcParams['figure.dpi'] = 300

        self.fig = plt.figure(figsize=(20, 25))

        if self.__class__.__name__ == "PitcherSummarySheet":
            self.player_type = "Pitcher"
        elif self.__class__.__name__ == "BatterSummarySheet":
            self.player_type = "Batter"

    def setup_plots(self):
        self.gs = gridspec.GridSpec(self.rows_count, self.columns_count,
                    height_ratios=self.height_ratios,  
                    width_ratios=self.width_rations)
        
    def generate_plots(self):
        Plotting.plot_image(self.ax_headshot, self.player.get_headshot())
        if self.player_type == "Pitcher":
            Plotting.plot_bio(self.ax_bio, self.player, 'Season Pitching Summary', self.season)
        else:
            Plotting.plot_bio(self.ax_bio, self.player, 'Season Batting Summary', self.season)

        Plotting.plot_image(self.ax_logo, Team.get_team_logo(self.team_abbrev))

        # Add footer text
        self.ax_footer.text(0, 1, FOOTER_TEXT[1]['text'], ha='left', va='top', fontsize=FOOTER_TEXT[1]['fontsize'])
        self.ax_footer.text(0.5, 1, FOOTER_TEXT[2]['text'], ha='center', va='top', fontsize=FOOTER_TEXT[2]['fontsize'])
        self.ax_footer.text(1, 1, FOOTER_TEXT[3]['text'], ha='right', va='top', fontsize=FOOTER_TEXT[3]['fontsize'])

    def add_header_and_footer_subplots(self):
        self.ax_footer = self.fig.add_subplot(self.gs[-1,1:7])
        self.ax_header = self.fig.add_subplot(self.gs[0,1:7])
        self.ax_left = self.fig.add_subplot(self.gs[:,0])
        self.ax_right = self.fig.add_subplot(self.gs[:,-1])

    def hide_axis(self):
        # Hide axes for footer, header, left, and right
        self.ax_footer.axis('off')
        self.ax_header.axis('off')
        self.ax_left.axis('off')
        self.ax_right.axis('off')

