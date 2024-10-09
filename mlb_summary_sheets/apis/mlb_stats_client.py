import requests

from mlb_summary_sheets.constants import STATS_API_BASE_URL, MLB_STATIC_BASE_URL


class MlbStatsClient: 

    # Sample
    #   https://statsapi.mlb.com/api/v1/people?personIds=669373&hydrate=currentTeam
    @staticmethod
    def fetch_player_info(player_id: int):
        url = f"{STATS_API_BASE_URL}people?personIds={player_id}&hydrate=currentTeam"
        data = requests.get(url).json()
        return data['people'][0]
    
    @staticmethod
    def fetch_team(team_id: int):
        url = f"{STATS_API_BASE_URL}teams/{team_id}"
        data = requests.get(url).json()
        return data