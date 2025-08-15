# tests/apis/test_fangraphs_client_integration.py


import os
import pandas as pd
import pytest
from mlb_data_lab.apis.fangraphs_client import FangraphsClient
import re


@pytest.mark.integration
def test_fangraphs_client_integration():
    client = FangraphsClient()
    assert client is not None
    # Add more integration tests here


def test_fetch_player_stats_integration():
    """
    Integration test for FangraphsClient.fetch_player_stats.
    This test calls the live Fangraphs API to retrieve player stats.
    Note: This test requires a working internet connection and depends on external API responses.
    """
    # Example player ID, season, team ID, and stat type
    player_fangraphs_id = 22267  # Tarik Skubal
    season = 2024 
    fangraphs_team_id = None  # No specific team filter
    stat_type = 'pitching'  # Example stat type

    result = FangraphsClient.fetch_player_stats(player_fangraphs_id, season, fangraphs_team_id, stat_type)

    assert isinstance(result, pd.DataFrame), "Expected a DataFrame as the result."
    assert not result.empty, "Expected non-empty DataFrame for player stats."

    # Additional assertions can be added here to validate the contents of the DataFrame
    assert 'Name' in result.columns, "Expected 'player_name' column in the DataFrame."
    assert 'Season' in result.columns, "Expected 'season' column in the DataFrame."
    assert 'Team' in result.columns, "Expected 'team' column in the DataFrame."
    assert 'Age' in result.columns, "Expected 'age' column in the DataFrame."

    name_clean = re.sub(r'<[^>]+>', '', str(result['Name'].iloc[0])).strip()
    assert name_clean == 'Tarik Skubal', "Expected player name to be 'Tarik Skubal'."
    assert result['Season'].iloc[0] == 2024, "Expected season to be 2024."
    team_clean = re.sub(r'<[^>]+>', '', str(result['Team'].iloc[0])).strip()
    assert team_clean == 'DET', "Expected team to be 'DET'."
    assert result['Age'].iloc[0] == 27, "Expected age to be 27."


def test_fetch_player_stats_multi_team_integration():
    """
    Integration test for a player who appeared for multiple teams in 2024; Team should be '---'.
    """
    player_fangraphs_id = 17479 # Jack Flaherty
    season = 2024
    fangraphs_team_id = None

    df = FangraphsClient.fetch_player_stats(player_fangraphs_id, season, fangraphs_team_id, 'pitching')
    if not isinstance(df, pd.DataFrame) or df.empty:
        df = FangraphsClient.fetch_player_stats(player_fangraphs_id, season, fangraphs_team_id, 'batting')

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert {'Name', 'Season', 'Team'}.issubset(df.columns)

    name_clean = re.sub(r'<[^>]+>', '', str(df['Name'].iloc[0])).strip()
    assert name_clean == 'Jack Flaherty', "Expected player name to be 'Jack Flaherty'."
    assert int(df['Season'].iloc[0]) == season
    team_clean = re.sub(r'<[^>]+>', '', str(df['Team'].iloc[0])).strip()
    assert team_clean == '- - -'


