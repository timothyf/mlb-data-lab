from PIL import Image
from io import BytesIO
from mlb_summary_sheets.team import Team
from mlb_summary_sheets.player_bio import PlayerBio
from mlb_summary_sheets.data_fetcher import DataFetcher
from mlb_summary_sheets.player_lookup import PlayerLookup  
import json
from mlb_summary_sheets.utils import Utils

class Player:

    def __init__(self, player_name: str):
        player_data = PlayerLookup.lookup_player(player_name)
        self.player_id = player_data['key_mlbam']
        self.bbref = player_data['key_bbref']
        self.player_info = DataFetcher.fetch_player_info(self.player_id)
        self.team_id = self.get_team_id()
        self.team = Team(self.team_id)
        self.bio = self.create_bio()

    
    def get_team_id(self):
        team_id = self.player_info['people'][0]['currentTeam']['id']
        return team_id


    def get_headshot(self):
        headshot = DataFetcher.fetch_player_headshot(self.player_id)
        img = Image.open(BytesIO(headshot))
        return img


    def create_bio(self):
        player_name = self.player_info['people'][0]['fullName']
        pitcher_hand = self.player_info['people'][0]['pitchHand']['code']
        bats_hand = self.player_info['people'][0]['batSide']['code']
        age = self.player_info['people'][0]['currentAge']
        height = self.player_info['people'][0]['height']
        weight = self.player_info['people'][0]['weight']
        position = self.player_info['people'][0]['primaryPosition']['abbreviation']
        return PlayerBio(player_name, age, height, weight, pitcher_hand, bats_hand, position)
    
    def export_to_json(self):
            """Exports player data to a JSON format"""
            player_data = {
                "player_id": self.player_id,
                "bbref": self.bbref,
                "team_id": self.team_id,
                "team_name": self.team.name,  # Assuming the Team class has a 'name' attribute
                "bio": {
                    "name": self.bio.name,
                    "age": self.bio.age,
                    "height": self.bio.height,
                    "weight": self.bio.weight,
                    "pitcher_hand": self.bio.pitcher_hand,
                    "bats_hand": self.bio.bats_hand,
                    "position": self.bio.position
                },
                "player_info": self.player_info['people']  # Include any additional player info you want
            }
            
            return json.dumps(player_data, indent=4, cls=Utils.NumpyEncoder)
    



        







        
