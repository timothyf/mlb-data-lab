from dataclasses import dataclass, field
from typing import Dict, List
import os

# Set BASE_DIR to the project root (mlb_stats directory)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Now you can correctly build paths relative to the project root
DATA_DIR = os.path.join(BASE_DIR, 'mlb_data_lab', 'data')

# Statcast Data output directory
STATCAST_DATA_DIR = os.path.join(BASE_DIR, 'output')

# Player sheets output directory
PLAYER_SHEETS_DIR = os.path.join(BASE_DIR, 'output')

FOOTER_TEXT = {
    1: {
        'text': 'Code by: Timothy Fisher',
        'fontsize': 24 },
    2: {
        'text': 'Color Coding Compares to League Average By Pitch',
        'fontsize': 16 },
    3: {
        'text': 'Data: MLB, Fangraphs\nImages: MLB, ESPN',
        'fontsize': 24 }
}


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
            'standard': ['G', 'PA', 'AB', 'H', '2B', '3B', 'HR', 'R', 'RBI', 'BB', 'IBB', 'SO', 'HBP', 'SF', 'SH', 'GDP', 'SB', 'CS', 'AVG'],
            #'standard': ['G', 'PA', 'AB', 'H', '1B', '2B', '3B', 'HR', 'R', 'RBI', 'BB', 'IBB', 'SO', 'HBP', 'SF', 'SH', 'GDP', 'SB', 'CS', 'AVG'],
            'advanced': ['BB%', 'K%', 'AVG', 'OBP', 'SLG', 'OPS', 'ISO', 'Spd', 'BABIP', 'UBR', 'wRC', 'wRAA', 'wOBA', 'wRC+', 'WAR'],
            'splits': ["gamesPlayed", "groundOuts", "airOuts", "doubles", "triples", "homeRuns", "strikeOuts", 
                       "baseOnBalls", "intentionalWalks", "hits", "hitByPitch", "avg", "atBats", "obp", "slg", "ops", 
                       "groundIntoDoublePlay", "groundIntoTriplePlay", "numberOfPitches", "plateAppearances", 
                       "totalBases", "rbi", "leftOnBase", "sacBunts", "sacFlies", "babip", "groundOutsToAirouts", 
                       "catchersInterference", "atBatsPerHomeRun"]
        },
        'pitching': {
            'standard': ['W', 'L', 'ERA', 'G', 'GS', 'CG', 'ShO', 'SV', 'HLD', 'BS', 'IP', 'TBF', 'H', 'R', 'ER', 'HR', 'BB', 'IBB', 'HBP', 'WP', 'BK', 'SO'],
            'advanced': ['K/9', 'BB/9', 'K/BB', 'H/9', 'HR/9', 'K%', 'BB%', 'K-BB%', 'AVG', 'WHIP', 'BABIP', 'LOB%', 'ERA-', 'FIP-','FIP', 'RS/9', 'Swing%'],
            'splits': ['PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'BB', 'SO', 'BA', 'OBP', 'SLG', 'OPS', 'TB', 'GDP', 
                       'HBP', 'SH', 'SF', 'IBB', 'ROE', 'BAbip', 'tOPS+', 'sOPS+']
        },
    }


