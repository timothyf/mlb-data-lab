from io import BytesIO
from PIL import Image

from mlb_data_lab.team.team import Team
from mlb_data_lab.player.player_bio import PlayerBio
from mlb_data_lab.player.player_lookup import PlayerLookup
from mlb_data_lab.apis.unified_data_client import UnifiedDataClient
from mlb_data_lab.player.player_info import PlayerInfo
from mlb_data_lab.config import STATCAST_DATA_DIR


class Player:

    data_client = UnifiedDataClient()

    def __init__(self, mlbam_id: int):
        self.mlbam_id = mlbam_id
        self.bbref_id = None
        self.player_info = PlayerInfo()
        self.player_bio = PlayerBio() 
        self.current_team = Team()
        self.player_stats = None
        self.player_splits_stats = None
        self.statcast_data = None
        

    def set_player_stats(self, season):
        if self.player_info.primary_position == 'P':
            self.player_stats = Player.data_client.fetch_fangraphs_pitcher_data(player_name=self.player_bio.full_name, team_fangraphs_id=self.current_team.fangraphs_id, start_year=season, end_year=season)
            print(f"Player stats: {self.player_stats}")
            self.player_splits_stats = Player.data_client.fetch_pitching_splits(self.mlbam_id, season=season)
        else:
            self.player_stats = Player.data_client.fetch_fangraphs_batter_data(player_name=self.player_bio.full_name, team_fangraphs_id=self.current_team.fangraphs_id, start_year=season, end_year=season)
            print(f"Player stats: {self.player_stats}")
            self.player_splits_stats = Player.data_client.fetch_batting_splits(self.mlbam_id, season=season)

    def set_statcast_data(self, start_date, end_date):
        if self.player_info.primary_position == 'P':
            self.statcast_data = Player.data_client.fetch_statcast_pitcher_data(self.mlbam_id, start_date, end_date)
        else:
            self.statcast_data = Player.data_client.fetch_statcast_batter_data(self.mlbam_id, start_date, end_date)


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
            player_data = PlayerLookup.lookup_player(player_id = mlbam_id)
            print(f"Creating player: {player_data}")
            player_name = f"{player_data.get('name_first', '').capitalize()} {player_data.get('name_last', '').capitalize()}"
            bbref_id = player_data.get('key_bbref')
            if not player_name:
                raise ValueError(f"Could not find player name for MLBAM ID: {mlbam_id}")

        else:
            # If neither mlbam_id nor player_name is provided, raise an error
            raise ValueError("At least one of 'mlbam_id' or 'player_name' must be provided.")

        # Create a new player instance and populate details
        player = Player(mlbam_id)
        player.bbref_id = bbref_id
        mlb_player_info = Player.data_client.fetch_player_info(mlbam_id)
        player.player_info.set_from_mlb_info(mlb_player_info)
        player.player_bio.set_from_mlb_info(mlb_player_info)
        player.set_team(mlb_player_info)
        return player

    def set_team(self, mlb_player_info):
        team_id = mlb_player_info.get('currentTeam', {}).get('id')
        self.current_team = Team.create_from_mlb(team_id=team_id)

    def get_headshot(self):
        headshot = Player.data_client.fetch_player_headshot(self.mlbam_id)
        img = Image.open(BytesIO(headshot))
        return img
    
    def save_statcast_data(self, year: int = 2024):
        if self.player_info.primary_position == 'P':
            file_path = f'{STATCAST_DATA_DIR}/{year}/statcast_data/{self.current_team.abbrev}/pitching/statcast_data_{self.player_bio.full_name.lower().replace(" ", "_")}_{year}.csv'
            Player.data_client.save_statcast_pitcher_data(self.mlbam_id, year, file_path)
        else:
            file_path = f'{STATCAST_DATA_DIR}/{year}/statcast_data/{self.current_team.abbrev}/batting/statcast_data_{self.player_bio.full_name.lower().replace(" ", "_")}_{year}.csv'
            Player.data_client.save_statcast_batter_data(self.mlbam_id, year, file_path)
        # statcast_data = Player.data_client.fetch_statcast_data(self.mlbam_id, year)
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

    



        







        
