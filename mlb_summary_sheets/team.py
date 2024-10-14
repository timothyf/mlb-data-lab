from mlb_summary_sheets.apis.data_fetcher import DataFetcher
from mlb_summary_sheets.constants import team_logo_urls
from mlb_summary_sheets.apis.mlb_stats_client import MlbStatsClient

class Team:

    def __init__(self):
        self.team_id = None
        self.abbrev = None #mlb_teams[team_id]['abbrev']
        self.name = None

    def get_logo(self):
        if self.abbrev not in team_logo_urls:
            return None
        return DataFetcher.fetch_logo_img(team_logo_urls[self.abbrev])
    
    def get_short_name(self):
        team_name_parts = self.name.split()  
        team_name_suffix = team_name_parts[-1]
        return team_name_suffix

    @staticmethod
    def create_from_mlb(team_id: int, team_name: str):
        team_data = MlbStatsClient.fetch_team(team_id)
        team = Team()
        team.team_id = team_id
        team.abbrev = team_data.get('abbreviation')
        team.name = team_data.get('name')
        return team

    


