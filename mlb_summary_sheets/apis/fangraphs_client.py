from mlb_summary_sheets.constants import FANGRAPHS_BASE_URL
import pandas as pd
import requests


class FangraphsClient:

    @staticmethod
    def fetch_leaderboards(season:int, stat_type:str):
        if stat_type == 'pitching':
            return FangraphsClient.fetch_pitching_leaderboards(season)
        elif stat_type == 'batting':
            return FangraphsClient.fetch_batting_leaderboards(season)
        else:
            raise ValueError("Invalid stat_type. Must be 'pitching' or 'batting'")

    @staticmethod
    def fetch_pitching_leaderboards(season:int):
        url = f"{FANGRAPHS_BASE_URL}?age=&pos=all&stats=pit&lg=all&season={season}&season1={season}&ind=0&qual=0&type=8&month=0&pageitems=500000"
        data = requests.get(url).json()
        df = pd.DataFrame(data=data['data'])
        return df
    
    @staticmethod
    def fetch_batting_leaderboards(season:int):
        url = f"{FANGRAPHS_BASE_URL}?age=&pos=all&stats=bat&lg=all&season={season}&season1={season}&ind=0&qual=0&type=8&month=0&pageitems=500000"
        data = requests.get(url).json()
        df = pd.DataFrame(data=data['data'])
        return df #df
    



