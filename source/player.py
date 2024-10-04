from PIL import Image
from io import BytesIO
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.pyplot as plt
import pandas as pd
from team import Team
from player_bio import PlayerBio
from data_fetcher import DataFetcher
from player_lookup import PlayerLookup  


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
        return PlayerBio(player_name, age, height, weight, pitcher_hand, bats_hand, 'Pitcher')







        
