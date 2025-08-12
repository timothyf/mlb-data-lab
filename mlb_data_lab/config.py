from dataclasses import dataclass, field
from typing import Dict, List
import os

STATS_API_BASE_URL = "https://statsapi.mlb.com/api/v1/"
FANGRAPHS_BASE_URL = "https://www.fangraphs.com/api/leaders/major-league/data"
FANGRAPHS_NEXT_URL = "https://www.fangraphs.com/_next/data/Gtd7iofF2h1X98b-Nerh6/players"
MLB_STATIC_BASE_URL = "https://img.mlbstatic.com/mlb-photos/image/"

# https://tjstatsapps-2025-mlb-pitching-app.hf.space/session/d2492a78e6783686d77e033535d0f94086a09e7c5b5fcc3ff961abc3c39ee809/download/download_all?w=

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

pitch_summary_columns = [ 'pitch_description',
            'pitch',
            'pitch_usage',
            'release_speed',
            'pfx_z',
            'pfx_x',
            'release_spin_rate',
            'release_pos_x',
            'release_pos_z',
            'release_extension',
            'delta_run_exp_per_100',
            'whiff_rate',
           # 'in_zone_rate',
           # 'chase_rate',
            'xwoba',
        ]


### PITCH COLORS ###
pitch_colors = {
    ## Fastballs ##
    'FF': {'color': '#FF007D', 'name': '4-Seam Fastball'},
    'FA': {'color': '#FF007D', 'name': 'Fastball'},
    'SI': {'color': '#98165D', 'name': 'Sinker'},
    'FC': {'color': '#BE5FA0', 'name': 'Cutter'},

    ## Offspeed ##
    'CH': {'color': '#F79E70', 'name': 'Changeup'},
    'FS': {'color': '#FE6100', 'name': 'Splitter'},
    'SC': {'color': '#F08223', 'name': 'Screwball'},
    'FO': {'color': '#FFB000', 'name': 'Forkball'},

    ## Sliders ##
    'SL': {'color': '#67E18D', 'name': 'Slider'},
    'ST': {'color': '#1BB999', 'name': 'Sweeper'},
    'SV': {'color': '#376748', 'name': 'Slurve'},

    ## Curveballs ##
    'KC': {'color': '#311D8B', 'name': 'Knuckle Curve'},
    'CU': {'color': '#3025CE', 'name': 'Curveball'},
    'CS': {'color': '#274BFC', 'name': 'Slow Curve'},
    'EP': {'color': '#648FFF', 'name': 'Eephus'},

    ## Others ##
    'KN': {'color': '#867A08', 'name': 'Knuckleball'},
    'PO': {'color': '#472C30', 'name': 'Pitch Out'},
    'UN': {'color': '#9C8975', 'name': 'Unknown'},
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
class LeagueTeams: 
    items = {
    'AL': {
    'BAL', 'BOS', 'CHW', 'CHA', 'CLE', 'DET',
    'HOU', 'KCR', 'KCA', 'LAA', 'MIN', 'NYY', 'NYA',
    'OAK', 'SEA', 'TBR', 'TBA', 'TEX', 'TOR' },
    'NL': {
    'ARI', 'ATL', 'CHC', 'CHN', 'CIN', 'COL',
    'LAD', 'LAN', 'MIA', 'MIL', 'NYM', 'NYN', 'PHI',
    'PIT', 'SDP', 'SDN', 'SFG', 'SFN', 'STL', 'WSN', 'WSH' }
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
                       "groundIntoDoublePlay", "numberOfPitches", "plateAppearances", 
                       "totalBases", "rbi", "leftOnBase", "sacBunts", "sacFlies", "babip"]
        },
        'pitching': {
            'standard': ['W', 'L', 'ERA', 'G', 'GS', 'CG', 'ShO', 'SV', 'HLD', 'BS', 'IP', 'TBF', 'H', 'R', 'ER', 'HR', 'BB', 'IBB', 'HBP', 'WP', 'BK', 'SO'],
            'advanced': ['K/9', 'BB/9', 'K/BB', 'H/9', 'HR/9', 'K%', 'BB%', 'K-BB%', 'AVG', 'WHIP', 'BABIP', 'LOB%', 'ERA-', 'FIP-','FIP', 'RS/9', 'Swing%'],
            'splits': ["groundOuts", "airOuts", "doubles", "triples", "homeRuns", "strikeOuts", 
                       "baseOnBalls", "hits", "hitByPitch", "avg", "atBats", "obp", "slg", 
                       "ops", "numberOfPitches", "inningsPitched", "whip", 
                       "battersFaced", "balls", "strikes", "strikePercentage", 
                       "pitchesPerInning","strikeoutWalkRatio", "strikeoutsPer9Inn", "walksPer9Inn", "hitsPer9Inn"]
        },
    }

