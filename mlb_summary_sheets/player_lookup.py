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
    def lookup_player(player_name: str = "", player_id: int = None):
        player_df = pd.DataFrame()  # Initialize as an empty DataFrame

        if player_name:
            # Split the name into parts based on spaces
            name_parts = player_name.split()

            first_name = name_parts[0]
            
            # # The last name is everything after the first part
            # last_name = " ".join(name_parts[1:])  # Join the remaining parts as the last name
            # The last part is the last name (ignore middle initials)
            last_name = name_parts[-1]
            if last_name == 'Jr.' or last_name == 'Sr.':  # Check for Jr. or Sr. suffix
                last_name = name_parts[-2]

            # Lookup the player by name
            player_df = pyb.playerid_lookup(last_name, first_name)

            if player_df.empty:
                new_last_name = " ".join(name_parts[1:])  # Join the remaining parts as the last name
                print(f"Player not found with first name: {first_name}, last name: {last_name}. Trying with first name {first_name}, last name: {new_last_name}")
                player_df = pyb.playerid_lookup(new_last_name, first_name)

        if player_id:
            # Lookup the player by ID if provided
            player_df = pyb.playerid_reverse_lookup([player_id], key_type='mlbam')

        # Return the first matching row or None if empty
        if not player_df.empty:
            print(f"Player found: {player_df.iloc[0]['name_last']}, {player_df.iloc[0]['name_first']}")
            print(f"MLBAM ID: {player_df.iloc[0]['key_mlbam']}")
            return player_df.iloc[0]
        else:
            return None


            # # If fuzzy matching is required
            # fuzzy_results = pd.DataFrame(pyb.playerid_lookup(last_name, first_name, fuzzy=True))
            # return fuzzy_results
