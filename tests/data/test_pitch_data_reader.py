import os
import pandas as pd

from mlb_data_lab.data.pitch_data_reader import PitchDataReader

FIXTURE = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'sample_pitch_data.csv')


def test_load_data():
    reader = PitchDataReader(csv_path=FIXTURE)
    df = reader.load()
    assert list(df.columns) == reader.columns
    assert df.shape[0] == 2


def test_get_pitcher_data():
    reader = PitchDataReader(csv_path=FIXTURE)
    subset = reader.get_pitcher_data(685126)
    assert subset['pitcher_name'].iloc[0] == 'Brandon Eisert'
    assert subset.shape[0] == 1