@dataclass
class StatsDisplayConfig:

    pitching = {
        'W': {'table_header': r'$\bf{W}$', 'format': '.0f'},
        'L': {'table_header': r'$\bf{L}$', 'format': '.0f'},
        'SV': {'table_header': r'$\bf{SV}$', 'format': '.0f'},
        'IP': {'table_header': r'$\bf{IP}$', 'format': ''},
        'SO': {'table_header': r'$\bf{SO}$', 'format': ''},
        'TBF': {'table_header': r'$\bf{TBF}$', 'format': '.0f'},
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
        'H': {'table_header': r'$\bf{H}$', 'format': '.0f'},
        '2B': {'table_header': r'$\bf{2B}$', 'format': '.0f'},
        '3B': {'table_header': r'$\bf{3B}$', 'format': '.0f'},
        'runs': {'table_header': r'$\bf{R}$', 'format': '.0f'},
        'R': {'table_header': r'$\bf{R}$', 'format': '.0f'},
        'ER': {'table_header': r'$\bf{ER}$', 'format': '.0f'},
        'homeRuns': {'table_header': r'$\bf{HR}$', 'format': '.0f'},
        'HR': {'table_header': r'$\bf{HR}$', 'format': '.0f'},
        'BB': {'table_header': r'$\bf{BB}$', 'format': '.0f'},
        'baseOnBalls' : {'table_header': r'$\bf{BB}$', 'format': ''},
        'IBB': {'table_header': r'$\bf{IBB}$', 'format': '.0f'},
        'HBP': {'table_header': r'$\bf{HBP}$', 'format': '.0f'},
        'SO': {'table_header': r'$\bf{SO}$', 'format': '.0f'},
        'OBP': {'table_header': r'$\bf{OBP}$', 'format': '.3f'},
        'obp': {'table_header': r'$\bf{OBP}$', 'format': ''},
        'SLG': {'table_header': r'$\bf{SLG}$', 'format': '.3f'},
        'slg': {'table_header': r'$\bf{SLG}$', 'format': ''},
        'ERA': {'table_header': r'$\bf{ERA}$', 'format': '.2f'},
        'wOBA': {'table_header': r'$\bf{wOBA}$', 'format': '.3f'},
        'G': {'table_header': r'$\bf{G}$', 'format': '.0f'},
        'GS': {'table_header': r'$\bf{GS}$', 'format': '.0f'},
        'CG': {'table_header': r'$\bf{CG}$', 'format': '.0f'},
        'ShO': {'table_header': r'$\bf{SHO}$', 'format': '.0f'},
        'qualityStarts': {'table_header': r'$\bf{QS}$', 'format': '.0f'},
        'WP': {'table_header': r'$\bf{WP}$', 'format': '.0f'},
        'BK': {'table_header': r'$\bf{BK}$', 'format': '.0f'},
        'RS/9': {'table_header': r'$\bf{RS\ /\;9}$', 'format': '.2f'},
        'H/9': {'table_header': r'$\bf{H\ /\;9}$', 'format': '.2f'},
        'Swing%': {'table_header': r'$\bf{Swing\%}$', 'format': 'percent'},
        'HLD': {'table_header': r'$\bf{HLD}$', 'format': '.0f'},
        'BS': {'table_header': r'$\bf{BS}$', 'format': '.0f'},
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
        'hitBatsmen': {'table_header': r'$\bf{HBP}$', 'format': '.0f'},
        'SH': {'table_header': r'$\bf{SH}$', 'format': '.0f'},
        'SF': {'table_header': r'$\bf{SF}$', 'format': '.0f'},
        'IBB': {'table_header': r'$\bf{IBB}$', 'format': '.0f'},
        'intentionalWalks': {'table_header': r'$\bf{IBB}$', 'format': '.0f'},
        'ROE': {'table_header': r'$\bf{ROE}$', 'format': '.0f'},
        'BAbip': {'table_header': r'$\bf{BAbip}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'babip': {'table_header': r'$\bf{BABIP}$'},
        'tOPS+': {'table_header': r'$\bf{tOPS+}$', 'format': '.0f'},
        'sOPS+': {'table_header': r'$\bf{sOPS+}$', 'format': '.0f'},
        'groundOuts': {'table_header': r'$\bf{GO}$', 'format': '.0f'},
        'airOuts': {'table_header': r'$\bf{AO}$', 'format': '.0f'},
        'groundIntoTriplePlay': {'table_header': r'$\bf{GITP}$', 'format': '.0f'},
        'numberOfPitches': {'table_header': r'$\bf{P}$', 'format': '.0f'},
        'gamesPlayed': {'table_header': r'$\bf{GP}$', 'format': '.0f'},
        'doubles': {'table_header': r'$\bf{2B}$', 'format': '.0f'},
        'triples': {'table_header': r'$\bf{3B}$', 'format': '.0f'},
        'catchersInterference': {'table_header': r'$\bf{CI}$', 'format': '.0f'},
        'strikeOuts': {'table_header': r'$\bf{SO}$', 'format': '.0f'},
        'hitByPitch': {'table_header': r'$\bf{HBP}$', 'format': '.0f'},
        'avg': {'table_header': r'$\bf{AVG}$'},
        'atBats': {'table_header': r'$\bf{AB}$'},
        'groundIntoDoublePlay': {'table_header': r'$\bf{GDP}$'},
        'groundIntoTriplePlay': {'table_header': r'$\bf{GITP}$'},
        'inningsPitched': {'table_header': r'$\bf{IP}$'},
        'outsPitched': {'table_header': r'$\bf{OUTS}$'},
        'whip': {'table_header': r'$\bf{WHIP}$'},
        'battersFaced': {'table_header': r'$\bf{BF}$'},
        'outs': {'table_header': r'$\bf{OUTS}$'},
        'gamesPitched': {'table_header': r'$\bf{GP}$'},
        'balls': {'table_header': r'$\bf{B}$'},
        'strikes': {'table_header': r'$\bf{S}$'},
        'strikePercentage': {'table_header': r'$\bf{S\%}$'},
        'balks': {'table_header': r'$\bf{BK}$'},
        'wildPitches': {'table_header': r'$\bf{WP}$'},
        'totalBases': {'table_header': r'$\bf{TB}$'},
        'groundOutsToAirouts': {'table_header': r'$\bf{GO/AO}$'},
        'pitchesPerInning': {'table_header': r'$\bf{P/IN}$'},
        'rbi': {'table_header': r'$\bf{RBI}$'},
        'pitchesThrown': {'table_header': r'$\bf{P}$'},
        'strikeoutWalkRatio': {'table_header': r'$\bf{K/BB}$'},
        'strikeoutsPer9Inn': {'table_header': r'$\bf{K\ /\;9}$'},
        'walksPer9Inn': {'table_header': r'$\bf{BB\ /\;9}$'},
        'hitsPer9Inn': {'table_header': r'$\bf{H\ /\;9}$'},
        'homeRunsPer9': {'table_header': r'$\bf{HR\ /\;9}$'},
        'sacBunts': {'table_header': r'$\bf{SH}$', 'format': '.0f'},
        'sacFlies': {'table_header': r'$\bf{SF}$', 'format': '.0f'},
        'velocity': {'table_header': r'$\bf{Velo}$', 'format': '.1f'}
    }

    batting = {
        'gamesPlayed': {'table_header': r'$\bf{G}$'},
        'G': {'table_header': r'$\bf{G}$', 'format': '.0f'}, 
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
        'BB%': {'table_header': r'$\bf{BB\%}$', 'format': lambda x: f'{x:.3f}'.lstrip('0')},
        'walksPerPlateAppearance': {'table_header': r'$\bf{BB\ /\;PA}$'},
        'K%': {'table_header': r'$\bf{K\%}$', 'format': 'percent'},
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

    pitch_stats = {
        'pitch': {'table_header': '$\\bf{Count}$', 'format': '.0f'},
        'release_speed': {'table_header': '$\\bf{Velocity}$', 'format': '.1f'},
        'velocity': {'table_header': '$\\bf{Velocity}$', 'format': '.1f'},
        'pfx_z': {'table_header': '$\\bf{iVB}$', 'format': '.1f'},
        'pfx_x': {'table_header': '$\\bf{HB}$', 'format': '.1f'},
        'release_spin_rate': {'table_header': '$\\bf{Spin}$', 'format': '.0f'},
        'release_pos_x': {'table_header': '$\\bf{hRel}$', 'format': '.1f'},
        'release_pos_z': {'table_header': '$\\bf{vRel}$', 'format': '.1f'},
        'release_extension': {'table_header': '$\\bf{Ext.}$', 'format': '.1f'},
        'xwoba': {'table_header': '$\\bf{xwOBA}$', 'format': '.3f'},
        'pitch_usage': {'table_header': '$\\bf{Pitch\\%}$', 'format': '.1%'},
        'whiff_rate': {'table_header': '$\\bf{Whiff\\%}$', 'format': '.1%'},
        'in_zone_rate': {'table_header': '$\\bf{Zone\\%}$', 'format': '.1%'},
        'chase_rate': {'table_header': '$\\bf{Chase\\%}$', 'format': '.1%'},
        'delta_run_exp_per_100': {'table_header': '$\\bf{RV\\//100}$', 'format': '.1f'}
    }



