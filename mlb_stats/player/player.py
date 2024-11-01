from io import BytesIO
from PIL import Image

from mlb_stats.team.team import Team
from mlb_stats.player.player_bio import PlayerBio
from mlb_stats.apis.data_fetcher import DataFetcher
from mlb_stats.player.player_lookup import PlayerLookup
from mlb_stats.apis.mlb_stats_client import MlbStatsClient
from mlb_stats.player.player_info import PlayerInfo
from mlb_stats.apis.pybaseball_client import PybaseballClient
from mlb_stats.config import STATCAST_DATA_DIR
from mlb_stats.apis.pybaseball_client import PybaseballClient


class Player:

    def __init__(self, mlbam_id: int):
        self.mlbam_id = mlbam_id
        self.bbref_id = None
        self.player_info = PlayerInfo()
        self.player_bio = PlayerBio() 
        self.current_team = Team()
        self.player_standard_stats = None
        self.player_advanced_stats = None
        self.player_splits_stats = None
        

    def set_player_stats(self, season):
        if self.player_info.primary_position == 'P':
            self.player_standard_stats = PybaseballClient.fetch_fangraphs_pitcher_data(player_name=self.player_bio.full_name, team_fangraphs_id=self.current_team.fangraphs_id, start_year=season, end_year=season)
            self.player_advanced_stats = self.player_standard_stats
            self.player_splits_stats = PybaseballClient.fetch_pitching_splits_leaderboards(player_bbref=self.bbref_id, season=season)
        else:
            self.player_standard_stats = PybaseballClient.fetch_fangraphs_batter_data(player_name=self.player_bio.full_name, team_fangraphs_id=self.current_team.fangraphs_id, start_year=season, end_year=season)
            self.player_advanced_stats = self.player_standard_stats
            self.player_splits_stats = PybaseballClient.fetch_batting_splits_leaderboards(player_bbref=self.bbref_id, season=season)


    @staticmethod
    def create_from_mlb(mlbam_id: int = None, player_name: str = None): 
        if player_name:
            print(f"Creating player: {player_name}")
            # Lookup player data using player name
            player_data = PlayerLookup.lookup_player(player_name)
            
            if player_data is None:
                print (f"Could not find player data for: {player_name}")
                return None
            mlbam_id = player_data.get('key_mlbam')

            # Check if mlbam_id is a list and get the first element
            if isinstance(mlbam_id, list):
                print(f"mlbam_id lists: {mlbam_id}")
                #mlbam_id = mlbam_id[0]
            bbref_id = player_data.get('key_bbref')
            if not mlbam_id:
                raise ValueError(f"Could not find MLBAM ID for player: {player_name}")

        elif mlbam_id:
            # Lookup player data using mlbam_id (if player_name is not provided)
            player_data = PlayerLookup.lookup_player_by_mlbam(mlbam_id)
            player_name = player_data.get('full_name')  # Safely get the player's full name
            bbref_id = player_data.get('key_bbref')
            if not player_name:
                raise ValueError(f"Could not find player name for MLBAM ID: {mlbam_id}")

        else:
            # If neither mlbam_id nor player_name is provided, raise an error
            raise ValueError("At least one of 'mlbam_id' or 'player_name' must be provided.")

        # Create a new player instance and populate details
        player = Player(mlbam_id)
        player.bbref_id = bbref_id
        mlb_player_info = MlbStatsClient.fetch_player_info(mlbam_id)
        player.player_info.set_from_mlb_info(mlb_player_info)
        player.player_bio.set_from_mlb_info(mlb_player_info)
        player.set_team(mlb_player_info)
        return player

    def set_team(self, mlb_player_info):
        team_id = mlb_player_info.get('currentTeam', {}).get('id')
        self.current_team = Team.create_from_mlb(team_id=team_id)

    def get_headshot(self):
        headshot = DataFetcher.fetch_player_headshot(self.mlbam_id)
        img = Image.open(BytesIO(headshot))
        return img
    
    def save_statcast_data(self, year: int = 2024):
        if self.player_info.primary_position == 'P':
            file_path = f'{STATCAST_DATA_DIR}/{year}/statcast_data/{self.current_team.abbrev}/pitching/statcast_data_{self.player_bio.full_name.lower().replace(" ", "_")}_{year}.csv'
            PybaseballClient.save_statcast_pitcher_data(self.mlbam_id, year, file_path)
        else:
            file_path = f'{STATCAST_DATA_DIR}/{year}/statcast_data/{self.current_team.abbrev}/batting/statcast_data_{self.player_bio.full_name.lower().replace(" ", "_")}_{year}.csv'
            PybaseballClient.save_statcast_batter_data(self.mlbam_id, year, file_path)
        # statcast_data = MlbStatsClient.fetch_statcast_data(self.mlbam_id, year)
        # if statcast_data is not None:
        #     Utils.save_csv(statcast_data, f"{self.player_bio.full_name}_statcast_{year}.csv")
        # else:
        #     print("No Statcast data available for saving.")
    
    
    def to_json(self):
        """Exports player data to a JSON format"""
        player_data = {
            "mlbam_id": self.mlbam_id,
            "bbref_id": self.bbref_id,
            "team_name": self.current_team.name,  
            "player_bio": self.player_bio.to_json(),
            "player_info": self.player_info.to_json(),
        }
        return player_data

    



        







        
