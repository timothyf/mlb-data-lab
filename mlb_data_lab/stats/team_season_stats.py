import numpy as np

from mlb_data_lab.apis.unified_data_client import UnifiedDataClient


class TeamSeasonStats:

    data_client = UnifiedDataClient()

    def __init__(self, season: int):
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
        self.batting_stats = TeamSeasonStats.data_client.fetch_team_batting_stats(team.abbrev, self.season, self.season)
        self.pitching_stats = TeamSeasonStats.data_client.fetch_team_pitching_stats(team.abbrev, self.season, self.season)

    
    def fetch_season_record(self, team):
        season_record = TeamSeasonStats.data_client.fetch_team_schedule_and_record(team.abbrev, self.season)
        self.wins = np.where(season_record['W/L']=='W', 1, (np.where(season_record['W/L']=='W-wo', 1, 0))).cumsum()[-1]
        self.losses = np.where(season_record['W/L']=='L', 1, (np.where(season_record['W/L']=='L-wo', 1, 0))).cumsum()[-1]
        self.win_pct = f"{(self.wins / (self.wins + self.losses)).round(3):.3f}".lstrip("0")
        self.runs_scored = season_record['R'].sum().astype(int)
        self.runs_allowed = season_record['RA'].sum().astype(int)
        self.run_diff = self.runs_scored - self.runs_allowed
        self.attendance = season_record['Attendance'].sum()
        self.home_attendance= (season_record[season_record['Home_Away'] == 'Home']['Attendance'].dropna().cumsum()).iloc[-1]

        # Calculate average game length
        time_strings = season_record['Time']
        total_minutes = time_strings.apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))
        avg_minutes = total_minutes.mean()
        avg_hours = int(avg_minutes // 60)
        avg_remaining_minutes = int(avg_minutes % 60)
        self.avg_game_length = f"{avg_hours}:{avg_remaining_minutes:02d}"


        #print(season_record.columns)









