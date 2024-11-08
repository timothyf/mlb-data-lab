import pybaseball as pyb
import requests
from mlb_data_lab.constants import STATS_API_BASE_URL, MLB_STATIC_BASE_URL
from PIL import Image
from io import BytesIO

class DataFetcher:
    
    
    @staticmethod
    def fetch_player_headshot(player_id: int):
        url = f'{MLB_STATIC_BASE_URL}'\
            f'upload/d_people:generic:headshot:67:current.png'\
            f'/w_640,q_auto:best/v1/people/{player_id}/headshot/silo/current.png'
        response = requests.get(url)
        return response.content
    
    @staticmethod
    def fetch_logo_img(logo_url: str):
        response = requests.get(logo_url)
        return Image.open(BytesIO(response.content))
