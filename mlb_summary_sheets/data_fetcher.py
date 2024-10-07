import pybaseball as pyb
import requests
from mlb_summary_sheets.constants import STATS_API_BASE_URL, MLB_STATIC_BASE_URL
from PIL import Image
from io import BytesIO

class DataFetcher:

    @staticmethod
    def fetch_statcast_pitcher_data(pitcher_id: int, start_date: str, end_date: str):
        df_pyb = pyb.statcast_pitcher(start_date, end_date, pitcher_id)
        df_pyb.head()
        return df_pyb
    
    # Sample
    #   https://statsapi.mlb.com/api/v1/people?personIds=669373&hydrate=currentTeam
    @staticmethod
    def fetch_player_info(player_id: int):
        url = f"{STATS_API_BASE_URL}people?personIds={player_id}&hydrate=currentTeam"
        data = requests.get(url).json()
        return data
    
    @staticmethod
    def fetch_player_headshot(player_id: int):
        url = f'{MLB_STATIC_BASE_URL}'\
            f'upload/d_people:generic:headshot:67:current.png'\
            f'/w_640,q_auto:best/v1/people/{player_id}/headshot/silo/current.png'
        response = requests.get(url)
        return response.content
    
    @staticmethod
    def fetch_team(team_id: int):
        url = f"{STATS_API_BASE_URL}teams/{team_id}"
        data = requests.get(url).json()
        return data
    
    @staticmethod
    def fetch_logo_img(logo_url: str):
        response = requests.get(logo_url)
        return Image.open(BytesIO(response.content))
