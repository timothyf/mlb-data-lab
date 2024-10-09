from dataclasses import dataclass, field
from typing import Dict, List
import os

# Set BASE_DIR to the project root (mlb_stats directory)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Now you can correctly build paths relative to the project root
DATA_DIR = os.path.join(BASE_DIR, 'mlb_summary_sheets', 'data')



@dataclass
class FontConfig:
    default_family: str = 'DejaVu Sans'
    default_size: int = 12
    title_size: int = 20
    axes_size: int = 16
    
    font_properties: dict = field(init=False)
    
    def __post_init__(self):
        # Setup the font properties for easy access
        self.font_properties = {
            'default': {'family': self.default_family, 'size': self.default_size},
            'titles': {'family': self.default_family, 'size': self.title_size, 'fontweight': 'bold'},
            'axes': {'family': self.default_family, 'size': self.axes_size},
        }

@dataclass
class StatsConfig:

    stat_lists = {
        'batting': {
            'standard': ['G', 'PA', 'AB', 'H', '1B', '2B', '3B', 'HR', 'R', 'RBI', 'BB', 'IBB', 'SO', 'HBP', 'SF', 'SH', 'GDP', 'SB', 'CS', 'AVG'],
            'advanced': ['BB%', 'K%', 'BB/K', 'AVG', 'OBP', 'SLG', 'OPS', 'ISO', 'Spd', 'BABIP', 'UBR', 'XBR', 'wRC', 'wRAA', 'wOBA', 'wRC+', 'WAR'],
            'splits': ['G', 'PA', 'AB', 'R', 'H', '1B', '2B', '3B', 'HR', 'RBI', 'BB', 'IBB', 'SO', 'AVG', 'OBP', 
                       'SLG', 'OPS', 'BAbip', 'tOPS+', 'sOPS+']
        },
        'pitching': {
            'standard': ['W', 'L', 'ERA', 'G', 'GS', 'QS', 'CG', 'ShO', 'SV', 'HLD', 'BS', 'IP', 'TBF', 'H', 'R', 'ER', 'HR', 'BB', 'IBB', 'HBP', 'WP', 'BK', 'SO'],
            'advanced': ['K/9', 'BB/9', 'K/BB', 'H/9', 'HR/9', 'K%', 'BB%', 'K-BB%', 'AVG', 'WHIP', 'BABIP', 'LOB%', 'ERA-', 'FIP-','FIP', 'RS/9', 'Swing%'],
            'splits': []
        },
    }



