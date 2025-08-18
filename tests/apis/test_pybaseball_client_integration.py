import pytest
import pandas as pd
from baseball_data_lab.apis.pybaseball_client import PybaseballClient

# @pytest.mark.integration
# def test_fetch_team_schedule_and_record_integration():
#     season = 2024
#     team_abbrev = "DET"
#     result = PybaseballClient.fetch_team_schedule_and_record(team_abbrev, season)

#     # For debugging, you can print the result (remove or comment out in production)
#     print(result)

#     # Verify that the result is a DataFrame and contains data.
#     assert isinstance(result, pd.DataFrame), "Expected result to be a pandas DataFrame"
#     assert not result.empty, "Expected DataFrame to contain team schedule and record data"

# @pytest.mark.integration
# def test_fetch_batting_splits_leaderboards_integration():
#     """
#     Integration test for fetch_batting_splits_leaderboards.
#     This test calls the actual pybaseball API.
    
#     Note: This test requires a working internet connection and that the external API
#     returns expected data. It uses a known player's BBRef id and a season with data.
#     """
#     # Known player BBRef id for Mike Trout (example) and a season that should have data.
#     player_bbref = "troutmi01"
#     season = 2019

#     result = PybaseballClient.fetch_batting_splits_leaderboards(player_bbref, season)
    
#     # For debugging, you can print the result (remove or comment out in production)
#     print(result)
    
#     # Verify that the result is a DataFrame and contains data.
#     assert isinstance(result, pd.DataFrame), "Expected result to be a pandas DataFrame"
#     assert not result.empty, "Expected DataFrame to contain batting splits data"

# @pytest.mark.integration
# def test_fetch_batting_splits_leaderboards_integration():
#     player_bbref = "troutmi01"  # or choose a player with known splits data
#     season = 2019
#     result = PybaseballClient.fetch_batting_splits_leaderboards(player_bbref, season)
    
#     # Check that the result is a DataFrame.
#     assert isinstance(result, pd.DataFrame)
    
#     assert not result.empty, "Expected DataFrame to contain batting splits data"
