color_stats = ['velocity', 'release_extension', 'delta_run_exp_per_100',
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

# Define the codes for different types of swings and whiffs
swing_code = ['foul_bunt','foul','hit_into_play','swinging_strike', 'foul_tip',
            'swinging_strike_blocked','missed_bunt','bunt_foul_tip']
            
whiff_code = ['swinging_strike', 'foul_tip', 'swinging_strike_blocked']


team_logo_urls = {
    'ARI': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/ari.png&h=500&w=500',
    'ATL': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/atl.png&h=500&w=500',
    'BAL': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/bal.png&h=500&w=500',
    'BOS': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/bos.png&h=500&w=500',
    'CHC': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/chc.png&h=500&w=500',
    'CWS': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/chw.png&h=500&w=500',
    'CIN': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/cin.png&h=500&w=500',
    'CLE': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/cle.png&h=500&w=500',
    'COL': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/col.png&h=500&w=500',
    'DET': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/det.png&h=500&w=500',
    'HOU': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/hou.png&h=500&w=500',
    'KC': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/kc.png&h=500&w=500',
    'LAA': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/laa.png&h=500&w=500',
    'LAD': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/lad.png&h=500&w=500',
    'MIA': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/mia.png&h=500&w=500',
    'MIL': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/mil.png&h=500&w=500',
    'MIN': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/min.png&h=500&w=500',
    'NYM': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/nym.png&h=500&w=500',
    'NYY': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/nyy.png&h=500&w=500',
    'OAK': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/oak.png&h=500&w=500',
    'PHI': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/phi.png&h=500&w=500',
    'PIT': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/pit.png&h=500&w=500',
    'SD': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/sd.png&h=500&w=500',
    'SF': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/sf.png&h=500&w=500',
    'SEA': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/sea.png&h=500&w=500',
    'STL': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/stl.png&h=500&w=500',
    'TB': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/tb.png&h=500&w=500',
    'TEX': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/tex.png&h=500&w=500',
    'TOR': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/tor.png&h=500&w=500',
    'WSH': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/wsh.png&h=500&w=500'
}

mlb_teams = {
    109: {'abbrev': 'ARI', 'name': 'Arizona Diamondbacks'},
    144: {'abbrev': 'ATL', 'name': 'Atlanta Braves'},
    110: {'abbrev': 'BAL', 'name': 'Baltimore Orioles'},
    111: {'abbrev': 'BOS', 'name': 'Boston Red Sox'},
    112: {'abbrev': 'CHC', 'name': 'Chicago Cubs'},
    145: {'abbrev': 'CWS', 'name': 'Chicago White Sox'},
    113: {'abbrev': 'CIN', 'name': 'Cincinnati Reds'},
    114: {'abbrev': 'CLE', 'name': 'Cleveland Guardians'},
    115: {'abbrev': 'COL', 'name': 'Colorado Rockies'},
    116: {'abbrev': 'DET', 'name': 'Detroit Tigers'},
    117: {'abbrev': 'HOU', 'name': 'Houston Astros'},
    118: {'abbrev': 'KC', 'name': 'Kansas City Royals'},
    108: {'abbrev': 'LAA', 'name': 'Los Angeles Angels'},
    119: {'abbrev': 'LAD', 'name': 'Los Angeles Dodgers'},
    146: {'abbrev': 'MIA', 'name': 'Miami Marlins'},
    158: {'abbrev': 'MIL', 'name': 'Milwaukee Brewers'},
    142: {'abbrev': 'MIN', 'name': 'Minnesota Twins'},
    121: {'abbrev': 'NYM', 'name': 'New York Mets'},
    147: {'abbrev': 'NYY', 'name': 'New York Yankees'},
    133: {'abbrev': 'OAK', 'name': 'Oakland Athletics'},
    143: {'abbrev': 'PHI', 'name': 'Philadelphia Phillies'},
    134: {'abbrev': 'PIT', 'name': 'Pittsburgh Pirates'},
    135: {'abbrev': 'SD', 'name': 'San Diego Padres'},
    137: {'abbrev': 'SF', 'name': 'San Francisco Giants'},
    136: {'abbrev': 'SEA', 'name': 'Seattle Mariners'},
    138: {'abbrev': 'STL', 'name': 'St. Louis Cardinals'},
    139: {'abbrev': 'TB', 'name': 'Tampa Bay Rays'},
    140: {'abbrev': 'TEX', 'name': 'Texas Rangers'},
    141: {'abbrev': 'TOR', 'name': 'Toronto Blue Jays'},
    120: {'abbrev': 'WSH', 'name': 'Washington Nationals'}
}


#     {"team": "AZ", "team_id": 109, "abbreviation": "ARI", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/ari.png&h=500&w=500"},
#     {"team": "ATL", "team_id": 144, "abbreviation": "ATL", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/atl.png&h=500&w=500"},
#     {"team": "BAL", "team_id": 110, "abbreviation": "BAL", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/bal.png&h=500&w=500"},
#     {"team": "BOS", "team_id": 111, "abbreviation": "BOS", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/bos.png&h=500&w=500"},
#     {"team": "CHC", "team_id": 112, "abbreviation": "CHC", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/chc.png&h=500&w=500"},
#     {"team": "CWS", "team_id": 145, "abbreviation": "CWS", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/chw.png&h=500&w=500"},
#     {"team": "CIN", "team_id": 113, "abbreviation": "CIN", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/cin.png&h=500&w=500"},
#     {"team": "CLE", "team_id": 114, "abbreviation": "CLE", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/cle.png&h=500&w=500"},
#     {"team": "COL", "team_id": 115, "abbreviation": "COL", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/col.png&h=500&w=500"},
#     {"team": "DET", "team_id": 116, "abbreviation": "DET", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/det.png&h=500&w=500"},
#     {"team": "HOU", "team_id": 117, "abbreviation": "HOU", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/hou.png&h=500&w=500"},
#     {"team": "KC", "team_id": 118, "abbreviation": "KC", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/kc.png&h=500&w=500"},
#     {"team": "LAA", "team_id": 108, "abbreviation": "LAA", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/laa.png&h=500&w=500"},
#     {"team": "LAD", "team_id": 119, "abbreviation": "LAD", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/lad.png&h=500&w=500"},
#     {"team": "MIA", "team_id": 146, "abbreviation": "MIA", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/mia.png&h=500&w=500"},
#     {"team": "MIL", "team_id": 158, "abbreviation": "MIL", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/mil.png&h=500&w=500"},
#     {"team": "MIN", "team_id": 142, "abbreviation": "MIN", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/min.png&h=500&w=500"},
#     {"team": "NYM", "team_id": 121, "abbreviation": "NYM", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/nym.png&h=500&w=500"},
#     {"team": "NYY", "team_id": 147, "abbreviation": "NYY", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/nyy.png&h=500&w=500"},
#     {"team": "OAK", "team_id": 133, "abbreviation": "OAK", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/oak.png&h=500&w=500"},
#     {"team": "PHI", "team_id": 143, "abbreviation": "PHI", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/phi.png&h=500&w=500"},
#     {"team": "PIT", "team_id": 134, "abbreviation": "PIT", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/pit.png&h=500&w=500"},
#     {"team": "SD", "team_id": 135, "abbreviation": "SD", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/sd.png&h=500&w=500"},
#     {"team": "SF", "team_id": 137, "abbreviation": "SF", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/sf.png&h=500&w=500"},
#     {"team": "SEA", "team_id": 136, "abbreviation": "SEA", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/sea.png&h=500&w=500"},
#     {"team": "STL", "team_id": 138, "abbreviation": "STL", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/stl.png&h=500&w=500"},
#     {"team": "TB", "team_id": 139, "abbreviation": "TB", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/tb.png&h=500&w=500"},
#     {"team": "TEX", "team_id": 140, "abbreviation": "TEX", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/tex.png&h=500&w=500"},
#     {"team": "TOR", "team_id": 141, "abbreviation": "TOR", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/tor.png&h=500&w=500"},
#     {"team": "WSH", "team_id": 120, "abbreviation": "WSH", "logo_url": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/wsh.png&h=500&w=500"}
# ]

