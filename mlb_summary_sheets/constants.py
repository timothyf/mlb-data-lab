import matplotlib

STATS_API_BASE_URL = "https://statsapi.mlb.com/api/v1/"
FANGRAPHS_BASE_URL = "https://www.fangraphs.com/api/leaders/major-league/data"
MLB_STATIC_BASE_URL = "https://img.mlbstatic.com/mlb-photos/image/"

color_stats = ['release_speed', 'release_extension', 'delta_run_exp_per_100', 
               'whiff_rate', 'in_zone_rate', 'chase_rate', 'xwoba']

statcast_events = {
    'batted_ball_events': [
        'single', 'double', 'triple', 'home_run', 'field_out', 'grounded_into_double_play', 'force_out', 'sac_fly',
        'sac_bunt', 'field_error', 'double_play', 'triple_play', 'catcher_interf', 'fielders_choice'
    ],
    'hit_events': ['single', 'double', 'triple', 'home_run'],
    'strikeout_events': ['strikeout', 'strikeout_double_play', 'strikeout_triple_play'],
    'walk_events': ['walk', 'intent_walk', 'hit_by_pitch'],
    'other_events': ['runner_double_play', 'fielders_choice_out'],
    'uncommon_events': ['other_out', 'fan_interference' 'batter_interference', 'sac_bunt_double_play'],
    'out_events': [
        'field_out', 'grounded_into_double_play', 'force_out', 'sac_fly',
        'sac_bunt', 'field_error', 'double_play', 'triple_play', 'catcher_interf', 'fielders_choice'
    ]
}

event_styles = {
    'single': {'marker': 'o', 'color': '#1f77b4', 'label': 'Single'}, # Blue for singles
    'double': {'marker': 'o', 'color': '#2ca02c', 'label': 'Double'}, # Green for doubles
    'triple': {'marker': 'o', 'color': '#ff7f0e', 'label': 'Triple'}, # Orange for triples
    'home_run': {'marker': 'o', 'color': '#d62728', 'label': 'Home Run'}, # Red for home runs
    'field_out': {'marker': 'x', 'color': 'grey', 'label': 'Field Out'},
    'grounded_into_double_play': {'marker': 'x', 'color': 'grey', 'label': 'GIDP'},
    'force_out': {'marker': 'x', 'color': 'grey', 'label': 'Force Out'},
    'sac_fly': {'marker': 's', 'color': 'grey', 'label': 'Sac Fly'},
    'sac_bunt': {'marker': 's', 'color': 'grey', 'label': 'Sac Bunt'},
    'field_error': {'marker': 'x', 'color': 'grey', 'label': 'Error'},
    'double_play': {'marker': 'x', 'color': 'grey', 'label': 'Double Play'},
    'triple_play': {'marker': 'x', 'color': 'grey', 'label': 'Triple Play'},
    'catcher_interf': {'marker': 'x', 'color': 'grey', 'label': 'Catcher Interference'},
    'fielders_choice': {'marker': 'x', 'color': 'grey', 'label': 'Fielder\'s Choice'}
}

# event_colors = {
#     '1B': '#1f77b4',  # Blue for singles
#     '2B': '#2ca02c',  # Green for doubles
#     '3B': '#ff7f0e',  # Orange for triples
#     'HR': '#d62728',  # Red for home runs
#     'LD': '#9467bd',  # Purple for line drives or another hit type
# }


# Define color maps
cmap_sum = matplotlib.colors.LinearSegmentedColormap.from_list("", ['#648FFF','#FFFFFF','#FFB000'])
cmap_sum_r = matplotlib.colors.LinearSegmentedColormap.from_list("", ['#FFB000','#FFFFFF','#648FFF'])

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
            'in_zone_rate',
            'chase_rate',
            'xwoba',
            ]

### PITCH COLORS ###
pitch_colors = {
    ## Fastballs ##
    'FF': {'colour': '#FF007D', 'name': '4-Seam Fastball'},
    'FA': {'colour': '#FF007D', 'name': 'Fastball'},
    'SI': {'colour': '#98165D', 'name': 'Sinker'},
    'FC': {'colour': '#BE5FA0', 'name': 'Cutter'},

    ## Offspeed ##
    'CH': {'colour': '#F79E70', 'name': 'Changeup'},
    'FS': {'colour': '#FE6100', 'name': 'Splitter'},
    'SC': {'colour': '#F08223', 'name': 'Screwball'},
    'FO': {'colour': '#FFB000', 'name': 'Forkball'},

    ## Sliders ##
    'SL': {'colour': '#67E18D', 'name': 'Slider'},
    'ST': {'colour': '#1BB999', 'name': 'Sweeper'},
    'SV': {'colour': '#376748', 'name': 'Slurve'},

    ## Curveballs ##
    'KC': {'colour': '#311D8B', 'name': 'Knuckle Curve'},
    'CU': {'colour': '#3025CE', 'name': 'Curveball'},
    'CS': {'colour': '#274BFC', 'name': 'Slow Curve'},
    'EP': {'colour': '#648FFF', 'name': 'Eephus'},

    ## Others ##
    'KN': {'colour': '#867A08', 'name': 'Knuckleball'},
    'PO': {'colour': '#472C30', 'name': 'Pitch Out'},
    'UN': {'colour': '#9C8975', 'name': 'Unknown'},
}


# Define the codes for different types of swings and whiffs
swing_code = ['foul_bunt','foul','hit_into_play','swinging_strike', 'foul_tip',
            'swinging_strike_blocked','missed_bunt','bunt_foul_tip']
            
whiff_code = ['swinging_strike', 'foul_tip', 'swinging_strike_blocked']

pitch_stats_dict = {
    'pitch': {'table_header': '$\\bf{Count}$', 'format': '.0f'},
    'release_speed': {'table_header': '$\\bf{Velocity}$', 'format': '.1f'},
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