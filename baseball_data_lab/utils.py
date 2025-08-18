import json
import numpy as np
import pandas as pd
import os
from baseball_data_lab.config import DATA_DIR
from baseball_data_lab.config import BASE_DIR
from baseball_data_lab.apis.chadwick_register import PlayerSearchClient
from baseball_data_lab.exceptions.custom_exceptions import NoFangraphsIdError




class Utils:

    @staticmethod
    def get_fangraphs_id(mlbam_id: int, search_client: PlayerSearchClient) -> any:
    
        # Perform the usual lookup first.
        player_data = search_client.playerid_reverse_lookup([mlbam_id], key_type='mlbam').get('key_fangraphs')
        player_fangraphs_id = player_data[0]

        # Check if the result is missing or not valid.
        if player_fangraphs_id in (None, -1, '', 'NA'):
            # try:
                # Load the fallback mapping file.
                mapping_file = os.path.join(BASE_DIR, 'player_id_map.csv')
                mapping = pd.read_csv(mapping_file)
                # Convert the MLBID column to the proper type if needed:
                if mapping['MLBID'].dtype != int:
                    #print(f"MLBID column is not of type int. Converting...")
                    # first filter out value of 'N/A' or 'nan'
                    mapping = mapping[mapping['MLBID'].astype(str) != 'N/A']
                    mapping = mapping[mapping['MLBID'].astype(str) != 'nan']

                    # filter out empty values
                    mapping = mapping[mapping['MLBID'].astype(str) != '']

                    mapping['MLBID'] = mapping['MLBID'].astype(int)
                    # Check if the conversion was successful
                    if mapping['MLBID'].dtype != int:
                        print(f"MLBID column value:s after conversion: {mapping['MLBID'].unique()}")
                        print(f"Conversion failed. MLBID column is still not of type int.")
                        # If conversion fails, return -1 or handle the error as needed.
                        # For now, just return -1
                        # and print a message.
                        return -1
                #mapping['MLBID'] = mapping['MLBID'].astype(int)
                # Search for the row that matches the given mlbam_id.
                row = mapping[mapping['MLBID'] == mlbam_id]
                #print(f"Fallback lookup: mlbam_id {mlbam_id} found in mapping file.")
                if not row.empty:
                    # Retrieve the Fangraphs ID from the appropriate column.
                    player_fangraphs_id = row.iloc[0]['IDFANGRAPHS']
                else:
                    #print(f"Fallback lookup: No mapping found for mlbam_id {mlbam_id}")
                    raise NoFangraphsIdError(f"Invalid Fangraphs ID for player {mlbam_id}.")
            # except Exception as e:
            #     print(f"Error loading fallback mapping: {e}")
        return player_fangraphs_id


    @staticmethod
    def ensure_directory_exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    @staticmethod
    def dump_json(json_str):
        return json.dumps(json_str, indent=4, cls=Utils.NumpyEncoder)

    @staticmethod
    class NumpyEncoder(json.JSONEncoder):
        """ Custom encoder to convert NumPy data types to native Python types """
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()  # Convert NumPy arrays to lists
            else:
                return super(Utils.NumpyEncoder, self).default(obj)
            
    @staticmethod
    def format_stat(value, format_spec: str = None):
        """Function to apply appropriate formatting to a stat."""

        if format_spec is None:
            return value
            
        # Check if the format_spec is a function (e.g., lambda)
        if callable(format_spec):
            return format_spec(value)  # Call the function to format the value

        # Check for percent formatting
        if format_spec == 'percent':
            return f"{value * 100:.1f}%"
        
        # Custom formatting for removing leading zero before the decimal
        if isinstance(format_spec, str) and 'no_leading_zero' in format_spec:
            formatted_value = f"{value:.3f}"  # Format with three decimal places
            return formatted_value.lstrip('0')  # Remove leading zero if present
        
        # Ensure format_spec is a string before using format()
        if isinstance(format_spec, str):
            return format(value, format_spec)
        
        # If format_spec is not a string, raise an error or handle appropriately
        raise TypeError(f"Invalid format_spec: {format_spec}. Expected a string or callable.")


class DataConverter:
    def __init__(self, input_dir: str=DATA_DIR, output_dir: str=DATA_DIR):
        self.input_dir = input_dir
        self.output_dir = output_dir

    def csv_to_json(self, csv_filename: str, json_filename: str):
        # Build file paths
        csv_path = os.path.join(self.input_dir, csv_filename)
        json_path = os.path.join(self.output_dir, json_filename)

        # Read the CSV file
        try:
            df = pd.read_csv(csv_path)
        except FileNotFoundError:
            print(f"CSV file not found: {csv_path}")
            return
        except pd.errors.EmptyDataError:
            print(f"CSV file is empty: {csv_path}")
            return

        # Convert to JSON and save
        df.to_json(json_path, orient="records", lines=True)
        print(f"File converted and saved as JSON: {json_path}")


    def create_current_teams_json(self):
        teams_csv = os.path.join(self.input_dir, 'fangraphs_teams.csv')
        teams_json = os.path.join(self.output_dir, 'current_teams.json')

        # Read the CSV file
        teams_df = pd.read_csv(teams_csv)

        # Filter for teams with yearID of 2021
        teams_df = teams_df[teams_df['yearID'] == 2021]

        # Select specific columns
        teams_df = teams_df[['ID', 'yearID', 'lgID', 'teamID', 'franchID', 'teamIDfg', 'teamIDBR', 'teamIDretro']]
        
        # Save the filtered data to JSON
        teams_df.to_json(teams_json, orient="records", lines=True)
        print(f"Current teams JSON created: {teams_json}")



