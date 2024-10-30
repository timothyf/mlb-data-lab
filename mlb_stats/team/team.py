from mlb_stats.apis.data_fetcher import DataFetcher
from mlb_stats.constants import team_logo_urls
from mlb_stats.apis.mlb_stats_client import MlbStatsClient
from mlb_stats.team.roster import Roster
from mlb_stats.apis.fangraphs_client import FangraphsClient
from mlb_stats.config import BASE_DIR
from mlb_stats.utils import Utils

class Team:

    def __init__(self):
        self.team_id = None # MLBAM team ID
        self.mlbam_id = None # MLBAM team ID
        self.abbrev = None #mlb_teams[team_id]['abbrev']
        self.name = None # full team name, i.e. Detroit Tigers
        self.location = None # i.e. Detroit, New York, etc.
        self.short_name = None # i.e. Detroit, Toronto, etc.
        self.club_name = None # i.e. Tigers, Blue Jays, etc.
        self.logo_url = None # URL to team logo
        self.season_roster = None # Complete roster for a given season
        

    def get_logo(self):
        if self.abbrev not in team_logo_urls:
            return None
        return DataFetcher.fetch_logo_img(team_logo_urls[self.abbrev])
    
    def set_season_roster(self, season):
        self.season_roster = Roster()
        self.season_roster.players = FangraphsClient.fetch_team_players(team_id=self.mlbam_id, season=season)
    
    def save_season_roster(self, season):
        file_path = f'{BASE_DIR}/output/{season}/{self.club_name}/season_roster.txt'
        Utils.ensure_directory_exists(file_path)
        with open(file_path, "w") as file:
            for line in self.season_roster.players:
                file.write(line + "\n")
    
    @staticmethod
    def get_team_logo(abbrev: str):
        if abbrev not in team_logo_urls:
            return None
        return DataFetcher.fetch_logo_img(team_logo_urls[abbrev])

    @staticmethod
    def create_from_mlb(team_id: int = None, team_name: str = None, season: int = 2024):
        if team_id is None and team_name:
            team_id = MlbStatsClient.get_team_id(team_name)
        team_data = MlbStatsClient.fetch_team(team_id)
        team = Team()
        team.team_id = team_id
        team.mlbam_id = team_data.get('id')
        team.abbrev = team_data.get('abbreviation')
        team.name = team_data.get('name')
        team.short_name = team_data.get('shortName')
        team.club_name = team_data.get('clubName')
        team.location = team_data.get('locationName')
        team.set_season_roster(season)
        return team

    @staticmethod
    def to_json(self):
        """Exports team data to a JSON format"""
        pass
    


