from mlb_stats.apis.data_fetcher import DataFetcher
from mlb_stats.constants import team_logo_urls
from mlb_stats.apis.mlb_stats_client import MlbStatsClient

class Team:

    def __init__(self):
        self.team_id = None # MLBAM team ID
        self.mlbam_id = None # MLBAM team ID
        self.abbrev = None #mlb_teams[team_id]['abbrev']
        self.name = None # full team name, i.e. Detroit Tigers
        self.location = None # i.e. Detroit, New York, etc.
        self.short_name = None # i.e. Tigers, Yankees, etc.
        self.logo_url = None # URL to team logo
        

    def get_logo(self):
        if self.abbrev not in team_logo_urls:
            return None
        return DataFetcher.fetch_logo_img(team_logo_urls[self.abbrev])
    
    @staticmethod
    def get_team_logo(abbrev: str):
        if abbrev not in team_logo_urls:
            return None
        return DataFetcher.fetch_logo_img(team_logo_urls[abbrev])
    
    def get_short_name(self):
        if self.short_name:
            return self.short_name
        team_name_parts = self.name.split()  
        team_name_suffix = team_name_parts[-1]
        self.short_name = team_name_suffix
        return self.short_name

    @staticmethod
    def create_from_mlb(team_id: int, team_name: str):
        team_data = MlbStatsClient.fetch_team(team_id)
        team = Team()
        team.team_id = team_id
        team.abbrev = team_data.get('abbreviation')
        team.name = team_data.get('name')
        return team

    @staticmethod
    def to_json(self):
        """Exports team data to a JSON format"""
        pass
    


