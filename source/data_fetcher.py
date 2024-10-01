import pandas as pd
import pybaseball as pyb
import requests
from constants import STATS_API_BASE_URL, FANGRAPHS_BASE_URL, MLB_STATIC_BASE_URL



class DataFetcher:
    @staticmethod
    def fetch_fangraphs_pitching_leaderboards(season:int):
        url = f"{FANGRAPHS_BASE_URL}?age=&pos=all&stats=pit&lg=all&season={season}&season1={season}&ind=0&qual=0&type=8&month=0&pageitems=500000"
        data = requests.get(url).json()
        df = pd.DataFrame(data=data['data'])
        return df

    @staticmethod
    def fetch_statcast_pitcher_data(pitcher_id: int, start_date: str, end_date: str):
        df_pyb = pyb.statcast_pitcher(start_date, end_date, pitcher_id)
        df_pyb.head()
        return df_pyb
    
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
