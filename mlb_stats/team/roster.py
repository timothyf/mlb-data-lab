from mlb_stats.team.team import Team
from mlb_stats.apis.mlb_stats_client import MlbStatsClient
from mlb_stats.apis.fangraphs_client import FangraphsClient

class Roster:
    def __init__(self):
        # Initialize self.players as an empty list
        self.players = []

    def add_players(self, players):
        """Add players to the self.players list"""
        if isinstance(players, list):
            self.players.extend(players)  # Add each player in the list to self.players
        else:
            raise ValueError("players should be a list")


    # Gets all players who played for a team in a given season
    @staticmethod
    def get_season_roster(team_id: int = None, team_name: str = None, year: int = 2024):
        roster = []
        if team_id:
            roster = FangraphsClient.fetch_team_players(team_id=team_id, season=year)
        elif team_name:
            team_id = MlbStatsClient.get_team_id(team_name)
            roster = FangraphsClient.fetch_team_players(team_id=team_id, season=year)

        # if team_id:
        #     roster = MlbStatsClient.fetch_active_roster(team_id=team_id, year=year)
        # elif team_name:
        #     roster = MlbStatsClient.fetch_active_roster(team_name=team_name, year=year)

       # print(f"Roster: {roster}")

        # Updated regular expression to handle middle initials, suffixes, and other name variations
       # player_names = re.findall(r'\d+\s+[A-Z0-9]+\s+([A-Za-z\w\s\-\.\']+(?:\s(Jr\.|Sr\.|II|III|IV|V)?)?)', roster)
       # player_names = re.findall(r'\s{2,}[A-Za-z\s\'\.\-]+(?:\s(Jr\.|Sr\.|II|III|IV|V)?)', roster)
       # player_names = re.findall(r'#?\s*[A-Z]+\s+([A-Za-z\'\.\-\s]+(?:\s(Jr\.|Sr\.|II|III|IV|V)?)?)', roster)
       # player_names = re.findall(r'#?\s*[A-Z]+\s+([A-Za-zÁÉÍÓÚáéíóúñÑ\'\.\-\s]+(?:\s(Jr\.|Sr\.|II|III|IV|V)?)?)', roster)

        print(f"Player names: {roster}")

        return roster

        # Extract only the first element (full name) from each tuple and strip whitespace
        #return [name[0].strip() for name in player_names]