@dataclass
class StatsDisplayConfig:

    pitching = {
        'W': {'table_header': r'$\bf{W}$', 'format': ''},
        'L': {'table_header': r'$\bf{L}$', 'format': ''},
        'SV': {'table_header': r'$\bf{SV}$', 'format': ''},
        'IP': {'table_header': r'$\bf{IP}$', 'format': ''},
        'SO': {'table_header': r'$\bf{SO}$', 'format': ''},
        'TBF': {'table_header': r'$\bf{TBF}$', 'format': ''},
        'AVG': {'table_header': r'$\bf{AVG}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'K/9': {'table_header': r'$\bf{K\ /\;9}$', 'format': '.2f'},
        'BB/9': {'table_header': r'$\bf{BB\ /\;9}$', 'format': '.2f'},
        'K/BB': {'table_header': r'$\bf{K\ /\;BB}$', 'format': '.2f'},
        'HR/9': {'table_header': r'$\bf{HR\ /\;9}$', 'format': '.2f'},
        'K%': {'table_header': r'$\bf{K\%}$', 'format': 'percent'},
        'BB%': {'table_header': r'$\bf{BB\%}$', 'format': 'percent'},
        'K-BB%': {'table_header': r'$\bf{K-BB\%}$', 'format': 'percent'},
        'WHIP': {'table_header': r'$\bf{WHIP}$', 'format': '.2f'},
        'BABIP': {'table_header': r'$\bf{BABIP}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'LOB%': {'table_header': r'$\bf{LOB\%}$', 'format': 'percent'},
        'xFIP': {'table_header': r'$\bf{xFIP}$', 'format': '.2f'},
        'FIP': {'table_header': r'$\bf{FIP}$', 'format': '.2f'},
        'hits': {'table_header': r'$\bf{H}$', 'format': ''},
        'H': {'table_header': r'$\bf{H}$', 'format': ''},
        '2B': {'table_header': r'$\bf{2B}$', 'format': '.0f'},
        '3B': {'table_header': r'$\bf{3B}$', 'format': '.0f'},
        'runs': {'table_header': r'$\bf{R}$', 'format': ''},
        'R': {'table_header': r'$\bf{R}$', 'format': ''},
        'ER': {'table_header': r'$\bf{ER}$', 'format': ''},
        'homeRuns': {'table_header': r'$\bf{HR}$', 'format': ''},
        'HR': {'table_header': r'$\bf{HR}$', 'format': ''},
        'BB': {'table_header': r'$\bf{BB}$', 'format': '.0f'},
        'baseOnBalls' : {'table_header': r'$\bf{BB}$', 'format': ''},
        'IBB': {'table_header': r'$\bf{IBB}$', 'format': '.0f'},
        'HBP': {'table_header': r'$\bf{HBP}$', 'format': '.0f'},
        'SO': {'table_header': r'$\bf{SO}$', 'format': '.0f'},
        'OBP': {'table_header': r'$\bf{OBP}$', 'format': '.3f'},
        'obp': {'table_header': r'$\bf{OBP}$', 'format': ''},
        'SLG': {'table_header': r'$\bf{SLG}$', 'format': '.3f'},
        'slg': {'table_header': r'$\bf{SLG}$', 'format': ''},
        'ERA': {'table_header': r'$\bf{ERA}$', 'format': ''},
        'wOBA': {'table_header': r'$\bf{wOBA}$', 'format': '.3f'},
        'G': {'table_header': r'$\bf{G}$', 'format': ''},
        'GS': {'table_header': r'$\bf{GS}$', 'format': ''},
        'CG': {'table_header': r'$\bf{CG}$', 'format': ''},
        'ShO': {'table_header': r'$\bf{SHO}$', 'format': ''},
        'qualityStarts': {'table_header': r'$\bf{QS}$', 'format': ''},
        'WP': {'table_header': r'$\bf{WP}$', 'format': ''},
        'BK': {'table_header': r'$\bf{BK}$', 'format': ''},
        'RS/9': {'table_header': r'$\bf{RS\ /\;9}$', 'format': '.2f'},
        'H/9': {'table_header': r'$\bf{H\ /\;9}$', 'format': '.2f'},
        'Swing%': {'table_header': r'$\bf{Swing\%}$', 'format': 'percent'},
        'HLD': {'table_header': r'$\bf{HLD}$', 'format': ''},
        'BS': {'table_header': r'$\bf{BS}$', 'format': ''},
        'ERA-': {'table_header': r'$\bf{ERA-}$', 'format': '.0f'},
        'FIP-': {'table_header': r'$\bf{FIP-}$', 'format': '.0f'},
        'PA': {'table_header': r'$\bf{PA}$', 'format': '.0f'},
        'AB': {'table_header': r'$\bf{AB}$', 'format': '.0f'},
        'BA': {'table_header': r'$\bf{BA}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'OBP': {'table_header': r'$\bf{OBP}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'SLG': {'table_header': r'$\bf{SLG}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'OPS': {'table_header': r'$\bf{OPS}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'ops': {'table_header': r'$\bf{OPS}$'},
        'TB': {'table_header': r'$\bf{TB}$', 'format': '.0f'},
        'GDP': {'table_header': r'$\bf{GDP}$', 'format': '.0f'},
        'HBP': {'table_header': r'$\bf{HBP}$', 'format': '.0f'},
        'hitBatsmen': {'table_header': r'$\bf{HBP}$', 'format': ''},
        'SH': {'table_header': r'$\bf{SH}$', 'format': '.0f'},
        'SF': {'table_header': r'$\bf{SF}$', 'format': '.0f'},
        'IBB': {'table_header': r'$\bf{IBB}$', 'format': '.0f'},
        'intentionalWalks': {'table_header': r'$\bf{IBB}$', 'format': ''},
        'ROE': {'table_header': r'$\bf{ROE}$', 'format': '.0f'},
        'BAbip': {'table_header': r'$\bf{BAbip}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'babip': {'table_header': r'$\bf{BABIP}$'},
        'tOPS+': {'table_header': r'$\bf{tOPS+}$', 'format': '.0f'},
        'sOPS+': {'table_header': r'$\bf{sOPS+}$', 'format': '.0f'},
        'groundOuts': {'table_header': r'$\bf{GO}$', 'format': '.0f'},
        'airOuts': {'table_header': r'$\bf{AO}$', 'format': '.0f'},
        'groundIntoTriplePlay': {'table_header': r'$\bf{GITP}$', 'format': '.0f'},
        'numberOfPitches': {'table_header': r'$\bf{P}$', 'format': '.0f'}
    }

    batting = {
        'gamesPlayed': {'table_header': r'$\bf{G}$'},
        'G': {'table_header': r'$\bf{G}$'},
        'GS': {'table_header': r'$\bf{GS}$', 'format': '.0f'}, 
        'PA': {'table_header': r'$\bf{PA}$', 'format': '.0f'},
        'plateAppearances': {'table_header': r'$\bf{PA}$'},
        'AB': {'table_header': r'$\bf{AB}$', 'format': '.0f'},
        'atBats': {'table_header': r'$\bf{AB}$'},
        'H': {'table_header': r'$\bf{H}$', 'format': '.0f'},
        'hits': {'table_header': r'$\bf{H}$'},
        '1B': {'table_header': r'$\bf{1B}$', 'format': '.0f'},
        '2B': {'table_header': r'$\bf{2B}$', 'format': '.0f'},
        'doubles': {'table_header': r'$\bf{2B}$'},
        '3B': {'table_header': r'$\bf{3B}$', 'format': '.0f'},
        'triples': {'table_header': r'$\bf{3B}$'},
        'HR': {'table_header': r'$\bf{HR}$', 'format': '.0f'},
        'homeRuns': {'table_header': r'$\bf{HR}$'},
        'R': {'table_header': r'$\bf{R}$', 'format': '.0f'},
        'runs': {'table_header': r'$\bf{R}$'},
        'RBI': {'table_header': r'$\bf{RBI}$', 'format': '.0f'},
        'rbi': {'table_header': r'$\bf{RBI}$'},
        'BB': {'table_header': r'$\bf{BB}$', 'format': '.0f'},
        'baseOnBalls': {'table_header': r'$\bf{BB}$'},
        'IBB': {'table_header': r'$\bf{IBB}$', 'format': '.0f'},
        'intentionalWalks': {'table_header': r'$\bf{IBB}$'},
        'SO': {'table_header': r'$\bf{SO}$', 'format': '.0f'},
        'strikeOuts': {'table_header': r'$\bf{SO}$'},
        'HBP': {'table_header': r'$\bf{HBP}$', 'format': '.0f'},
        'hitByPitch': {'table_header': r'$\bf{HBP}$'},
        'SF': {'table_header': r'$\bf{SF}$', 'format': '.0f'},
        'sacFlies': {'table_header': r'$\bf{SF}$'},
        'SH': {'table_header': r'$\bf{SH}$', 'format': '.0f'},
        'sacBunts': {'table_header': r'$\bf{SH}$'},
        'GDP': {'table_header': r'$\bf{GDP}$', 'format': '.0f'},
        'groundIntoDoublePlay': {'table_header': r'$\bf{GDP}$'},
        'SB': {'table_header': r'$\bf{SB}$', 'format': '.0f'},
        'stolenBases': {'table_header': r'$\bf{SB}$'},
        'CS': {'table_header': r'$\bf{CS}$', 'format': '.0f'},
        'caughtStealing': {'table_header': r'$\bf{CS}$'},
        'AVG': {'table_header': r'$\bf{AVG}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'avg': {'table_header': r'$\bf{AVG}$'},
        'OBP': {'table_header': r'$\bf{OBP}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'obp': {'table_header': r'$\bf{OBP}$'},
        'SLG': {'table_header': r'$\bf{SLG}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'slg': {'table_header': r'$\bf{SLG}$'},
        'OPS': {'table_header': r'$\bf{OPS}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'ops': {'table_header': r'$\bf{OPS}$'},
        'wOBA': {'table_header': r'$\bf{wOBA}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'wRC+': {'table_header': r'$\bf{wRC+}$', 'format': '.0f'},
        'WAR': {'table_header': r'$\bf{WAR}$', 'format': '.1f'},
        'BB%': {'table_header': r'$\bf{BB\%}$'},
        'walksPerPlateAppearance': {'table_header': r'$\bf{BB\ /\;PA}$'},
        'K%': {'table_header': r'$\bf{K\%}$'},
        'BB/K': {'table_header': r'$\bf{BB/K}$', 'format': '.2f'},
        'walksPerStrikeout': {'table_header': r'$\bf{BB/K}$'},
        'ISO': {'table_header': r'$\bf{ISO}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'iso': {'table_header': r'$\bf{ISO}$'},
        'Spd': {'table_header': r'$\bf{Spd}$', 'format': '.1f'},
        'BABIP': {'table_header': r'$\bf{BABIP}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'babip': {'table_header': r'$\bf{BABIP}$'},
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
        'groundOuts': {'table_header': r'$\bf{GO}$', 'format': '.0f'},
        'airOuts': {'table_header': r'$\bf{AO}$', 'format': '.0f'},
        'groundIntoTriplePlay': {'table_header': r'$\bf{GITP}$', 'format': '.0f'},
        'numberOfPitches': {'table_header': r'$\bf{P}$', 'format': '.0f'},
        'totalBases': {'table_header': r'$\bf{TB}$', 'format': '.0f'},
        'leftOnBase': {'table_header': r'$\bf{LOB}$', 'format': '.0f'},
        'groundOutsToAirouts': {'table_header': r'$\bf{GO/AO}$'},
        'catchersInterference': {'table_header': r'$\bf{CI}$', 'format': '.0f'},
        'atBatsPerHomeRun': {'table_header': r'$\bf{AB/HR}$'},
    }



