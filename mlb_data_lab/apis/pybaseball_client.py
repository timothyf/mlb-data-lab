import pybaseball as pyb
import pandas as pd
from mlb_data_lab.config import StatsConfig
from mlb_data_lab.apis.mlb_stats_client import MlbStatsClient
import os


class PybaseballClient: 
    

    @staticmethod
    def fetch_fangraphs_batter_data(player_name: str, team_fangraphs_id: str, start_year: int, end_year: int):
        data = pyb.batting_stats(start_season=start_year, end_season=end_year, team=team_fangraphs_id, qual=1)
        try:
            player_stats = data[data['Name'] == player_name]
            
            if player_stats.empty:
                print(f"Player '{player_name}' not found.")
                return None
            else:
                return player_stats.to_dict(orient='records')[0]
        except KeyError:
            print("The data does not contain the expected columns.")
            return None

    @staticmethod
    def fetch_fangraphs_pitcher_data(player_name: str, team_fangraphs_id: str, start_year: int, end_year: int):
        data = pyb.pitching_stats(start_season=start_year, end_season=end_year, team=team_fangraphs_id, qual=1)
        try:
            player_stats = data[data['Name'] == player_name]
            
            if player_stats.empty:
                print(f"Player '{player_name}' not found.")
                return None
            else:
                return player_stats.to_dict(orient='records')[0]
        except KeyError:
            print("The data does not contain the expected columns.")
            return None
        
    @staticmethod
    def fetch_team_batting_stats(team_abbrev: str, start_year: int, end_year: int):
        data = pyb.team_batting(start_year, end_year, 'al')   
        stats = data.query(f"Team == '{team_abbrev}'")     
        return stats
    
    @staticmethod
    def fetch_team_pitching_stats(team_abbrev: str, start_year: int, end_year: int):
        data = pyb.team_pitching(start_year, end_year, 'al')   
        stats = data.query(f"Team == '{team_abbrev}'")     
        return stats
    
    @staticmethod
    def fetch_team_schedule_and_record(team_abbrev: str, season: int):
        print(f"Fetching schedule and record for {team_abbrev} in season {season}...")
        data = pyb.schedule_and_record(season, team_abbrev)
        return data
    
    @staticmethod
    def lookup_player(last_name: str, first_name: str, fuzzy: bool = False):
        return pyb.playerid_lookup(last_name, first_name, fuzzy=fuzzy)
    
    @staticmethod
    def lookup_player_by_id(player_id: int):
        #print(f"Looking up player by ID: {player_id}")
        return pyb.playerid_reverse_lookup([player_id], key_type='mlbam')

    @staticmethod
    def fetch_statcast_batter_data(player_id: int, start_date: str, end_date: str):
        statcast_data = pyb.statcast_batter(start_date, end_date, player_id)  
        return statcast_data
    

    @staticmethod
    def save_statcast_batter_data(player_id: int, year: int, file_path: str = None):
        season_info = MlbStatsClient.get_season_info(year)
        start_date = season_info['regularSeasonStartDate']
        end_date = season_info['regularSeasonEndDate']
        statcast_data = pyb.statcast_batter(start_date, end_date, player_id)
        if statcast_data is not None and not statcast_data.empty:
            if file_path is None:
                file_path = f'output/statcast_data_{player_id}_{start_date}_{end_date}.csv'

            # Ensure that the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            statcast_data.to_csv(file_path, index=False)
            print(f"Statcast data saved to {file_path}")
        else:
            print("No valid statcast data found to save.")
        return
    
    @staticmethod
    def save_statcast_pitcher_data(player_id: int, year: int, file_path: str = None):
        season_info = MlbStatsClient.get_season_info(year)
        start_date = season_info['regularSeasonStartDate']
        end_date = season_info['regularSeasonEndDate']
        statcast_data = pyb.statcast_pitcher(start_date, end_date, player_id)
        if statcast_data is not None and not statcast_data.empty:
            if file_path is None:
                file_path = f'output/statcast_data_{player_id}_{start_date}_{end_date}.csv'

            # Ensure that the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            statcast_data.to_csv(file_path, index=False)
            print(f"Statcast data saved to {file_path}")
        else:
            print("No valid statcast data found to save.")
        return
    
    @staticmethod
    def fetch_statcast_pitcher_data(pitcher_id: int, start_date: str, end_date: str):
        df_pyb = pyb.statcast_pitcher(start_date, end_date, pitcher_id)
        df_pyb.head()
        return df_pyb


    # Split types returned:
        # ['Career Totals', 'Last 7 days', 'Last 14 days', 'Last 28 days', 'Last 365 days', 'vs RHP', 'vs LHP', 
        #  'vs RHP as LHB', 'vs LHP as LHB', 'vs RH Starter', 'vs LH Starter', 'Home', 'Away', '1st Half', '2nd Half', 
        #  'April/March', 'May', 'June', 'July', 'August', 'Sept/Oct', 'in Wins', 'in Losses', 'as Starter', 'as Sub', 
        #  'as LF', 'as CF', 'as RF', 'as DH', 'as PH', '1st Batter G', 'Leadoff Inn.', 'Batting 1st', 'Batting 2nd', 
        #  'Batting 3rd', 'Batting 4th', 'Batting 5th', 'Batting 6th', 'Batting 9th', 'Swung at 1st Pitch', 'Took 1st Pitch', 
        #  'First Pitch', '1-0 Count', '2-0 Count', '3-0 Count', '0-1 Count', '1-1 Count', '2-1 Count', '3-1 Count', 
        #  '0-2 Count', '1-2 Count', '2-2 Count', 'Full Count', 'After 1-0', 'After 2-0', 'After 3-0', 'After 0-1', 
        #  'After 1-1', 'After 2-1', 'After 3-1', 'After 0-2', 'After 1-2', 'After 2-2', 'Zero Balls', 'Zero Strikes', 
        #  'Three Balls', 'Two Strikes', 'Batter Ahead', 'Even Count', 'Pitcher Ahead', '0 outs', '1 out', '2 outs', 
        #  'RISP', '---', 'Men On', '1--', '-2-', '--3', '12-', '1-3', '-23', '123', 'on 1st, <2 out', 'on 3rd, <2 out', 
        #  'on 3rd, 2 out', '0 out, ---', '0 out, 1--', '0 out, -2-', '0 out, --3', '0 out, 12-', '0 out, 1-3', '0 out, -23', 
        #  '0 out, 123', '1 out, ---', '1 out, 1--', '1 out, -2-', '1 out, --3', '1 out, 12-', '1 out, 1-3', '1 out, -23', 
        #  '1 out, 123', '2 out, ---', '2 out, 1--', '2 out, -2-', '2 out, --3', '2 out, 12-', '2 out, 1-3', '2 out, -23', 
        #  '2 out, 123', '2 outs, RISP', 'Late & Close', 'Tie Game', 'Within 1 R', 'Within 2 R', 'Within 3 R', 'Within 4 R', 
        #  'Margin > 4 R', 'Ahead', 'Behind', 'High Lvrge', 'Medium Lvrge', 'Low Lvrge', 'vs. SP', 'vs. RP', 'vs. SP, 1st', 
        #  'vs. SP, 2nd', 'vs. SP, 3rd', 'vs. SP, 4th+', 'vs. RP, 1st', 'vs. RP, 2nd', 'vs. Power', 'vs. avg.P/F', 
        #  'vs. Finesse', 'vs. Fly Ball', 'vs. avg.F/G', 'vs. GrndBall', 'To Infield', 'To Outfield', 'Ball In Play', 
        #  'Not in Play', 'Fair Terr', 'Foul Terr', 'Pulled-LHB', 'Up Mdle-LHB', 'Opp Fld-LHB', 'Ground Balls', 'Fly Balls', 
        #  'Line Drives', 'Inter-League', 'Los Angeles Angels', 'Arizona Diamondbacks', 'Atlanta Braves', 'Baltimore Orioles', 
        #  'Boston Red Sox', 'Chicago Cubs', 'Chicago White Sox', 'Cincinnati Reds', 'Cleveland Guardians', 'Colorado Rockies', 
        #  'Miami Marlins', 'Houston Astros', 'Kansas City Royals', 'Los Angeles Dodgers', 'Milwaukee Brewers', 
        #  'Minnesota Twins', 'New York Mets', 'New York Yankees', 'Oakland Athletics', 'Philadelphia Phillies', 
        #  'Pittsburgh Pirates', 'San Diego Padres', 'Seattle Mariners', 'San Francisco Giants', 'St. Louis Cardinals', 
        #  'Tampa Bay Rays', 'Texas Rangers', 'Toronto Blue Jays', 'Washington Nationals', 'WP < .500', 'WP >= .500', 
        #  'Night', 'Day', 'Open', 'Dome', 'Retract', 'Grass', 'Artif. Turf', 'LAA-Angel Stad', 'ARI-Chase Field', 
        #  'Muncy Bank BP', 'STL-Busch Stad 3', 'NYM-Citi Field', 'DET-Comerica Pk', 'CHW-Guaranteed', 'HOU-MinuteMaidPk', 
        #  'BOS-Fenway Pk', 'CIN-GreatAmer BP', 'CLE-Progressive', 'MIA-loanDepot pk', 'MIL-Am Fam Field', 'WSN-Natls Park', 
        #  'OAK-Oakland Col.', 'BAL-Camden Yards', 'SFG-Oracle Park', 'SDP-Petco Pk', 'PIT-PNC Pk', 'KCR-KauffmanStad', 
        #  'SEA-T-Mobile Pk', 'TOR-Rogers Ctr', 'ATL-Truist Pk', 'MIN-Target Field', 'TBR-TropicanaFld', 'CHC-Wrigley Fld', 
        #  'NYY-Yankee Stad3', 'TEX-GlbLifeField']

        # Acces example:
        #    data.xs('vs LHP', level=1)['AB']
        
    @staticmethod
    def fetch_batting_splits_leaderboards(player_bbref: str, season: int) -> pd.DataFrame:
        splits_stats_list = StatsConfig().stat_lists['batting']['splits']
        print(f"Fetching batting splits data for player {player_bbref} in season {season}...")
        
        try:
            data = pyb.get_splits(playerid=player_bbref, year=season)
        except IndexError as e:
            print("IndexError caught in get_splits:", e)
            # Return an empty DataFrame if no splits data is available
            return pd.DataFrame()
        
        # Convert to DataFrame if not already one
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)
        
        # Process splits data
        split_labels = ['vs LHP', 'vs RHP', 'Ahead', 'Behind']
        combined_data = process_splits(data, splits_stats_list, split_labels, player_bbref, season)
        
        return combined_data


    
    @staticmethod
    def fetch_pitching_splits_leaderboards(player_bbref: str, season: int) -> pd.DataFrame:
        # Define the columns you want to keep for pitching splits
        splits_stats_list = StatsConfig().stat_lists['pitching']['splits']

        try:
            # Fetching the splits data for pitching
            data = pyb.get_splits(playerid=player_bbref, year=season, pitching_splits=True)
            df1, df2 = data

            # Check if the requested season is present in df1
            split_years = df1.index.get_level_values('Split').str.extract(r'(\d{4})')[0]
            split_years = split_years.dropna().astype(int)

            if season not in split_years.values:
                print(f"Warning: No splits data available for {season}.")
                return pd.DataFrame()

            data = df1

        except IndexError as e:
            print(f"IndexError: {e}. Failed to fetch data for player {player_bbref} in season {season}.")
            return pd.DataFrame()

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return pd.DataFrame()

        # Process splits data
        split_labels = ['vs LHB', 'vs RHB', 'Ahead', 'Behind']
        combined_data = process_splits(data, splits_stats_list, split_labels, player_bbref, season)

        return combined_data

