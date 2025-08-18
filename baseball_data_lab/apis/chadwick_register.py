import os
import re
import io
import zipfile
import unicodedata
from difflib import get_close_matches
from typing import List, Tuple, Iterable, Optional

import pandas as pd


class ChadwickRegister:
    """Handles loading and cleaning of the Chadwick register."""

    # Compiled regex to filter out system/hidden files and match people CSV files.
    PEOPLE_FILE_PATTERN = re.compile(r"^(?!__MACOSX).*people.*\.csv$", re.IGNORECASE)

    def __init__(self, register_file: str = 'chadwick-register.csv', zip_file: str = 'chadwick-register.zip'):
        self.register_file = register_file
        self.zip_file = zip_file
        self.lookup_table: Optional[pd.DataFrame] = None

    def _extract_people_files(self, zip_archive: zipfile.ZipFile) -> Iterable[zipfile.ZipInfo]:
        return filter(
            lambda zi: re.search(self.PEOPLE_FILE_PATTERN, zi.filename),
            zip_archive.infolist()
        )

    def _extract_people_table(self, zip_archive: zipfile.ZipFile) -> pd.DataFrame:
        # Read each matching CSV file into a DataFrame and concatenate them vertically.
        dfs = [
            pd.read_csv(io.BytesIO(zip_archive.read(zi.filename)), low_memory=False)
            for zi in self._extract_people_files(zip_archive)
        ]
        return pd.concat(dfs, axis=0)

    def load(self, save: bool = False) -> pd.DataFrame:
        """
        Loads the Chadwick register. If the register file exists locally, it loads it;
        otherwise it extracts the data from the given ZIP file.
        """
        if os.path.exists(self.register_file):
            self.lookup_table = pd.read_csv(self.register_file)
            return self.lookup_table

        print("Gathering player lookup table. This may take a moment.")

        with open(self.zip_file, 'rb') as f:
            zip_data = f.read()

        # Define the columns that are important.
        mlb_only_cols = ['key_retro', 'key_bbref', 'key_fangraphs', 'mlb_played_first', 'mlb_played_last']
        cols_to_keep = ['name_last', 'name_first', 'key_mlbam'] + mlb_only_cols

        with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_archive:
            table = self._extract_people_table(zip_archive).loc[:, cols_to_keep]

        print(f"Cleaning up player lookup table. Found {len(table)} players.")
        table.dropna(how='all', subset=mlb_only_cols, inplace=True)
        table.reset_index(drop=True, inplace=True)

        # Fill missing values in key columns and force proper types.
        table[['key_mlbam', 'key_fangraphs']] = table[['key_mlbam', 'key_fangraphs']].fillna(-1).astype(int)
        table = table[cols_to_keep]

        if save:
            table.to_csv(self.register_file, index=False)

        self.lookup_table = table
        return table

    def get_lookup_table(self, save: bool = False) -> pd.DataFrame:
        """
        Returns the lookup table (loading it if necessary) and normalizes the names
        to lower case for consistency.
        """
        if self.lookup_table is None:
            self.load(save)
        # Normalize names for case‐insensitive search.
        self.lookup_table['name_last'] = self.lookup_table['name_last'].str.lower()
        self.lookup_table['name_first'] = self.lookup_table['name_first'].str.lower()
        return self.lookup_table

    @staticmethod
    def normalize_accents(s: str) -> str:
        """Returns the string with accented characters normalized."""
        return ''.join(c for c in unicodedata.normalize('NFD', str(s)) if unicodedata.category(c) != 'Mn')

    def get_closest_names(self, last: str, first: str) -> pd.DataFrame:
        """
        Uses difflib.get_close_matches to return the five names closest to the full name.
        """
        table = self.get_lookup_table()
        filled_df = table.fillna("").assign(chadwick_name=lambda df: df['name_first'] + " " + df['name_last'])
        fuzzy_matches = pd.DataFrame(
            get_close_matches(f"{first} {last}", filled_df['chadwick_name'], n=5, cutoff=0)
        ).rename({0: "chadwick_name"}, axis=1)
        return fuzzy_matches.merge(filled_df, on="chadwick_name").drop("chadwick_name", axis=1)


class PlayerSearchClient:
    """
    Provides methods to search for player information from the Chadwick register.
    """

    def __init__(self, register: ChadwickRegister):
        self.register = register
        self.table = self.register.get_lookup_table()

    def search(self, last: str, first: Optional[str] = None, fuzzy: bool = False, ignore_accents: bool = False) -> pd.DataFrame:
        """
        Looks up a player by first and last name. If no exact match is found and fuzzy is True,
        returns the five closest matches.
        """
        last = last.lower()
        first = first.lower() if first is not None else None

        if ignore_accents:
            last = self.register.normalize_accents(last)
            if first is not None:
                first = self.register.normalize_accents(first)
            self.table['name_last'] = self.table['name_last'].apply(self.register.normalize_accents)
            self.table['name_first'] = self.table['name_first'].apply(self.register.normalize_accents)

        if first is None:
            results = self.table.loc[self.table['name_last'] == last]
        else:
            results = self.table.loc[(self.table['name_last'] == last) & (self.table['name_first'] == first)]

        results = results.reset_index(drop=True)
        if results.empty and fuzzy and first is not None:
            print("No identically matched names found! Returning the 5 most similar names.")
            results = self.register.get_closest_names(last, first)
        return results

    def search_list(self, player_list: List[Tuple[str, str]]) -> pd.DataFrame:
        """
        Looks up a list of players given as tuples (last, first).
        """
        results = pd.DataFrame()
        for last, first in player_list:
            results = pd.concat([results, self.search(last, first)], ignore_index=True)
        return results

    def reverse_lookup(self, player_ids: List[str], key_type: str = 'mlbam') -> pd.DataFrame:
        """
        Given a list of player IDs and a key type, returns a DataFrame with player information.
        """
        key_types = ('mlbam', 'retro', 'bbref', 'fangraphs')
        if key_type not in key_types:
            raise ValueError(f"[Key Type: {key_type}] Invalid; must be one of {key_types}")
        key = f'key_{key_type}'
        results = self.table[self.table[key].isin(player_ids)]
        return results.reset_index(drop=True)

    # Convenience methods for commonly needed functionality:
    def playerid_lookup(self, last: str, first: Optional[str] = None, fuzzy: bool = False, ignore_accents: bool = False) -> pd.DataFrame:
        return self.search(last, first, fuzzy, ignore_accents)

    def player_search_list(self, player_list: List[Tuple[str, str]]) -> pd.DataFrame:
        return self.search_list(player_list)

    def playerid_reverse_lookup(self, player_ids: List[str], key_type: str = 'mlbam') -> pd.DataFrame:
        return self.reverse_lookup(player_ids, key_type)

# # Example usage:
# if __name__ == "__main__":
#     register = ChadwickRegister()
#     # Load and optionally save the register locally.
#     register.load(save=True)
#     client = PlayerSearchClient(register)
#     # Example search; adjust names as necessary
#     result = client.search("Williams", "john", fuzzy=True, ignore_accents=True)
#     print(result)
