import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from data.mlb_teams import mlb_teams
from data_fetcher import DataFetcher



class Team:

    def __init__(self, team_id):
        self.team_id = team_id
        self.team_abb = Team.get_team_abbreviation_by_id(self.team_id)

    def get_logo(self):
        logo_url = Team.get_team_logo_url_by_id(self.team_id)
        return DataFetcher.fetch_logo_img(logo_url)
    
    @staticmethod
    def get_team_abbreviation_by_id(team_id):
        for team in mlb_teams:
            if team['team_id'] == team_id:
                return team['abbreviation']
        return None  # If no team is found with the provided team_id
    
    @staticmethod
    def get_team_logo_url_by_id(team_id):
        for team in mlb_teams:
            if team['team_id'] == team_id:
                return team['logo_url']
        return None  # If no team is found with the provided team_id