def process_splits(data, splits_stats_list, split_labels, player_bbref, season):
        """
        Processes split data by extracting relevant columns, calculating stats, 
        and handling missing data for specific split types.
        """
        splits_data = {}

        for split in split_labels:
            try:
                split_data = data.xs(split, level=1)
            except KeyError:
                print(f"No data found for {split} for player {player_bbref} in season {season}.")
                split_data = pd.DataFrame()  # Empty DataFrame if split is not found

            # Handle missing columns by reindexing
            split_data = split_data.reindex(columns=splits_stats_list)

            # Handle specific columns like 'H', 'AB', 'AVG' for batting splits
            if not split_data.empty and {'H', 'AB'}.issubset(split_data.columns):
                split_data['H'] = pd.to_numeric(split_data['H'], errors='coerce')
                split_data['AB'] = pd.to_numeric(split_data['AB'], errors='coerce')
                split_data['AVG'] = split_data['H'] / split_data['AB']

                # Replace inf and -inf values with 0 (avoid inplace=True)
                split_data['AVG'] = split_data['AVG'].replace([float('inf'), -float('inf')], 0)

                # Fill NaN values with 0 (avoid inplace=True)
                split_data['AVG'] = split_data['AVG'].fillna(0)

            splits_data[split] = split_data

        # Filter out empty DataFrames and combine valid splits
        valid_splits = {key: df for key, df in splits_data.items() if not df.dropna(how='all').empty}

        if valid_splits:
            combined_data = pd.concat(valid_splits.values(), keys=valid_splits.keys(), axis=0)
        else:
            combined_data = pd.DataFrame()  # Empty DataFrame if no valid splits exist
        
        return combined_data
