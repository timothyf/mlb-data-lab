import os
from typing import Optional

from mlb_data_lab.constants import team_logo_urls
from mlb_data_lab.team.roster import Roster
from mlb_data_lab.apis.unified_data_client import UnifiedDataClient
from mlb_data_lab.config import BASE_DIR
from mlb_data_lab.utils import Utils
from mlb_data_lab.data.fangraphs_teams import FangraphsTeams
from mlb_data_lab.config import DATA_DIR
from mlb_data_lab.stats.team_season_stats import TeamSeasonStats

import warnings
warnings.filterwarnings("ignore", category=FutureWarning, message="A value is trying to be set on a copy of a DataFrame or Series through chained assignment")

class Team:

    def __init__(self, data_client: Optional[UnifiedDataClient] = None):
        self.data_client: UnifiedDataClient = data_client if data_client else UnifiedDataClient()
        self.team_id = None # MLBAM team ID
        self.mlbam_id = None # MLBAM team ID
        self.fangraphs_id = None # Fangraphs team ID
        self.abbrev = None #mlb_teams[team_id]['abbrev']
        self.name = None # full team name, i.e. Detroit Tigers
        self.location = None # i.e. Detroit, New York, etc.
        self.short_name = None # i.e. Detroit, Toronto, etc.
        self.club_name = None # i.e. Tigers, Blue Jays, etc.
        self.logo_url = None # URL to team logo
        self.season_roster = None # Complete roster for a given season
        self.season_stats = None # Team stats for a given season
        

    def get_logo(self):
        if self.abbrev not in team_logo_urls:
            return None
        return self.data_client.fetch_logo_img(team_logo_urls[self.abbrev])
    
    def set_season_roster(self, season):
        self.season_roster = Roster()
        self.season_roster.players = self.data_client.fetch_team_players(team_id=self.mlbam_id, season=season)

    def populate_season_stats(self, season):
        self.season_stats = TeamSeasonStats(season)
        self.season_stats.populate(self)

    def populate_season_batting_stats(self, season):
        self.season_batting_stats = self.data_client.fetch_team_batting_stats(self.abbrev, season, season)

    def populate_season_pitching_stats(self, season):
        self.season_pitching_stats = self.data_client.fetch_team_pitching_stats(self.abbrev, season, season)

    def save_season_roster(self, season):
        file_path = f'{BASE_DIR}/output/{season}/{self.club_name}/season_roster.txt'
        Utils.ensure_directory_exists(file_path)
        with open(file_path, "w") as file:
            for line in self.season_roster.players:
                file.write(line + "\n")

    def set_fangraphs_id(self):
        teams = FangraphsTeams(os.path.join(DATA_DIR, 'fangraphs_teams.csv'))
        team = teams.get_by_teamID(self.abbrev)
        if team is None:
            return
        team = team[-1]
        self.fangraphs_id = team['teamIDfg']
    

    def get_team_logo(self, abbrev: str):
        if abbrev not in team_logo_urls:
            return None
        return self.data_client.fetch_logo_img(team_logo_urls[abbrev])

    @staticmethod
    def create_from_mlb(team_id: int = None, team_name: str = None, season: int = 2024, data_client: Optional[UnifiedDataClient] = None):
        if team_id is None and team_name is None:
            raise ValueError("Either team_id or team_name must be provided.")
        data_client = UnifiedDataClient = data_client if data_client else UnifiedDataClient()
        team = Team(data_client=data_client)
        if team_id is None and team_name:
            team_id = data_client.get_team_id(team_name)
        team_data = data_client.fetch_team(team_id)
        team.team_id = team_id
        team.mlbam_id = team_data.get('id')
        team.abbrev = team_data.get('abbreviation')
        team.name = team_data.get('name')
        team.short_name = team_data.get('shortName')
        team.club_name = team_data.get('clubName')
        team.location = team_data.get('locationName')
        team.set_season_roster(season)
        team.set_fangraphs_id()
        return team

    @staticmethod
    def to_json(self):
        """Exports team data to a JSON format"""
        pass
    


