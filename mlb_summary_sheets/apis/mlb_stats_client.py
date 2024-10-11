import requests
import statsapi

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
        return data.get('teams', {})[0]
    
    # Sample
        #77  2B  Andy Ibáñez
        #4   P   Beau Brieske
        #48  P   Brant Hurter
        #75  P   Brenan Hanifee
        #33  2B  Colt Keith
        #38  C   Dillon Dingler
        #17  3B  Jace Jung
        #21  P   Jackson Jobe
        #34  C   Jake Rogers
        #68  P   Jason Foley
        #44  LF  Justyn-Henry Malloy
        #54  P   Keider Montero
        #30  RF  Kerry Carpenter
        #8   CF  Matt Vierling
        #22  CF  Parker Meadows
        #45  P   Reese Olson
        #31  LF  Riley Greene
        #73  P   Sean Guenther
        #20  1B  Spencer Torkelson
        #29  P   Tarik Skubal
        #27  SS  Trey Sweeney
        #36  P   Ty Madden
        #87  P   Tyler Holton
        #46  RF  Wenceel Pérez
        #19  P   Will Vest
        #39  SS  Zach McKinstry
    @staticmethod
    def fetch_active_roster(team_id: int = None, team_name: str = None):
        if not team_id:
            team_id = MlbStatsClient.get_team_id(team_name)
        active_roster = statsapi.roster(team_id, rosterType='active')
        return active_roster

    @staticmethod
    def get_team_id(team_name):
        teams = statsapi.lookup_team(team_name)
        if teams:
            return teams[0]['id']
        else:
            raise ValueError(f"Team '{team_name}' not found.")
    
    @staticmethod
    def get_player_mlbam_id(player_name):
        # Search for the player using the player's name
        search_results = statsapi.lookup_player(player_name)
        
        # Check if any results are found
        if search_results:
            # Take the first result (or handle multiple results if necessary)
            player_info = search_results[0]
            player_id = player_info['id']
            player_full_name = player_info['fullName']
            print(f"Player Name: {player_full_name}, MLBAM ID: {player_id}")
            return player_id
        else:
            print(f"No player found for name: {player_name}")
            return None