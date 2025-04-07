# tests/apis/test_mlb_stats_client_integration.py

import pytest
from mlb_data_lab.apis.mlb_stats_client import MlbStatsClient
import pandas as pd

@pytest.mark.integration
def test_fetch_player_stats_integration():
    """
    Integration test for MlbStatsClient.fetch_player_stats.

    This test calls the live Stats API to retrieve season stats splits for a known player.
    It uses Mike Trout's numeric player ID (commonly 545361) and a season with data.
    Note: This test requires a working internet connection and depends on external API responses.
    """
    # Known player id for Mike Trout; adjust if needed.
    player_id = 545361
    season = 2019

    result = MlbStatsClient.fetch_player_stats(player_id, season)
    
    # Assert that the result is not None and is a list.
    assert result is not None, "Expected non-None splits data for player stats."
    assert isinstance(result, list), "Expected splits data to be returned as a list."

    # For each split, check that:
    # - The split is a dictionary.
    # - It contains the keys 'season' and 'stat'.
    # - The 'stat' value is a dictionary with non-None (and if numeric, non-negative) values.
    for split in result:
        assert isinstance(split, dict), "Each split should be a dictionary."
        expected_keys = ['season', 'stat']
        for key in expected_keys:
            assert key in split, f"Expected key '{key}' in split: {split}"
        
        # Ensure that the 'stat' field is a dictionary.
        stat_data = split['stat']
        assert isinstance(stat_data, dict), "The 'stat' field should be a dictionary."
        
        # Check that each stat value is not None. Optionally, if numeric, it should be non-negative.
        for stat_key, value in stat_data.items():
            assert value is not None, f"Stat '{stat_key}' in split {split} is None."
            # If the value is numeric, check that it is not negative.
            try:
                numeric_value = float(value)
                assert numeric_value >= 0, f"Stat '{stat_key}' in split {split} is negative."
            except (ValueError, TypeError):
                # If the value cannot be converted to float, skip the numeric check.
                pass



@pytest.mark.integration
def test_fetch_batter_stat_splits_integration():
    """
    Integration test for MlbStatsClient.fetch_player_stat_splits using sample data for Riley Greene.
    """
    # Use Riley Greene's player id and season 2024.
    player_id = 682985
    season = 2024

    splits = MlbStatsClient.fetch_batter_stat_splits(player_id, season)

    # Basic assertions.
    assert splits is not None, "Expected non-None stat splits for player stats."
    assert isinstance(splits, pd.DataFrame), "Expected result to be a pandas DataFrame"
    assert len(splits) == 2, f"Expected 2 hitting splits, got {len(splits)} splits."

    # Define expected keys for every split.
    expected_keys = [
        'gamesPlayed'
    ]

    # Expected values for the "vl" split.
    expected_first = {
        "gamesPlayed": 84
    }

    # Expected values for the "vr" split.
    expected_second = {
         "gamesPlayed": 131
     }
    
    def check_split(split, expected):
        # Convert the namedtuple row to a dictionary.
        split_dict = split._asdict()
        # Remove the 'Index' key since it comes from the MultiIndex.
        split_dict.pop('Index', None)
        # For each expected key, check that it exists and its value matches.
        for key in expected_keys:
            assert key in split_dict, f"Expected key '{key}' in split row: {split_dict}"
            #assert split_dict[key] == exp_value, f"Expected key '{key}' to have value {exp_value}, got {split_dict[key]}"

        # Explicitly check for the value of 'gamesPlayed'
        for key in expected:
            expected_value = expected[key]
            actual_value = split_dict.get(key)
            assert actual_value == expected_value, f"Expected gamesPlayed to be {expected_value}, got {actual_value}"


    split_names = splits.index.get_level_values('Split')
    # Check that the split names are as expected.
    assert len(split_names) == 2, f"Expected 2 splits, got {len(split_names)}"
    assert "vl" in split_names, f"Expected 'vs Left' split, got {split_names}"
    assert "vr" in split_names, f"Expected 'vs Right' split, got {split_names}"

    # Iterate over the splits and verify expected values.
    for i, split in enumerate(splits.itertuples()):
        if i == 0:
            check_split(split, expected_first)
        elif i == 1:
            check_split(split, expected_second)
        else:
            pytest.fail(f"Unexpected split index: {i}")


