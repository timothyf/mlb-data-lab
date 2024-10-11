import matplotlib.pyplot as plt

from mlb_summary_sheets.player import Player
from mlb_summary_sheets.stats.stats_display import StatsDisplay
from mlb_summary_sheets.batting.batting_spray_chart import BattingSprayChart
from mlb_summary_sheets.constants import statcast_events
from mlb_summary_sheets.summary_sheet import SummarySheet
from mlb_summary_sheets.apis.pybaseball_client import PybaseballClient



class BatterSummarySheet(SummarySheet):

    def __init__(self, player: Player, season: int):
        super().__init__(player, season)

        self.statcast_data = PybaseballClient.fetch_statcast_batter_data(player.mlbam_id, self.start_date, self.end_date)

        self.columns_count = 8
        self.rows_count = 8
        self.height_ratios = [2, 20, 5, 5, 16, 46, 1, 8]
        self.width_rations = [1, 18, 18, 18, 18, 18, 18, 1]

        self.setup_plots()

        # Define the positions of each subplot in the grid
        self.ax_headshot = self.fig.add_subplot(self.gs[1,1:3])
        self.ax_bio = self.fig.add_subplot(self.gs[1,3:5])
        self.ax_logo = self.fig.add_subplot(self.gs[1,5:7])
        self.ax_standard_stats = self.fig.add_subplot(self.gs[2,1:7])
        self.ax_advanced_stats = self.fig.add_subplot(self.gs[3,1:7])
        self.ax_splits_stats = self.fig.add_subplot(self.gs[4,1:7])
        self.ax_chart1 = self.fig.add_subplot(self.gs[5,1:4])
        self.ax_chart2 = self.fig.add_subplot(self.gs[5,4:7])

        self.add_header_and_footer_subplots()
        self.hide_axis()


    def generate_plots(self):
        super().generate_plots()

        stats_display = StatsDisplay(player=self.player, season=self.season, stat_type='batting')
        stats_display.display_standard_stats(self.ax_standard_stats)
        stats_display.display_advanced_stats(self.ax_advanced_stats)
        stats_display.display_splits_stats(self.ax_splits_stats)

        BattingSprayChart(self.player.mlbam_id, statcast_events['batted_ball_events']).plot(self.ax_chart1, self.statcast_data, "Batted Balls")
        BattingSprayChart(self.player.mlbam_id, statcast_events['hit_events']).plot(self.ax_chart2, self.statcast_data, "Hits")

        plt.tight_layout()
        plt.savefig(f'output/batter_summary_{self.player.player_bio.full_name.lower().replace(" ", "_")}.png')
        plt.close()