@dataclass
class StatsDisplayConfig:

    pitching = {
        'W': {'table_header': r'$\bf{W}$', 'format': '.0f'},
        'L': {'table_header': r'$\bf{L}$', 'format': '.0f'},
        'SV': {'table_header': r'$\bf{SV}$', 'format': '.0f'},
        'IP': {'table_header': r'$\bf{IP}$', 'format': '.1f'},
        'TBF': {'table_header': r'$\bf{TBF}$', 'format': '.0f'},
        'AVG': {'table_header': r'$\bf{AVG}$', 'format': '.3f'},
        'K/9': {'table_header': r'$\bf{K\ /\;9}$', 'format': '.2f'},
        'BB/9': {'table_header': r'$\bf{BB\ /\;9}$', 'format': '.2f'},
        'K/BB': {'table_header': r'$\bf{K\ /\;BB}$', 'format': '.2f'},
        'HR/9': {'table_header': r'$\bf{HR\ /\;9}$', 'format': '.2f'},
        'K%': {'table_header': r'$\bf{K\%}$', 'format': 'percent'},
        'BB%': {'table_header': r'$\bf{BB\%}$', 'format': 'percent'},
        'K-BB%': {'table_header': r'$\bf{K-BB\%}$', 'format': 'percent'},
        'WHIP': {'table_header': r'$\bf{WHIP}$', 'format': '.2f'},
        'BABIP': {'table_header': r'$\bf{BABIP}$', 'format': '.3f'},
        'LOB%': {'table_header': r'$\bf{LOB\%}$', 'format': 'percent'},
        'xFIP': {'table_header': r'$\bf{xFIP}$', 'format': '.2f'},
        'FIP': {'table_header': r'$\bf{FIP}$', 'format': '.2f'},
        'H': {'table_header': r'$\bf{H}$', 'format': '.0f'},
        '2B': {'table_header': r'$\bf{2B}$', 'format': '.0f'},
        '3B': {'table_header': r'$\bf{3B}$', 'format': '.0f'},
        'R': {'table_header': r'$\bf{R}$', 'format': '.0f'},
        'ER': {'table_header': r'$\bf{ER}$', 'format': '.0f'},
        'HR': {'table_header': r'$\bf{HR}$', 'format': '.0f'},
        'BB': {'table_header': r'$\bf{BB}$', 'format': '.0f'},
        'IBB': {'table_header': r'$\bf{IBB}$', 'format': '.0f'},
        'HBP': {'table_header': r'$\bf{HBP}$', 'format': '.0f'},
        'SO': {'table_header': r'$\bf{SO}$', 'format': '.0f'},
        'OBP': {'table_header': r'$\bf{OBP}$', 'format': '.3f'},
        'SLG': {'table_header': r'$\bf{SLG}$', 'format': '.3f'},
        'ERA': {'table_header': r'$\bf{ERA}$', 'format': '.2f'},
        'wOBA': {'table_header': r'$\bf{wOBA}$', 'format': '.3f'},
        'G': {'table_header': r'$\bf{G}$', 'format': '.0f'},
        'GS': {'table_header': r'$\bf{GS}$', 'format': '.0f'},
        'CG': {'table_header': r'$\bf{CG}$', 'format': '.0f'},
        'SHO': {'table_header': r'$\bf{SHO}$', 'format': '.0f'},
        'QS': {'table_header': r'$\bf{QS}$', 'format': '.0f'},
        'WP': {'table_header': r'$\bf{WP}$', 'format': '.0f'},
        'BK': {'table_header': r'$\bf{BK}$', 'format': '.0f'},
        'RS/9': {'table_header': r'$\bf{RS\ /\;9}$', 'format': '.2f'},
        'H/9': {'table_header': r'$\bf{H\ /\;9}$', 'format': '.2f'},
        'Swing%': {'table_header': r'$\bf{Swing\%}$', 'format': 'percent'},
        'ShO': {'table_header': r'$\bf{ShO}$', 'format': '.0f'},
        'HLD': {'table_header': r'$\bf{HLD}$', 'format': '.0f'},
        'BS': {'table_header': r'$\bf{BS}$', 'format': '.0f'},
        'ERA-': {'table_header': r'$\bf{ERA-}$', 'format': '.0f'},
        'FIP-': {'table_header': r'$\bf{FIP-}$', 'format': '.0f'},
    }

    batting = {
        'G': {'table_header': r'$\bf{G}$', 'format': '.0f'},
        'GS': {'table_header': r'$\bf{GS}$', 'format': '.0f'}, 
        'PA': {'table_header': r'$\bf{PA}$', 'format': '.0f'},
        'AB': {'table_header': r'$\bf{AB}$', 'format': '.0f'},
        'H': {'table_header': r'$\bf{H}$', 'format': '.0f'},
        '1B': {'table_header': r'$\bf{1B}$', 'format': '.0f'},
        '2B': {'table_header': r'$\bf{2B}$', 'format': '.0f'},
        '3B': {'table_header': r'$\bf{3B}$', 'format': '.0f'},
        'HR': {'table_header': r'$\bf{HR}$', 'format': '.0f'},
        'R': {'table_header': r'$\bf{R}$', 'format': '.0f'},
        'RBI': {'table_header': r'$\bf{RBI}$', 'format': '.0f'},
        'BB': {'table_header': r'$\bf{BB}$', 'format': '.0f'},
        'IBB': {'table_header': r'$\bf{IBB}$', 'format': '.0f'},
        'SO': {'table_header': r'$\bf{SO}$', 'format': '.0f'},
        'HBP': {'table_header': r'$\bf{HBP}$', 'format': '.0f'},
        'SF': {'table_header': r'$\bf{SF}$', 'format': '.0f'},
        'SH': {'table_header': r'$\bf{SH}$', 'format': '.0f'},
        'GDP': {'table_header': r'$\bf{GDP}$', 'format': '.0f'},
        'SB': {'table_header': r'$\bf{SB}$', 'format': '.0f'},
        'CS': {'table_header': r'$\bf{CS}$', 'format': '.0f'},
        'AVG': {'table_header': r'$\bf{AVG}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'OBP': {'table_header': r'$\bf{OBP}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'SLG': {'table_header': r'$\bf{SLG}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'OPS': {'table_header': r'$\bf{OPS}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'wOBA': {'table_header': r'$\bf{wOBA}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'wRC+': {'table_header': r'$\bf{wRC+}$', 'format': '.0f'},
        'WAR': {'table_header': r'$\bf{WAR}$', 'format': '.1f'},
        'BB%': {'table_header': r'$\bf{BB\%}$', 'format': 'percent'},
        'K%': {'table_header': r'$\bf{K\%}$', 'format': 'percent'},
        'BB/K': {'table_header': r'$\bf{BB/K}$', 'format': '.2f'},
        'ISO': {'table_header': r'$\bf{ISO}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'Spd': {'table_header': r'$\bf{Spd}$', 'format': '.1f'},
        'BABIP': {'table_header': r'$\bf{BABIP}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'UBR': {'table_header': r'$\bf{UBR}$', 'format': '.1f'},
        'wRC': {'table_header': r'$\bf{wRC}$', 'format': '.0f'},
        'XBR': {'table_header': r'$\bf{XBR}$', 'format': '.1f'},
        'wRAA': {'table_header': r'$\bf{wRAA}$', 'format': '.1f'},
        'BA': {'table_header': r'$\bf{BA}$', 'format': '.3f'},
        'TB': {'table_header': r'$\bf{TB}$', 'format': '.0f'},
        'ROE': {'table_header': r'$\bf{ROE}$', 'format': '.0f'},
        'BAbip': {'table_header': r'$\bf{BAbip}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'tOPS+': {'table_header': r'$\bf{tOPS+}$', 'format': '.0f'},
        'sOPS+': {'table_header': r'$\bf{sOPS+}$', 'format': '.0f'},
    }



