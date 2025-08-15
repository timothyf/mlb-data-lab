# tests/apis/test_mlb_stats_client_integration.py

import pytest
from mlb_data_lab.apis.mlb_stats_client import MlbStatsClient
import pandas as pd


@pytest.mark.integration
def test_fetch_player_info():
    """
    Integration test for MlbStatsClient.fetch_player_info.
    """
    player_id = 669373  # Tarik Skubal
    result = MlbStatsClient.fetch_player_info(player_id)

    # Assert that the result is not None and contains expected keys.
    assert result is not None, "Expected non-None player info."
    expected_keys = ['id', 'firstName', 'lastName', 'primaryNumber', 'birthDate', 
                     'currentAge', 'currentTeam', 'primaryPosition', 'batSide',
                     'pitchHand']
    for key in expected_keys:
        assert key in result, f"Expected key '{key}' in player info."

    assert result['id'] == player_id, f"Expected player ID {player_id}, got {result['id']}."
    assert result['firstName'] == "Tarik", f"Expected first name 'Tarik', got {result['firstName']}."
    assert result['lastName'] == "Skubal", f"Expected last name 'Skubal', got {result['lastName']}."
    assert result['primaryNumber'] == "29", f"Expected primary number '29', got {result['primaryNumber']}."
    assert result['birthDate'] == "1996-11-20", f"Expected birth date '1996-11-20', got {result['birthDate']}."
    assert result['currentTeam']['name'] == "Detroit Tigers", f"Expected current team 'Detroit Tigers', got {result['currentTeam']}."
    assert result['primaryPosition']['name'] == "Pitcher", f"Expected primary position 'Pitcher', got {result['primaryPosition']}."
    assert result['batSide']['description'] == "Right", f"Expected bat side 'Left', got {result['batSide']}."
    assert result['pitchHand']['description'] == "Left", f"Expected pitch hand 'Left', got {result['pitchHand']}."


@pytest.mark.integration
def test_fetch_team_integration():
    """
    Integration test for MlbStatsClient.fetch_team_info.
    """
    team_id = 116  # Detroit Tigers
    result = MlbStatsClient.fetch_team(team_id)

    # Assert that the result is not None and contains expected keys.
    assert result is not None, "Expected non-None team info."
    expected_keys = ['id', 'name', 'venue', 'teamCode', 'abbreviation', 'teamName',
                     'locationName']
    for key in expected_keys:
        assert key in result, f"Expected key '{key}' in team info."

    assert result['id'] == team_id, f"Expected team ID {team_id}, got {result['id']}."
    assert result['name'] == "Detroit Tigers", f"Expected team name 'Detroit Tigers', got {result['name']}."
    assert result['venue']['name'] == "Comerica Park", f"Expected venue 'Comerica Park', got {result['venue']['name']}."


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
def test_fetch_player_stats_by_season_integration():
    """Integration test for MlbStatsClient.fetch_player_stats_by_season (refactored shape)."""

    # --- Case 1: Single-team season (Mike Trout, 2019) ---
    player_id = 545361  # Mike Trout
    season = 2019

    result = MlbStatsClient.fetch_player_stats_by_season(player_id, season)

    # Basic structure checks
    assert isinstance(result, dict)
    assert result.get("player_id") == player_id
    assert "season" in result and isinstance(result["season"], dict)
    assert "teams" in result and isinstance(result["teams"], dict)
    assert "team_ids" in result and isinstance(result["team_ids"], list)

    # At least one team entry should exist and be well-formed
    assert len(result["team_ids"]) >= 1
    for tid in result["team_ids"]:
        assert tid in result["teams"], f"team_id {tid} missing from teams map"
        team_entry = result["teams"][tid]
        assert isinstance(team_entry, dict)
        # team metadata
        assert "teamId" in team_entry
        assert "teamName" in team_entry
        assert "abbrev" in team_entry
        # stats bucket
        assert "stats" in team_entry and isinstance(team_entry["stats"], dict)

    # Optional: sanity checks on aggregate season bucket (keys presence, types)
    # (Avoid brittle checks on exact values; just assert dict-like contents)
    assert isinstance(result["season"], dict)

    # --- Case 2: Multi-team season (Jack Flaherty, 2024) ---
    player_id = 656427  # Jack Flaherty
    season = 2024

    result = MlbStatsClient.fetch_player_stats_by_season(player_id, season)

    # Structure checks again
    assert isinstance(result, dict)
    assert result.get("player_id") == player_id
    assert "season" in result and isinstance(result["season"], dict)
    assert "teams" in result and isinstance(result["teams"], dict)
    assert "team_ids" in result and isinstance(result["team_ids"], list)

    # Expect multiple teams (was traded during 2024)
    assert len(result["team_ids"]) >= 2, (
        f"Expected >=2 teams for player {player_id} in {season}, got {len(result['team_ids'])}"
    )

    # Validate each team entry has a stats bucket
    for tid in result["team_ids"]:
        team_entry = result["teams"][tid]
        assert isinstance(team_entry.get("stats"), dict)
        # Optional: presence of a few common numeric stats if available
        # (don’t fail if missing—API fields can vary by group/type)
        # e.g., gamesPlayed/gamesPitched may or may not be present depending on group
        # So we just ensure dict-ness and leave content checks to unit tests against fixtures.


