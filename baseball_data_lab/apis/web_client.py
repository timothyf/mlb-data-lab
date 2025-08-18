import requests
from baseball_data_lab.config import MLB_STATIC_BASE_URL
from PIL import Image
from io import BytesIO

class WebClient:
    
    
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
    
    # https://img.mlbstatic.com/mlb-photos/image/upload/w_800,d_people:generic:action:hero:current.png,q_auto:best,f_auto/v1/people/681481/action/hero/current
    @staticmethod
    def fetch_player_action_shot(player_id: int, width: int = 800):
        url = f'{MLB_STATIC_BASE_URL}'\
            f'upload/w_{width},d_people:generic:action:hero:current.png,q_auto:best,f_auto/v1/people/{player_id}/action/hero/current'
        response = requests.get(url)
        return response.content

    """
    Fetches the MLB daily schedule for a given date.
    :param date: Date in 'YYYY-MM-DD' format.
    :return: JSON response containing the daily schedule.

    https://baseballsavant.mlb.com/schedule?date=2025-6-28
    """
    @staticmethod
    def fetch_daily_schedule(date: str):
        url = f'https://baseballsavant.mlb.com/schedule?date={date}'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch schedule for {date}: {response.status_code}") 
        

    """
    Returns the SVG URL for a given stadium ID.
    :param stadium_id: The ID of the stadium.
    :return: The SVG URL for the stadium.

    https://baseballsavant.mlb.com/site-core/images/fields/2394.svg
    """
    @staticmethod
    def get_stadium_svg(stadium_id: int):
        """
        Returns the SVG URL for a given stadium ID.
        :param stadium_id: The ID of the stadium.
        :return: The SVG for the stadium.

        https://baseballsavant.mlb.com/site-core/images/fields/2394.svg
        """
        if stadium_id is None:
            raise ValueError("Stadium ID cannot be None")
        return 'https://baseballsavant.mlb.com/site-core/images/fields/{stadium_id}.svg'
        
    