import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from typing import Optional

from mlb_data_lab.data_viz.plotting import Plotting
from mlb_data_lab.config import FOOTER_TEXT
from mlb_data_lab.team.team import Team
from mlb_data_lab.config  import BASE_DIR
from mlb_data_lab.utils import Utils
from mlb_data_lab.apis.unified_data_client import UnifiedDataClient
from mlb_data_lab.apis.local_data_client import LocalDataClient


class PlayerSheet:

    local_data_client = LocalDataClient()

    def __init__(self, data_client: Optional[UnifiedDataClient] = None):

        self.data_client: UnifiedDataClient = data_client if data_client else UnifiedDataClient()

        # Set the resolution of the figures to 300 DPI
        mpl.rcParams['figure.dpi'] = 300

        self.fig = plt.figure(figsize=(20, 25))  

    def setup_plots(self):
        self.gs = gridspec.GridSpec(self.rows_count, self.columns_count,
                    height_ratios=self.height_ratios,  
                    width_ratios=self.width_rations)
        
    def generate_plots(self):
        if hasattr(self, 'player'):
            Plotting.plot_image(self.ax_headshot, self.player.get_headshot())
            if self.player_type == "Pitcher":
                Plotting.plot_bio(self.ax_bio, self.player, 'Season Pitching Summary', self.season)
            else:
                Plotting.plot_bio(self.ax_bio, self.player, 'Season Batting Summary', self.season)
            Plotting.plot_image(self.ax_logo, Team.get_team_logo(self.player.current_team.abbrev))
        elif hasattr(self, 'team'):
            Plotting.plot_team_info(self.ax_bio, self.team, f'Team {self.sheet_type.capitalize()} Summary', self.season)
            Plotting.plot_image(self.ax_logo, self.team.get_logo())

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
        self.ax_footer.axis('off')
        self.ax_header.axis('off')
        self.ax_left.axis('off')
        self.ax_right.axis('off')

    # sheet_type = 'batter' || 'pitcher' || 'team'
    def save_sheet(self, sheet_type):
        if sheet_type == 'team':
            file_path = f'{BASE_DIR}/output/{self.season}/{self.team.club_name}/'
            Utils.ensure_directory_exists(file_path)
            full_path = f'{file_path}team_{self.sheet_type}_summary_{self.team.club_name.lower().replace(" ", "_")}.png'
        else:
            file_path = f'{BASE_DIR}/output/{self.season}/{self.player.current_team.club_name}/'
            Utils.ensure_directory_exists(file_path)
            full_path = f'{file_path}{sheet_type}_summary_{self.player.player_bio.full_name.lower().replace(" ", "_")}.png'
        plt.savefig(full_path) #, bbox_inches='tight')