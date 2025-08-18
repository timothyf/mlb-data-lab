import os
import pandas as pd

from baseball_data_lab.config import DATA_DIR

class LocalDataClient:

    def __init__(self, data_dir: str=DATA_DIR):
        self.data_dir = data_dir
    
    def get_data(self, filename: str) -> pd.DataFrame:
        file_path = os.path.join(self.data_dir, filename)
        if filename.endswith('.json'):
            return pd.read_json(file_path)
        elif filename.endswith('.csv'):
            return pd.read_csv(file_path)
        else:
            raise ValueError("Unsupported file format. Please use a .csv or .json file.")

    def save_data(self, data: pd.DataFrame, filename: str):
        data.to_csv(os.path.join(self.data_dir, filename), index=False)

    def lookup_player(self, last_name: str, first_name: str):
        players = self.get_data('combined_people.csv')
        player = players[(players['name_last'] == last_name) & (players['name_first'] == first_name)]
        return player
    
    def get_statcast_league_pitching(self, season: int):
        return self.get_data(f'statcast_league_pitching_{season}.csv')

    def get_fangraphs_teams(self):
        return self.get_data('fangraphs_teams.csv')
    
    def get_fangraphs_team(self, team_abbrev: str):
        teams = self.get_fangraphs_teams()
        team = teams[teams['teamId'] == team_abbrev]
        return team
    
    def get_current_teams(self):
        return self.get_data('current_teams.json')
    
    def get_current_team(self, team_abbrev: str):
        teams = self.get_current_teams()
        team = teams[teams['teamID'] == team_abbrev]
        return team
