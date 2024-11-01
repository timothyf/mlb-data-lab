import csv
from typing import List, Dict, Optional

class FangraphsTeams:
    def __init__(self, file_path: str):
        # Load data from CSV file
        self.data = self._load_data(file_path)
        # Create indices for faster access
        self.index_by_year = {}
        self.index_by_lgID = {}
        self.index_by_teamID = {}
        
        # Index the data
        for entry in self.data:
            try:
                year = int(entry['yearID'])  # Convert yearID to integer
            except ValueError:
                print(f"Invalid yearID value: {entry['yearID']}")
                continue  # Skip this entry if conversion fails
            
            lgID = entry['lgID']
            teamID = entry['teamID']
            
            if year not in self.index_by_year:
                self.index_by_year[year] = []
            self.index_by_year[year].append(entry)
            
            if lgID not in self.index_by_lgID:
                self.index_by_lgID[lgID] = []
            self.index_by_lgID[lgID].append(entry)
            
            if teamID not in self.index_by_teamID:
                self.index_by_teamID[teamID] = []
            self.index_by_teamID[teamID].append(entry)

    
    def _load_data(self, file_path: str) -> List[Dict]:
        """Load data from a CSV file."""
        try:
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                return [row for row in reader]
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return []
        except csv.Error as e:
            print(f"Error reading CSV file: {file_path}, {e}")
            return []
    
    def get_by_year(self, year: int) -> Optional[List[Dict]]:
        """Retrieve data by year."""
        return self.index_by_year.get(year, None)
    
    def get_by_lgID(self, lgID: str) -> Optional[List[Dict]]:
        """Retrieve data by league ID."""
        return self.index_by_lgID.get(lgID, None)
    
    def get_by_teamID(self, teamID: str) -> Optional[List[Dict]]:
        """Retrieve data by team ID."""
        return self.index_by_teamID.get(teamID, None)


# # Example usage
# # Initialize the FangraphsTeams class with the JSON file path
# fangraphs_teams = FangraphsTeams('fangraphs_teams.json')

# # Access data by year, league ID, or team ID
# print(fangraphs_teams.get_by_year(1876))
# print(fangraphs_teams.get_by_lgID("NL"))
# print(fangraphs_teams.get_by_teamID("BSN"))
