import matplotlib.pyplot as plt

from mlb_data_lab.player.player import Player
from mlb_data_lab.stats.stats_display import StatsDisplay
from mlb_data_lab.data_viz.batting_spray_chart import BattingSprayChart
from mlb_data_lab.constants import statcast_events
from mlb_data_lab.summary_sheets.summary_sheet import SummarySheet
from mlb_data_lab.apis.pybaseball_client import PybaseballClient
from mlb_data_lab.team.team import Team


class TeamBattingSheet(SummarySheet):

    def __init__(self, team: Team, season: int):
        super().__init__(season)

        self.team = team

        #self.statcast_data = PybaseballClient.fetch_statcast_batter_data(player.mlbam_id, self.start_date, self.end_date)

        self.columns_count = 8
        self.rows_count = 8
        self.height_ratios = [2, 20, 5, 5, 16, 46, 1, 8]
        self.width_rations = [1, 18, 18, 18, 18, 18, 18, 1]

        self.setup_plots()

        # Define the positions of each subplot in the grid
        self.ax_logo = self.fig.add_subplot(self.gs[1,1:3])
        self.ax_bio = self.fig.add_subplot(self.gs[1,3:5])
        self.ax_standard_stats = self.fig.add_subplot(self.gs[2,1:7])
        self.ax_advanced_stats = self.fig.add_subplot(self.gs[3,1:7])

        self.add_header_and_footer_subplots()
        self.hide_axis()


    def generate_plots(self):
        super().generate_plots()

        # stats_display = StatsDisplay(player=self.player, season=self.season, stat_type='batting')
        # stats_display.display_standard_stats(self.ax_standard_stats)
        # stats_display.display_advanced_stats(self.ax_advanced_stats)
        # stats_display.display_splits_stats(self.ax_splits_stats)

        # spray_chart = BattingSprayChart(self.player.mlbam_id, statcast_events['batted_ball_events'])
        # if spray_chart.check_for_valid_data(self.statcast_data):
        #     spray_chart.plot(self.ax_chart1, self.statcast_data, "Batted Balls")
        # else:
        #     print("No valid data available for plotting batted ball events.")
        #     self.ax_chart1.remove()  # Remove the subplot if no valid data is found


        # spray_chart = BattingSprayChart(self.player.mlbam_id, statcast_events['hit_events'])
        # if spray_chart.check_for_valid_data(self.statcast_data):
        #     spray_chart.plot(self.ax_chart2, self.statcast_data, "Hits")
        # else:
        #     print("No valid data available for plotting hit events.")
        #     self.ax_chart2.remove()  # Remove the subplot if no valid data is found

        plt.tight_layout()
        self.save_sheet("team")
        plt.close()