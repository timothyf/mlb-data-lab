import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gridspec

from mlb_summary_sheets.player import Player
from mlb_summary_sheets.team import Team
from mlb_summary_sheets.stats.base_stats import PitchingStats
from mlb_summary_sheets.pitching.pitch_velocity_distribution_plot import PitchVelocityDistributionPlot
from mlb_summary_sheets.pitching.rolling_pitch_usage_plot import RollingPitchUsagePlot
from mlb_summary_sheets.pitching.pitch_break_plot import PitchBreakPlot
from mlb_summary_sheets.pitching.pitch_breakdown_table import PitchBreakdownTable
from mlb_summary_sheets.apis.pybaseball_client import PybaseballClient
from mlb_summary_sheets.constants import swing_code, whiff_code
from mlb_summary_sheets.config import DATA_DIR
from mlb_summary_sheets.summary_sheet import SummarySheet


class PitcherSummarySheet(SummarySheet):

    def __init__(self, player: Player, season: int):
        super().__init__(player, season)

        self.statcast_pitching_data = PybaseballClient.fetch_statcast_pitcher_data(self.player.mlbam_id, self.start_date, self.end_date)

        self.columns_count = 8
        self.rows_count = 9
        self.height_ratios = [2, 20, 9, 9, 0.25, 36, 36, 2, 10]
        self.width_rations = [1, 18, 18, 18, 18, 18, 18, 1]

        self.setup_plots()

        # Define the positions of each subplot in the grid
        self.ax_headshot = self.fig.add_subplot(self.gs[1,1:3])
        self.ax_bio = self.fig.add_subplot(self.gs[1,3:5])
        self.ax_logo = self.fig.add_subplot(self.gs[1,5:7])
        self.ax_standard_stats = self.fig.add_subplot(self.gs[2,1:7])
        self.ax_advanced_stats = self.fig.add_subplot(self.gs[3,1:7])
        self.ax_pitch_velocity = self.fig.add_subplot(self.gs[5,1:3])
        self.ax_pitch_usage = self.fig.add_subplot(self.gs[5,3:5])
        self.ax_pitch_break = self.fig.add_subplot(self.gs[5,5:7])
        self.ax_pitch_breakdown = self.fig.add_subplot(self.gs[6,1:7])

        self.add_header_and_footer_subplots()
        self.hide_axis()


    def generate_plots(self):
        super().generate_plots()

        pitcher_stats = PitchingStats(player=self.player, season=self.season)
        pitcher_stats.display_standard_stats(self.ax_standard_stats)
        pitcher_stats.display_advanced_stats(self.ax_advanced_stats)

        pitching_data = self.prepare_pitching_data(self.statcast_pitching_data)

        self.plot_pitch_velocity_distribution(self.statcast_pitching_data, self.ax_pitch_velocity)
        RollingPitchUsagePlot(self.player).plot(df=self.statcast_pitching_data, ax=self.ax_pitch_usage, window=5)
        PitchBreakPlot(self.player).plot(df=pitching_data, ax=self.ax_pitch_break)
        PitchBreakdownTable(self.player).plot(df=pitching_data, ax=self.ax_pitch_breakdown, fontsize=16)

        # Adjust the spacing between subplots
        plt.tight_layout()

        plt.savefig(f'output/pitcher_summary_{self.player.player_bio.full_name.lower().replace(" ", "_")}.png')
        plt.close()

    
    def plot_pitch_velocity_distribution(self, df: pd.DataFrame, ax: plt.Axes):
        df_statcast_group = pd.read_csv(os.path.join(DATA_DIR, 'statcast_2024_grouped.csv'))
        pvd_plot = PitchVelocityDistributionPlot(self.player)
        pvd_plot.plot(df=df, ax=ax,
                    gs=self.gs,
                    gs_x=[5, 6],
                    gs_y=[1, 3],
                    fig=self.fig,
                    df_statcast_group=df_statcast_group)


    def prepare_pitching_data(self, statcast_pitching_data: pd.DataFrame):
        df = statcast_pitching_data.copy()

        # Create new columns in the DataFrame to indicate swing, whiff, in-zone, out-zone, and chase
        df['swing'] = (df['description'].isin(swing_code))
        df['whiff'] = (df['description'].isin(whiff_code))
        df['in_zone'] = (df['zone'] < 10)
        df['out_zone'] = (df['zone'] > 10)
        df['chase'] = (df.in_zone==False) & (df.swing == 1)

        # Convert the pitch type to a categorical variable
        df['pfx_z'] = df['pfx_z'] * 12
        df['pfx_x'] = df['pfx_x'] * 12
        return df
    
    

