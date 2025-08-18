import pandas as pd
import logging
from baseball_data_lab.apis.unified_data_client import UnifiedDataClient
from baseball_data_lab.special_name_mappings import SpecialNameMappings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PlayerLookup:
    def __init__(self, data_client: UnifiedDataClient = None):
        """
        Initialize the PlayerLookup instance.
        Optionally pass a UnifiedDataClient instance; if not provided, one is created.
        Also preprocesses special name mappings for quick lookup.
        """
        self.data_client = data_client if data_client else UnifiedDataClient()
        # Preprocess special mappings into dictionaries (keys in lowercase)
        self.first_name_map = {
            original.lower(): resolved
            for original, resolved in SpecialNameMappings.get('first_name', {}).items()
        }
        self.last_name_map = {
            original.lower(): resolved
            for original, resolved in SpecialNameMappings.get('last_name', {}).items()
        }
        self.player_name_map = {
            original.lower(): player_id
            for original, player_id in SpecialNameMappings.get('player_name', {}).items()
        }

    def parse_full_name(self, player_name: str) -> (str, str):
        """
        Parse a full player name into first name and last name.
        Handles suffixes like Jr., Sr., II, III, or IV.
        Raises ValueError if the name cannot be parsed.
        """
        parts = player_name.split()
        if len(parts) < 2:
            raise ValueError(f"Player name '{player_name}' does not contain enough parts.")
        first_name = parts[0]
        # If the last token is a known suffix and there are at least 3 parts, use the second-to-last token as last name.
        if parts[-1] in ['Jr.', 'Sr.', 'II', 'III', 'IV'] and len(parts) >= 3:
            last_name = parts[-2]
        else:
            last_name = parts[-1]
        return first_name, last_name

    def lookup_player_id(self, player_name: str):
        """
        Lookup a player's MLBAM ID using their pitcher name.
        If multiple entries are returned, a warning is logged.
        If not found, returns the fuzzy search result.
        """
        try:
            first_name, last_name = self.parse_full_name(player_name)
        except ValueError as e:
            logger.error(f"Error parsing name '{player_name}': {e}")
            return None

        player_id_df = self.data_client.lookup_player(last_name, first_name)
        if not player_id_df.empty:
            key_mlbam_value = player_id_df.iloc[0]['key_mlbam']
            if isinstance(key_mlbam_value, list):
                logger.warning(f"Multiple names found for: {player_name}")
            return key_mlbam_value
        else:
            logger.info(f"Player not found: {player_name}. Trying fuzzy matching...")
            fuzzy_results = pd.DataFrame(self.data_client.lookup_player(last_name, first_name, fuzzy=True))
            return fuzzy_results

    def lookup_player(self, player_name: str = "", player_id: int = None):
        """
        Lookup player information either by player name or using an MLBAM ID.
        Returns a Series representing the first row of data if found, otherwise None.
        """
        player_df = pd.DataFrame()
        if player_name:
            try:
                first_name, last_name = self.parse_full_name(player_name)
            except ValueError as e:
                logger.error(f"Error parsing player name '{player_name}': {e}")
                return None

            try:
                player_df = self.data_client.lookup_player(last_name, first_name)
            except Exception as e:
                logger.error(f"Error looking up player {player_name}: {e}")
                return None

            # If no results, try to resolve through special name mappings.
            if player_df.empty:
                player_df, special_id = self.handle_special_cases(first_name, last_name, player_name)
                if special_id is not None:
                    player_id = special_id

        if player_id:
            player_df = self.data_client.lookup_player_by_id(player_id)

        if not player_df.empty:
            # Optionally log a successful lookup.
            #logger.info(f"Player found: {player_df.iloc[0]['name_first']} {player_df.iloc[0]['name_last']}, MLBAM ID: {player_df.iloc[0]['key_mlbam']}")
            return player_df.iloc[0]
        else:
            logger.info(f"No data found for player: {player_name}")
            return None

    def handle_special_cases(self, first_name: str, last_name: str, player_name: str) -> (pd.DataFrame, int):
        """
        Attempts to resolve name issues using preprocessed special name mappings.
        Returns a tuple (player_df, player_id). If a player ID is found, that should be used for further lookup.
        """
        player_df = pd.DataFrame()
        player_id = None

        # As an initial attempt, try constructing a new last name by joining all parts after the first.
        name_parts = player_name.split()
        if len(name_parts) > 2:
            new_last_name = " ".join(name_parts[1:])
            try:
                player_df = self.data_client.lookup_player(new_last_name, first_name)
                if not player_df.empty:
                    return player_df, player_id
            except Exception as e:
                logger.error(f"Error during lookup with new_last_name '{new_last_name}': {e}")

        # Check if a correction exists for the first name.
        new_first = self.first_name_map.get(first_name.lower())
        if new_first:
            try:
                player_df = self.data_client.lookup_player(last_name, new_first)
                if not player_df.empty:
                    #logger.info(f"Resolved first name '{first_name}' to '{new_first}' for player '{player_name}'")
                    return player_df, player_id
            except Exception as e:
                logger.error(f"Error during lookup with corrected first name '{new_first}': {e}")

        # Check if a correction exists for the last name.
        new_last = self.last_name_map.get(last_name.lower())
        if new_last:
            try:
                player_df = self.data_client.lookup_player(new_last, first_name)
                if not player_df.empty:
                    #logger.info(f"Resolved last name '{last_name}' to '{new_last}' for player '{player_name}'")
                    return player_df, player_id
            except Exception as e:
                logger.error(f"Error during lookup with corrected last name '{new_last}': {e}")

        # If a full player name mapping exists, return the associated player ID.
        full_id = self.player_name_map.get(player_name.lower())
        if full_id:
            #logger.info(f"Resolved full player name '{player_name}' to player ID {full_id}")
            return pd.DataFrame(), full_id

        return player_df, player_id
