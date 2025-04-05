-- create_schema.sql
-- SQL schema for unified baseball pitch events,
-- capturing both pitching and batting perspectives in a single fact table.

-- Create the games dimension table
CREATE TABLE IF NOT EXISTS games (
    game_pk BIGINT PRIMARY KEY,
    game_date DATE NOT NULL,
    game_year INT,
    game_type VARCHAR(20),
    home_team VARCHAR(3),  -- Optionally, this can be a foreign key to a teams table
    away_team VARCHAR(3),
    home_score INT,
    away_score INT,
    bat_score INT,
    fld_score INT,
    post_away_score INT,
    post_home_score INT,
    post_bat_score INT,
    post_fld_score INT
);

-- Create the players dimension table
CREATE TABLE IF NOT EXISTS players (
    player_id SERIAL PRIMARY KEY,
    player_name VARCHAR(100) UNIQUE,
    stand VARCHAR(1),      -- e.g., 'L' or 'R'
    p_throws VARCHAR(1)     -- e.g., 'L' or 'R'
);

-- Create the umpires dimension table (optional)
CREATE TABLE IF NOT EXISTS umpires (
    umpire_id SERIAL PRIMARY KEY,
    umpire_name VARCHAR(100) UNIQUE
);

-- Create the unified plate_appearances fact table capturing both batter and pitcher metrics
CREATE TABLE IF NOT EXISTS plate_appearances (
    appearance_id SERIAL PRIMARY KEY,
    
    -- Foreign Keys
    game_pk BIGINT REFERENCES games(game_pk),
    batter_id INT REFERENCES players(player_id),
    pitcher_id INT REFERENCES players(player_id),
    umpire_id INT REFERENCES umpires(umpire_id),
    
    -- Game and Inning Details
    game_date DATE,
    game_year INT,
    game_type VARCHAR(20),
    inning INT,
    inning_topbot VARCHAR(3),  -- e.g., 'top' or 'bot'
    at_bat_number INT,
    pitch_number INT,
    
    -- Pitch Metrics
    pitch_type VARCHAR(10),
    pitch_name VARCHAR(50),
    release_speed REAL,
    release_pos_x REAL,
    release_pos_z REAL,
    release_pos_y REAL,
    spin_dir REAL,
    release_spin_rate REAL,
    release_extension REAL,
    pfx_x REAL,
    pfx_z REAL,
    plate_x REAL,
    plate_z REAL,
    vx0 REAL,
    vy0 REAL,
    vz0 REAL,
    ax REAL,
    ay REAL,
    az REAL,
    sz_top REAL,
    sz_bot REAL,
    
    -- Batted Ball & Outcome Metrics
    hit_distance_sc REAL,
    launch_speed REAL,
    launch_angle REAL,
    effective_speed REAL,
    hc_x REAL,
    hc_y REAL,
    spin_axis REAL,
    delta_home_win_exp REAL,
    delta_run_exp REAL,
    bat_speed REAL,
    swing_length REAL,
    delta_pitcher_run_exp REAL,
    hyper_speed REAL,
    home_score_diff INT,
    bat_score_diff INT,
    home_win_exp REAL,
    bat_win_exp REAL,
    
    -- Event and Description Fields
    events VARCHAR(50),
    description TEXT,
    zone INT,
    des TEXT,
    hit_location INT,
    bb_type VARCHAR(50),
    balls INT,
    strikes INT,
    
    -- Deprecated and Additional Metrics
    spin_rate_deprecated REAL,
    break_angle_deprecated REAL,
    break_length_deprecated REAL,
    tfs_deprecated REAL,
    tfs_zulu_deprecated TIMESTAMP,
    estimated_ba_using_speedangle REAL,
    estimated_woba_using_speedangle REAL,
    woba_value REAL,
    woba_denom REAL,
    babip_value REAL,
    iso_value REAL,
    launch_speed_angle REAL,
    
    -- Fielding and Alignment Info
    fielder_2 VARCHAR(50),
    fielder_3 VARCHAR(50),
    fielder_4 VARCHAR(50),
    fielder_5 VARCHAR(50),
    fielder_6 VARCHAR(50),
    fielder_7 VARCHAR(50),
    fielder_8 VARCHAR(50),
    fielder_9 VARCHAR(50),
    if_fielding_alignment TEXT,
    of_fielding_alignment TEXT,
    
    -- Advanced Batting/Pitching Context
    n_thruorder_pitcher INT,
    n_priorpa_thisgame_player_at_bat INT,
    pitcher_days_since_prev_game INT,
    batter_days_since_prev_game INT,
    pitcher_days_until_next_game INT,
    batter_days_until_next_game INT,
    api_break_z_with_gravity REAL,
    api_break_x_arm REAL,
    api_break_x_batter_in REAL,
    arm_angle REAL
);
