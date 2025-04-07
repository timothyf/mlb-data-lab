import pytest
import pandas as pd
from mlb_data_lab.player.player import Player

@pytest.mark.integration
def test_set_player_stats_integration():
    """
    Integration test for Player.set_player_stats.

    This test creates a Player instance for a known MLB player using create_from_mlb,
    calls set_player_stats for a given season, and asserts that the player's
    stats properties are populated with non-empty data structures.
    
    NOTE: This test requires an active internet connection and that the external
    APIs (pybaseball and MLB Stats API) return expected data.
    """
    # Use a known MLBAM ID for a well-known player (for example, Mike Trout)
    mlbam_id = 545361  # Adjust if needed
    season = 2023

    # Create the Player instance via create_from_mlb
    player = Player.create_from_mlb(mlbam_id=mlbam_id)
    assert player is not None, "Failed to create player instance via create_from_mlb"

    # Ensure required attributes were set.
    assert hasattr(player.player_info, "primary_position"), "Player primary_position not set"
    assert player.bbref_id is not None, "Player bbref_id not set"
    
    # Call set_player_stats which should fetch and populate stats based on the player's position.
    player.set_player_stats(season)
    
    # Verify that the player's stats properties have been populated.
    assert player.player_standard_stats is not None, "Standard stats not set"
    assert player.player_advanced_stats is not None, "Advanced stats not set"
    assert player.player_splits_stats is not None, "Splits stats not set"
    
    # Additional checks on standard stats.
    print(f"Standard stats type: {type(player.player_standard_stats)}")
    if isinstance(player.player_standard_stats, dict):
        assert bool(player.player_standard_stats), "Standard stats dict is empty"
        stats_df = pd.DataFrame([player.player_standard_stats])
        assert not stats_df.empty, "Standard stats DataFrame is empty"
        common_columns = ['AB', 'H', 'AVG', 'RBI']
        missing_cols = [col for col in common_columns if col not in stats_df.columns]
        assert not missing_cols, f"Missing expected columns in standard stats: {missing_cols}"
    elif isinstance(player.player_standard_stats, list):
        assert len(player.player_standard_stats) > 0, "Standard stats list is empty"
    elif isinstance(player.player_standard_stats, pd.DataFrame):
        assert not player.player_standard_stats.empty, "Standard stats DataFrame is empty"
    
    # Verify that advanced stats match standard stats per our implementation.
    print(f"Advanced stats type: {type(player.player_advanced_stats)}")
    assert player.player_advanced_stats == player.player_standard_stats, "Advanced stats differ from standard stats"
    
    # Additional checks on splits stats.
    print(f"Splits stats type: {type(player.player_splits_stats)}")
    if isinstance(player.player_splits_stats, dict):
        assert bool(player.player_splits_stats), "Splits stats dict is empty"
        stats_df = pd.DataFrame([player.player_splits_stats])
        assert not stats_df.empty, "Splits stats DataFrame is empty"
        common_columns = ['AB', 'H', 'AVG', 'RBI']
        missing_cols = [col for col in common_columns if col not in stats_df.columns]
        assert not missing_cols, f"Missing expected columns in splits stats: {missing_cols}"
    elif isinstance(player.player_splits_stats, list):
        assert len(player.player_splits_stats) > 0, "Splits stats list is empty"
    elif isinstance(player.player_splits_stats, pd.DataFrame):
        assert not player.player_splits_stats.empty, "Splits stats DataFrame is empty"
        # Optionally, check for some common expected columns (e.g., AB, H, AVG)
        common_columns = ["gamesPlayed", "groundOuts", "airOuts", "doubles", "triples", "homeRuns", "strikeOuts"]
        missing_cols = [col for col in common_columns if col not in player.player_splits_stats.columns]
        assert not missing_cols, f"Missing expected columns in splits stats: {missing_cols}"
