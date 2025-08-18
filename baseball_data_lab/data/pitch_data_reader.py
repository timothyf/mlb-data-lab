import os
from dataclasses import dataclass, field
from typing import List
import pandas as pd

from baseball_data_lab.config import DATA_DIR

@dataclass
class PitchDataReader:
    """Utility class for loading and querying pitch data."""
    csv_path: str = os.path.join(DATA_DIR, "pitch-data-2025-06-18.csv")

    # Column order expected in the CSV
    columns: List[str] = field(default_factory=lambda: (
        "pitcher_id pitcher_name pitch_type count pitch_percent rhh_percent lhh_percent "
        "start_speed max_start_speed ivb hb release_pos_z release_pos_x extension tj_stuff_plus"
    ).split())
    _data: pd.DataFrame | None = None

    def load(self) -> pd.DataFrame:
        """Load the CSV into a pandas DataFrame and validate columns."""
        df = pd.read_csv(self.csv_path)
        if list(df.columns) != self.columns:
            raise ValueError("Unexpected columns in pitch data file")
        self._data = df
        return df

    @property
    def data(self) -> pd.DataFrame:
        if self._data is None:
            return self.load()
        return self._data

    def get_pitcher_data(self, pitcher_id: int) -> pd.DataFrame:
        """Return pitch records for a given pitcher ID."""
        df = self.data
        return df[df["pitcher_id"] == pitcher_id].copy()