"""Integration test for MlbStatsClient.get_player_teams_for_season against live API."""
@pytest.mark.integration
def test_get_player_teams_for_season_integration():
    # Likely single-team season
    trout_2019 = MlbStatsClient.get_player_teams_for_season(545361, 2019)  # Mike Trout
    assert isinstance(trout_2019, list)
    assert len(trout_2019) >= 1
    assert all(
        isinstance(t.get("teamId"), (int, str)) and isinstance(t.get("teamName"), str)
        for t in trout_2019
    ), "Each team entry should have teamId and teamName"

    # Known multi-team season (trade year)
    flaherty_2024_ids = MlbStatsClient.get_player_teams_for_season(656427, 2024, ids_only=True)
    assert isinstance(flaherty_2024_ids, list)
    assert len(flaherty_2024_ids) >= 2, "Expected multi-team season for 2024"
    assert all(isinstance(tid, (int, str)) for tid in flaherty_2024_ids)


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
    assert len(splits) == 4, f"Expected 4 hitting splits, got {len(splits)} splits."

    # Define expected keys for every split.
    expected_keys = [
        'gamesPlayed'
    ]

    # Expected values for the "vl" split.
    expected_first = {
        "gamesPlayed": 66
    }

    # Expected values for the "vr" split.
    expected_second = {
         "gamesPlayed": 71
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
    assert len(split_names) == 4, f"Expected 4 splits, got {len(split_names)}"
    assert "vl" in split_names, f"Expected 'vs Left' split, got {split_names}"
    assert "vr" in split_names, f"Expected 'vs Right' split, got {split_names}"
    assert("h" in split_names), f"Expected 'Home' split, got {split_names}"
    assert("a" in split_names), f"Expected 'Away' split, got {split_names}"

    # Iterate over the splits and verify expected values.
    for i, split in enumerate(splits.itertuples()):
        if i == 0:
            check_split(split, expected_first)
        elif i == 1:
            check_split(split, expected_second)
        elif i == 2:
            pass
        elif i == 3:
            pass
        else:
            pytest.fail(f"Unexpected split index: {i}")


@pytest.mark.integration
def test_fetch_pitcher_stat_splits_integration():
    """
    Integration test for MlbStatsClient.fetch_pitcher_stat_splits using sample data for a pitcher.
    """
    # Use a sample pitcher id and season.
    pitcher_id = 669373 # Tarik Skubal
    season = 2024

    splits = MlbStatsClient.fetch_pitcher_stat_splits(pitcher_id, season)

    # Basic assertions.
    assert splits is not None, "Expected non-None stat splits for pitcher stats."
    assert isinstance(splits, pd.DataFrame), "Expected result to be a pandas DataFrame"
    assert len(splits) == 2, f"Expected 2 pitching splits, got {len(splits)} splits."

    # Define expected keys for every split.
    expected_keys = [
        'gamesPlayed'
    ]

    # Expected values for the "vl" split.
    expected_first = {
        "gamesPlayed": 26
    }

    # Expected values for the "vr" split.
    expected_second = {
         "gamesPlayed": 31
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
    # assert("h" in split_names), f"Expected 'Home' split, got {split_names}"
    # assert("a" in split_names), f"Expected 'Away' split, got {split_names}"

    # Iterate over the splits and verify expected values.
    for i, split in enumerate(splits.itertuples()):
        if i == 0:
            check_split(split, expected_first)
        elif i == 1:
            check_split(split, expected_second)
        elif i == 2:
            pass
        elif i == 3:
            pass
        else:
            pytest.fail(f"Unexpected split index: {i}")


@pytest.mark.integration
def test_fetch_player_team_integration():
    """
    Integration test for MlbStatsClient.fetch_player_team using sample data for a player.
    """
    player_id = 669373  # Tarik Skubal
    team = MlbStatsClient.fetch_player_team(player_id, 2024)
    assert team is not None, "Expected non-None team data."
    assert team['id'] == 116, f"Expected team ID 116, got {team['id']}"


@pytest.mark.integration
def test_fetch_active_roster_integration():
    """
    Integration test for MlbStatsClient.fetch_active_roster using sample data for a team.
    """
    team_id = 116  # Detroit Tigers
    roster = MlbStatsClient.fetch_active_roster(team_id)
    assert roster is not None, "Expected non-None roster data."
    assert isinstance(roster, str), "Expected roster data to be a string."
    assert len(roster) == 1062, "Expected roster string length to be 1062."


@pytest.mark.integration
def test_fetch_team_roster_integration():
    pass


@pytest.mark.integration
def test_get_team_id_integration():
    pass


@pytest.mark.integration
def test_get_player_mlbam_id_integration():
    pass


@pytest.mark.integration
def test_get_season_info_integration():
    pass
