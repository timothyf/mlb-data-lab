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
    #   https://statsapi.mlb.com/api/v1/people?personIds=669373&season=2024&hydrate=stats(group=[hitting,pitching],type=season,season=2024)
    #   https://statsapi.mlb.com/api/v1/people?personIds=114752&season=1984&hydrate=stats(group=[hitting],type=season,season=1984)
    #   https://statsapi.mlb.com/api/v1/people?personIds=111509&season=1984&hydrate=stats(group=[hitting],type=season,season=1984)
    @staticmethod
    def fetch_player_stats(player_id: int, year: int):
        stats = statsapi.get('people', {'personIds': player_id, 'season': year, 
                                        'hydrate': f'stats(group=[hitting,pitching],type=season,season={year})'}
                            )['people'][0]
        if 'stats' not in stats:
            return None
        return stats['stats'][0]['splits']
    

    # Sample
    #   https://statsapi.mlb.com/api/v1/people?personIds=111509&season=1984&hydrate=stats(group=[],type=season,team,season=1984)
    @staticmethod
    def fetch_player_team(player_id: int, year: int):
        info = statsapi.get('people', {'personIds': player_id, 
                                            'season': year, 
                                            'hydrate': f'stats(group=[],type=season,team,season={year})'
                                })['people'][0]['stats'][0]['splits']

        # Iterate over the elements in info to find the 'team' field
        for element in info:
            if 'team' in element:
                return element['team']
        
        # Return None or handle case if no 'team' is found in any element
        print(f"No team information found for player {player_id} in season {year}.")
        return None


    
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
    def fetch_active_roster(team_id: int = None, team_name: str = None, year: int = 2024):
        if not team_id:
            team_id = MlbStatsClient.get_team_id(team_name)
        active_roster = statsapi.roster(team_id, rosterType='active', season=year)
        return active_roster
    
    def fetch_team_roster(team_id: int, season: int):
        # Fetch the team roster for the given season
        roster_data = statsapi.get('team_roster', {'teamId': team_id, 'season': season})
        
        # Extract player names from the roster data
        players = roster_data['roster']
        player_names = [player['person']['fullName'] for player in players]
        
        return player_names

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
        

    @staticmethod
    def get_season_info(year):
        return statsapi.get('season',{'seasonId':year,'sportId':1})['seasons'][0]   