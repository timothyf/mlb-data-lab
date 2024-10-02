import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from player_bio import PlayerBio
from player import Player
from team import Team
import seaborn as sns
import matplotlib as mpl
import matplotlib.gridspec as gridspec
from pitching.pitching_stats import PitchingStats
from pitching.pitch_velocity_distribution_plot import PitchVelocityDistributionPlot
from pitching.rolling_pitch_usage_plot import RollingPitchUsagePlot
from pitching.pitch_break_plot import PitchBreakPlot
from data_fetcher import DataFetcher
from constants import swing_code, whiff_code
from pitching.pitch_breakdown_table import PitchBreakdownTable


class PitcherSummarySheet:

    def __init__(self, player: Player, season: int):
        self.player = player
        self.team = Team(player.team_id)
        self.season = season

        self.setup()

        self.fig = plt.figure(figsize=(20, 25))

        # Create a gridspec layout with 8 columns and 6 rows
        # Include border plots for the header, footer, left, and right
        self.gs = gridspec.GridSpec(9, 8,
                    height_ratios=[2, 20, 9, 9, 0.25, 36, 36, 2, 10],  
                    width_ratios=[1, 18, 18, 18, 18, 18, 18, 1])

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
        mpl.rcParams['figure.dpi'] = 100


    def generate_plots(self, player: Player):
        self.plot_image(self.ax_headshot, player.get_headshot())
        self.plot_bio(self.ax_bio, player.bio)
        self.plot_image(self.ax_logo, self.team.get_logo())

        pitcher_stats = PitchingStats(pitcher_id=self.player.player_id, season=self.season)
        pitcher_stats.display_standard_stats(self.ax_standard_stats)
        pitcher_stats.display_advanced_stats(self.ax_advanced_stats)

        df_pyb = DataFetcher.fetch_statcast_pitcher_data(self.player.player_id, '2024-03-28', '2024-10-01')
        df = self.df_processing(df_pyb)

        self.plot_pitch_velocity_distribution(df_pyb, self.ax_pitch_velocity)
        self.plot_rolling_pitch_usage(df_pyb, self.ax_pitch_usage)
        self.plot_pitch_break(df, self.ax_pitch_break)

        self.plot_pitch_type_breakdown(df, self.ax_pitch_breakdown)

        # Add footer text
        self.ax_footer.text(0, 1, 'Code by: Timothy Fisher', ha='left', va='top', fontsize=24)
        self.ax_footer.text(0.5, 1, 'Color Coding Compares to League Average By Pitch', ha='center', va='top', fontsize=16)
        self.ax_footer.text(1, 1, 'Data: MLB, Fangraphs\nImages: MLB, ESPN', ha='right', va='top', fontsize=24)

        # Adjust the spacing between subplots
        plt.tight_layout()

        plt.savefig(f'pitcher_summary_{player.bio.name.lower().replace(" ", "_")}.png')
        #plt.show()


    def plot_bio(self, ax: plt.Axes, bio: PlayerBio):        
        ax.text(0.5, 1, f'{bio.name}', va='top', ha='center', fontsize=56)
        ax.text(0.5, 0.65, f'{bio.pitcher_hand}HP, Age:{bio.age}, {bio.height}/{bio.weight}', va='top', ha='center', fontsize=30)
        ax.text(0.5, 0.40, f'Season Pitching Summary', va='top', ha='center', fontsize=40)
        ax.text(0.5, 0.15, f'2024 MLB Season', va='top', ha='center', fontsize=30, fontstyle='italic')  
        ax.axis('off')
    
    def plot_image(self, ax: plt.Axes, img: Image):
        ax.set_xlim(0, 1.3)
        ax.set_ylim(0, 1)
        ax.imshow(img, extent=[0, 1, 0, 1], origin='upper')
        ax.axis('off')

    
    def plot_pitch_velocity_distribution(self, df: pd.DataFrame, ax: plt.Axes):
        df_statcast_group = pd.read_csv('statcast_2024_grouped.csv')
        pvd_plot = PitchVelocityDistributionPlot(self.player)
        pvd_plot.plot(df=df, ax=ax,
                    gs=self.gs,
                    gs_x=[5, 6],
                    gs_y=[1, 3],
                    fig=self.fig,
                    df_statcast_group=df_statcast_group)


    def plot_rolling_pitch_usage(self, df: pd.DataFrame, ax: plt.Axes):
        pu_plot = RollingPitchUsagePlot(self.player)
        pu_plot.plot(df=df, ax=ax, window=5)


    def plot_pitch_break(self, df: pd.DataFrame, ax: plt.Axes):
        pb_plot = PitchBreakPlot(self.player)
        pb_plot.plot(df=df, ax=ax)

    
    def plot_pitch_type_breakdown(self, df: pd.DataFrame, ax: plt.Axes):
        pbd_plot = PitchBreakdownTable(self.player)
        pbd_plot.plot(df=df, ax=ax, fontsize=16)
        pass


    def df_processing(self, df_pyb: pd.DataFrame):
        df = df_pyb.copy()

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
    
    

