import pandas as pd
import pybaseball as pyb


class PlayerLookup:

    # This method uses the pybaseball library to lookup a player's MLBAM ID
    @staticmethod
    def lookup_player_id(pitcher_name: str):
        first_name, last_name = pitcher_name.split()
        player_id_df = pyb.playerid_lookup(last_name, first_name)
        if not player_id_df.empty:
            key_mlbam_value = player_id_df.iloc[0]['key_mlbam']
            if isinstance(key_mlbam_value, list):
                print(f"Multiple names found for: {pitcher_name}")
            return key_mlbam_value
        else:
            print(f"Player not found: {pitcher_name}")
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
