from mlb_summary_sheets.apis.data_fetcher import DataFetcher
from mlb_summary_sheets.constants import team_logo_urls
from mlb_summary_sheets.constants import mlb_teams

class Team:

    def __init__(self):
        self.team_id = None
        self.abbrev = None #mlb_teams[team_id]['abbrev']
        self.name = None

    def get_logo(self):
        return DataFetcher.fetch_logo_img(team_logo_urls[self.abbrev])
    


