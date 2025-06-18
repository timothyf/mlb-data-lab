import os
import pandas as pd

from mlb_data_lab.config import DATA_DIR

class PitchData:
    """Load and provide helpers for pitch level Statcast data."""

    def __init__(self, file_name: str = "pitch-data-2025-06-18.csv", data_dir: str = DATA_DIR):
        self.file_path = os.path.join(data_dir, file_name)
        self.data = None

    def load(self) -> pd.DataFrame:
        """Read the CSV file into a DataFrame."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
        self.data = pd.read_csv(self.file_path)
        return self.data

    def _ensure_loaded(self):
        if self.data is None:
            self.load()

    def get_pitch_types(self):
        """Return a list of unique pitch types."""
        self._ensure_loaded()
        if 'pitch_type' in self.data.columns:
            return self.data['pitch_type'].unique().tolist()
        return []

    def pitches_by_pitcher(self, pitcher_id: int) -> pd.DataFrame:
        """Return all pitches thrown by a given pitcher."""
        self._ensure_loaded()
        if 'pitcher' not in self.data.columns:
            raise ValueError("Column 'pitcher' not found in data")
        return self.data[self.data['pitcher'] == pitcher_id]

    def average_release_speed(self, pitcher_id: int = None) -> float:
        """Calculate average release speed, optionally for a specific pitcher."""
        self._ensure_loaded()
        if 'release_speed' not in self.data.columns:
            raise ValueError("Column 'release_speed' not found in data")
        df = self.data
        if pitcher_id is not None:
            if 'pitcher' not in df.columns:
                raise ValueError("Column 'pitcher' not found in data")
            df = df[df['pitcher'] == pitcher_id]
        return df['release_speed'].mean()

    def summary_by_pitch_type(self) -> pd.DataFrame:
        """Return average metrics grouped by pitch type."""
        self._ensure_loaded()
        if 'pitch_type' not in self.data.columns:
            raise ValueError("Column 'pitch_type' not found in data")
        summary_cols = [c for c in ['release_speed', 'release_spin_rate', 'swing', 'whiff'] if c in self.data.columns]
        return self.data.groupby('pitch_type')[summary_cols].mean().reset_index()
