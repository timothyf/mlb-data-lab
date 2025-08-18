# player.py

import logging
from io import BytesIO
from typing import Optional, Dict, Any

from PIL import Image
import math

from baseball_data_lab.team.team import Team
from baseball_data_lab.player.player_bio import PlayerBio
from baseball_data_lab.player.player_lookup import PlayerLookup
from baseball_data_lab.apis.unified_data_client import UnifiedDataClient
from baseball_data_lab.player.player_info import PlayerInfo
from baseball_data_lab.config import STATCAST_DATA_DIR

logger = logging.getLogger(__name__)


class Player:
    def __init__(self, mlbam_id: Optional[int] = None, data_client: Optional[UnifiedDataClient] = None):
        """
        Initializes a Player instance.
        
        :param mlbam_id: MLB Advanced Media ID
        :param data_client: UnifiedDataClient instance; if not provided, a default one is used.
        """
        self.mlbam_id = mlbam_id
        self.bbref_id: Optional[str] = None
        self.player_info: PlayerInfo = PlayerInfo()
        self.player_bio: PlayerBio = PlayerBio() 
        self.current_team: Team = Team(data_client=data_client)
        self.player_stats: Optional[Any] = None
        self.player_splits_stats: Optional[Any] = None
        self.statcast_data: Optional[Any] = None
        self.data_client: UnifiedDataClient = data_client if data_client else UnifiedDataClient()
        self.lookup_client: PlayerLookup = PlayerLookup(data_client=self.data_client)

    def load_stats_for_season(self, season: int) -> None:
        """
        Fetches and sets the player's season statistics.
        """
        if self.player_info.primary_position == 'P':
            self.player_stats = self.data_client.fetch_pitching_stats(
                mlbam_id=self.mlbam_id,
                season=season)
            self.player_splits_stats = self.data_client.fetch_pitching_splits(self.mlbam_id, season=season)
        else:
            self.player_stats = self.data_client.fetch_batting_stats(
                mlbam_id=self.mlbam_id,
                season=season)
            self.player_splits_stats = self.data_client.fetch_batting_splits(self.mlbam_id, season=season)

    def load_statcast_data(self, start_date: str, end_date: str) -> None:
        """
        Fetches and sets the player's Statcast data.
        """
        if self.player_info.primary_position == 'P':
            self.statcast_data = self.data_client.fetch_statcast_pitcher_data(self.mlbam_id, start_date, end_date)
        else:
            self.statcast_data = self.data_client.fetch_statcast_batter_data(self.mlbam_id, start_date, end_date)

    @classmethod
    def create_from_mlb(cls, *, mlbam_id: Optional[int] = None, player_name: Optional[str] = None,
                        data_client: Optional[UnifiedDataClient] = None) -> Optional["Player"]:
        """
        Factory method to create a Player instance using MLBAM ID or player_name.
        """
        player = Player(data_client=data_client)
        if player_name:
            #logger.info(f"Creating player: {player_name}")
            player_data = player.lookup_client.lookup_player(player_name)
            if player_data is None:
                logger.error(f"Could not find player data for: {player_name}")
                return None
            mlbam_id = player_data.get('key_mlbam')
            # If mlbam_id is a list, consider taking the first element.
            if isinstance(mlbam_id, list):
                logger.debug(f"mlbam_id list received: {mlbam_id}")
                mlbam_id = mlbam_id[0]
            bbref_id = player_data.get('key_bbref')
            if not mlbam_id:
                raise ValueError(f"Could not find MLBAM ID for player: {player_name}")

        elif mlbam_id:
            player_data = player.lookup_client.lookup_player(player_id=mlbam_id)
            #logger.info(f"Creating player: {player_data}")
            first = player_data.get('name_first', '').capitalize()
            last = player_data.get('name_last', '').capitalize()
            player_name = f"{first} {last}"
            bbref_id = player_data.get('key_bbref')
            if not player_name:
                raise ValueError(f"Could not find player name for MLBAM ID: {mlbam_id}")
        else:
            raise ValueError("At least one of 'mlbam_id' or 'player_name' must be provided.")

        player.mlbam_id = mlbam_id #cls(mlbam_id, data_client=data_client)
        player.bbref_id = bbref_id
        mlb_player_info = player.data_client.fetch_player_info(mlbam_id)
        player.player_info.set_from_mlb_info(mlb_player_info)
        player.player_bio.set_from_mlb_info(mlb_player_info)
        player.set_team(mlb_player_info)
        return player

    def set_team(self, mlb_player_info: Dict[str, Any]) -> None:
        """
        Sets the current team based on MLB player info.
        """
        team_id = mlb_player_info.get('currentTeam', {}).get('id')
        if team_id:
            self.current_team = Team.create_from_mlb(team_id=team_id, data_client=self.data_client)
        else:
            logger.warning("No current team information available.")

    def get_headshot(self) -> Image.Image:
        """
        Returns the headshot image of the player.
        """
        headshot = self.data_client.fetch_player_headshot(self.mlbam_id)
        img = Image.open(BytesIO(headshot))
        return img
    
    def save_statcast_data(self, year: int = 2024) -> None:
        """
        Saves the player's statcast data to a CSV file based on their position.
        """
        name_slug = self.player_bio.full_name.lower().replace(" ", "_")
        if self.player_info.primary_position == 'P':
            file_path = f'{STATCAST_DATA_DIR}/{year}/statcast_data/{self.current_team.abbrev}/pitching/statcast_data_{name_slug}_{year}.csv'
            self.data_client.save_statcast_pitcher_data(self.mlbam_id, year, file_path)
        else:
            file_path = f'{STATCAST_DATA_DIR}/{year}/statcast_data/{self.current_team.abbrev}/batting/statcast_data_{name_slug}_{year}.csv'
            self.data_client.save_statcast_batter_data(self.mlbam_id, year, file_path)
        logger.info(f"Statcast data saved to {file_path}")
    
    def to_json(self) -> Dict[str, Any]:
        """
        Exports player data to a JSON-friendly dictionary.
        """
        return {
            "mlbam_id": self.mlbam_id,
            "bbref_id": self.bbref_id,
            "team_name": self.current_team.name,  
            "player_bio": self.player_bio.to_json(),
            "player_info": self.player_info.to_json(),
        }
