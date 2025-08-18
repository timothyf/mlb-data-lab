import numpy as np

from baseball_data_lab.apis.unified_data_client import UnifiedDataClient


class TeamSeasonStats:

    def __init__(self, season: int, data_client: UnifiedDataClient = None):
        self.data_client = data_client if data_client else UnifiedDataClient()
        self.season = season
        self.wins = None
        self.losses = None
        self.runs_scored = None
        self.runs_allowed = None
        self.run_diff = None
        self.win_pct = None
        self.attendance = None
        self.home_attendance = None
        self.avg_game_length = None
        self.batting_stats = None
        self.pitching_stats = None

    def populate(self, team):
        self.fetch_season_record(team)
        self.batting_stats = self.data_client.fetch_team_batting_stats(team.abbrev, self.season, self.season)
        self.pitching_stats = self.data_client.fetch_team_pitching_stats(team.abbrev, self.season, self.season)

    
    def fetch_season_record(self, team):
        season_record = self.data_client.get_team_record_for_season(self.season, team.team_id)
        self.wins = season_record['leagueRecord']['wins']
        self.losses = season_record['leagueRecord']['losses']
        self.win_pct = season_record['leagueRecord']['pct']
        self.runs_scored = season_record['runsScored']
        self.runs_allowed = season_record['runsAllowed']
        self.run_diff = season_record['runDifferential']










