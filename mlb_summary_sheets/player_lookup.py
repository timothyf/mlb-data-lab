import pandas as pd
import pybaseball as pyb
import statsapi


class PlayerLookup:

    # This method uses the pybaseball library to lookup a player's MLBAM ID
    @staticmethod
    def lookup_player_id(pitcher_name: str):
        first_name, last_name = pitcher_name.split()
        player_id_df = pyb.playerid_lookup(last_name, first_name)
        if not player_id_df.empty:
            return player_id_df.iloc[0]['key_mlbam']
        else:
            # If fuzzy matching is required
            fuzzy_results = pd.DataFrame(pyb.playerid_lookup(last_name, first_name, fuzzy=True))
            return fuzzy_results
        
    # This method uses the pybaseball library to lookup a player's information
    # information returned includes: 
    #        name_last, name_first, key_mlbam, key_retro, key_bbref, key_fangraphs, mlb_played_first, mlb_played_last
    @staticmethod
    def lookup_player(player_name: str="", player_id: int=None):
        if player_name:
            first_name, last_name = player_name.split()
            player_df = pyb.playerid_lookup(last_name, first_name)
        if player_id:
            player_df = pyb.playerid_reverse_lookup([player_id], key_type='mlbam')
        if not player_df.empty:
            return player_df.iloc[0]
        else:
            # If fuzzy matching is required
            fuzzy_results = pd.DataFrame(pyb.playerid_lookup(last_name, first_name, fuzzy=True))
            return fuzzy_results

    # This method uses the statsapi library to lookup a player's MLBAM ID
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