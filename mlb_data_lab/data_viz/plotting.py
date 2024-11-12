from PIL import Image
import matplotlib.pyplot as plt
from mlb_data_lab.player.player import Player
from mlb_data_lab.team.team import Team


class Plotting:

    @staticmethod
    def plot_image(ax: plt.Axes, img: Image, origin='upper'):
        ax.set_xlim(0, 1.3)
        ax.set_ylim(0, 1)
        if img is not None:
         ax.imshow(img, extent=[0, 1, 0, 1], origin='upper')
        ax.axis('off')

    @staticmethod
    def plot_bio(ax: plt.Axes, player: Player, title: str, season: int):        
        ax.text(0.5, 1, f'{player.player_bio.full_name}', va='top', ha='center', fontsize=56)
        ax.text(0.5, 0.65, f'{player.player_info.primary_position}, Age:{player.player_bio.current_age}, {player.player_bio.height}/{player.player_bio.weight}', va='top', ha='center', fontsize=30)
        ax.text(0.5, 0.40, f'{title}', va='top', ha='center', fontsize=40)
        ax.text(0.5, 0.15, f'{season} MLB Season', va='top', ha='center', fontsize=30, fontstyle='italic')  
        ax.axis('off')

    @staticmethod
    def plot_team_info(ax: plt.Axes, team: Team, title: str, season: int):
        team.populate_season_stats(season)
        stats = team.season_stats
        ax.text(0.5, 1, f'{team.name}', va='top', ha='center', fontsize=56)
        ax.text(0.5, 0.70, f'{title}', va='top', ha='center', fontsize=40)
        ax.text(0.5, 0.50, f'{season} MLB Season', va='top', ha='center', fontsize=40)
        ax.text(0.5, 0.28, f'{stats.wins} - {stats.losses}  PCT {stats.win_pct}', va='top', ha='center', fontsize=30)
        ax.text(0.5, 0.10, f'RS {stats.runs_scored}  RA {stats.runs_allowed}  DIFF {stats.run_diff}', va='top', ha='center', fontsize=30)

        ax.axis('off')


    
    
