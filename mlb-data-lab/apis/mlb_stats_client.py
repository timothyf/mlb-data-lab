import requests
import statsapi
import json

from mlb_stats.constants import STATS_API_BASE_URL


class MlbStatsClient: 

    # Sample
    #   https://statsapi.mlb.com/api/v1/people?personIds=669373&hydrate=currentTeam
    @staticmethod
    def fetch_player_info(player_id: int):
        url = f"{STATS_API_BASE_URL}people?personIds={player_id}&hydrate=currentTeam"
        data = requests.get(url).json()
        return data['people'][0]
    
    # Sample
    #   https://statsapi.mlb.com/api/v1/teams/116
    @staticmethod
    def fetch_team(team_id: int):
        url = f"{STATS_API_BASE_URL}teams/{team_id}"
        data = requests.get(url).json()
        return data.get('teams', {})[0]
    
    # Sample
    #   https://statsapi.mlb.com/api/v1/people?personIds=669373&season=2024&hydrate=stats(group=[hitting,pitching],type=season,season=2024)
    #   https://statsapi.mlb.com/api/v1/people?personIds=114752&season=1984&hydrate=stats(group=[hitting],type=season,season=1984)
    #   https://statsapi.mlb.com/api/v1/people?personIds=111509
    #           &season=1984
    #           &hydrate=stats(group=[hitting],
    #           type=season,
    #           season=1984)
    @staticmethod
    def fetch_player_stats(player_id: int, year: int):
        stats = statsapi.get('people', {'personIds': player_id, 'season': year, 
                                        'hydrate': f'stats(group=[hitting,pitching],type=season,season={year})'}
                            )['people'][0]
        if 'stats' not in stats:
            return None
        return stats['stats'][0]['splits']
    
    # Sample
    # https://statsapi.mlb.com/api/v1/people/656427?hydrate=team,
    #       stats(type=[season,seasonBasic,seasonAdvanced,availableStats](team(league)),
    #       leagueListId=mlb_hist,
    #       season=2024)
    #   https://statsapi.mlb.com/api/v1/people/656427?hydrate=team,stats(type=[season,seasonBasic,seasonAdvanced,availableStats](team(league)),leagueListId=mlb_hist,season=2024)
    @staticmethod
    def fetch_player_stats_by_season(player_id: int, year: int):
        url = f"https://statsapi.mlb.com/api/v1/people/{player_id}?hydrate=team,stats(type=[season,seasonBasic,seasonAdvanced,availableStats](team(league)),leagueListId=mlb_hist,season={year})"
        response = requests.get(url)

        if response.status_code == 200:
            # Parse JSON data from response
            data = response.json()
            
            # Initialize the structure for combined data
            combined_data = {
                "player_id": player_id,
                "season_stats": {}
            }
            
            # Process each person in the data
            for person in data.get('people', []):
                # Filter by matching player_id only
                if person['id'] == player_id:
                    for stat_group in person['stats']:
                        if stat_group['type']['displayName'] in ['season', 'seasonAdvanced']:
                            for split in stat_group['splits']:
                                # Check for season total stats (without team info)
                                if 'team' not in split and split['season'] == str(year):
                                    season_stats = combined_data["season_stats"].setdefault("season", {})
                                    season_stats.update(split['stat'])

                                    # Calculate BB% if walks and plate appearances are available
                                    if 'baseOnBalls' in season_stats and 'plateAppearances' in season_stats:
                                        bb_percent = (season_stats['baseOnBalls'] / season_stats['plateAppearances']) * 100
                                        season_stats['BB%'] = round(bb_percent, 2)

                                    # Calculate K% if strikeouts and plate appearances are available
                                    if 'strikeOuts' in season_stats and 'plateAppearances' in season_stats:
                                        k_percent = (season_stats['strikeOuts'] / season_stats['plateAppearances']) * 100
                                        season_stats['K%'] = round(k_percent, 2)

                                # Check for team-specific stats
                                elif 'team' in split and split['season'] == str(year):
                                    team_name = split['team']['teamName'].lower()
                                    team_entry = combined_data["season_stats"].setdefault(team_name, {})
                                    team_entry.update(split['stat'])

                                    # Calculate BB% for team stats if available
                                    if 'baseOnBalls' in team_entry and 'plateAppearances' in team_entry:
                                        bb_percent = (team_entry['baseOnBalls'] / team_entry['plateAppearances']) * 100
                                        team_entry['BB%'] = round(bb_percent, 2)

                                    # Calculate K% if strikeouts and plate appearances are available
                                    if 'strikeOuts' in team_entry and 'plateAppearances' in team_entry:
                                        k_percent = (team_entry['strikeOuts'] / team_entry['plateAppearances']) * 100
                                        team_entry['K%'] = round(k_percent, 2)

            return combined_data
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")




    

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
    
    @staticmethod
    def fetch_team_roster(team_id: int, season: int):
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
        
    # Sample
    #   https://statsapi.mlb.com/api/v1/seasons/2024?sportId=1
    @staticmethod
    def get_season_info(year):
        return statsapi.get('season',{'seasonId':year,'sportId':1})['seasons'][0]   