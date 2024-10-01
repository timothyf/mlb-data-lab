import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from constants import mlb_teams
from data_fetcher import DataFetcher



class Team:

    def __init__(self, team_id):
        self.team_id = team_id
        self.team_info = DataFetcher.fetch_team(self.team_id)['teams'][0]
        self.team_abb = self.get_abbrev()


    def get_abbrev(self):
        return self.team_info['abbreviation']

    def get_logo(self):
        # Get the logo URL from the image dictionary using the team abbreviation
        df_image = pd.DataFrame(mlb_teams)
        image_dict = df_image.set_index('team')['logo_url'].to_dict()
        logo_url = image_dict[self.team_abb]

        response = requests.get(logo_url)
        return Image.open(BytesIO(response.content))
