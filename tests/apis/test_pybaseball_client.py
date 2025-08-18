# tests/test_pybaseball_client.py
import os
import pandas as pd
import pytest
from baseball_data_lab.apis.pybaseball_client import PybaseballClient, process_splits

# --- Fake Data and Functions for Testing ---

def fake_batting_stats(*args, **kwargs):
    # Returns a DataFrame with one row for a batter named 'John Doe'
    return pd.DataFrame({'Name': ['John Doe'], 'AVG': [0.300]})

def fake_batting_stats_empty(*args, **kwargs):
    # Returns an empty DataFrame with a 'Name' column
    return pd.DataFrame({'Name': []})

def fake_pitching_stats(*args, **kwargs):
    return pd.DataFrame({'Name': ['Jane Smith'], 'ERA': [3.50]})

def fake_team_batting(*args, **kwargs):
    return pd.DataFrame({'Team': ['NY'], 'Runs': [100], 'Hits': [150]})

def fake_team_pitching(*args, **kwargs):
    return pd.DataFrame({'Team': ['NY'], 'ERA': [4.00], 'Innings': [180]})

def fake_schedule_and_record(season, team_abbrev):
    return pd.DataFrame({'Game': [1, 2, 3], 'Record': ['W', 'L', 'W']})

def fake_playerid_lookup(last_name, first_name, fuzzy=False):
    return pd.DataFrame({'name': [f"{first_name} {last_name}"], 'id': [123]})

def fake_playerid_reverse_lookup(ids, key_type):
    return pd.DataFrame({'name': ['John Doe'], 'id': ids})

def fake_statcast_batter(start_date, end_date, player_id):
    return pd.DataFrame({'hit_distance': [300], 'launch_speed': [95]})

def fake_statcast_pitcher(start_date, end_date, pitcher_id):
    return pd.DataFrame({'pitch_speed': [90], 'spin_rate': [2200]})

def fake_get_splits(playerid, year, pitching_splits=False):
    # Return a simple MultiIndexed DataFrame for splits
    index = pd.MultiIndex.from_tuples([('vs LHP', 'Split1')], names=['SplitLabel', 'Dummy'])
    df = pd.DataFrame({'AB': [10], 'H': [3]}, index=index)
    return df if not pitching_splits else (df, None)

# --- Tests for PybaseballClient Methods ---

def test_fetch_fangraphs_batter_data_success(monkeypatch):
    monkeypatch.setattr("baseball_data_lab.apis.pybaseball_client.pyb.batting_stats", fake_batting_stats)
    result = PybaseballClient.fetch_fangraphs_batter_data("John Doe", "NY", 2020, 2021)
    expected = {'Name': 'John Doe', 'AVG': 0.300}
    assert result == expected

def test_fetch_fangraphs_batter_data_not_found(monkeypatch, capsys):
    monkeypatch.setattr("baseball_data_lab.apis.pybaseball_client.pyb.batting_stats", fake_batting_stats_empty)
    result = PybaseballClient.fetch_fangraphs_batter_data("Nonexistent", "NY", 2020, 2021)
    assert result is None
    captured = capsys.readouterr().out
    assert "Player 'Nonexistent' not found." in captured

def test_fetch_fangraphs_pitcher_data_success(monkeypatch):
    monkeypatch.setattr("baseball_data_lab.apis.pybaseball_client.pyb.pitching_stats", fake_pitching_stats)
    result = PybaseballClient.fetch_fangraphs_pitcher_data("Jane Smith", "NY", 2020, 2021)
    expected = {'Name': 'Jane Smith', 'ERA': 3.50}
    assert result == expected

def test_fetch_team_batting_stats(monkeypatch):
    monkeypatch.setattr("baseball_data_lab.apis.pybaseball_client.pyb.team_batting", fake_team_batting)
    result = PybaseballClient.fetch_team_batting_stats("NY", 2020, 2021)
    assert not result.empty
    assert result.iloc[0]['Team'] == "NY"

def test_fetch_team_pitching_stats(monkeypatch):
    monkeypatch.setattr("baseball_data_lab.apis.pybaseball_client.pyb.team_pitching", fake_team_pitching)
    result = PybaseballClient.fetch_team_pitching_stats("NY", 2020, 2021)
    assert not result.empty
    assert result.iloc[0]['Team'] == "NY"

def test_fetch_team_schedule_and_record(monkeypatch):
    monkeypatch.setattr("baseball_data_lab.apis.pybaseball_client.pyb.schedule_and_record", fake_schedule_and_record)
    result = PybaseballClient.fetch_team_schedule_and_record("NY", 2021)
    assert not result.empty
    assert "Record" in result.columns

def test_lookup_player(monkeypatch):
    monkeypatch.setattr("baseball_data_lab.apis.pybaseball_client.pyb.playerid_lookup", fake_playerid_lookup)
    result = PybaseballClient.lookup_player("Doe", "John")
    assert not result.empty

def test_lookup_player_by_id(monkeypatch):
    monkeypatch.setattr("baseball_data_lab.apis.pybaseball_client.pyb.playerid_reverse_lookup", fake_playerid_reverse_lookup)
    result = PybaseballClient.lookup_player_by_id(123)
    assert not result.empty

def test_fetch_statcast_batter_data(monkeypatch):
    monkeypatch.setattr("baseball_data_lab.apis.pybaseball_client.pyb.statcast_batter", fake_statcast_batter)
    result = PybaseballClient.fetch_statcast_batter_data(123, "2020-04-01", "2020-09-30")
    assert not result.empty

def test_fetch_statcast_pitcher_data(monkeypatch):
    monkeypatch.setattr("baseball_data_lab.apis.pybaseball_client.pyb.statcast_pitcher", fake_statcast_pitcher)
    result = PybaseballClient.fetch_statcast_pitcher_data(321, "2020-04-01", "2020-09-30")
    assert not result.empty

def test_save_statcast_batter_data(monkeypatch, tmp_path, capsys):
    # Fake season info for a given year
    def fake_get_season_info(year):
        return {'regularSeasonStartDate': '2020-04-01', 'regularSeasonEndDate': '2020-09-30'}
    monkeypatch.setattr("baseball_data_lab.apis.mlb_stats_client.MlbStatsClient.get_season_info", fake_get_season_info)
    monkeypatch.setattr("baseball_data_lab.apis.pybaseball_client.pyb.statcast_batter", fake_statcast_batter)
    
    # Use a temporary file path
    temp_file = tmp_path / "statcast_test.csv"
    PybaseballClient.save_statcast_batter_data(123, 2020, file_path=str(temp_file))
    assert os.path.exists(temp_file)
    df = pd.read_csv(temp_file)
    assert not df.empty

def test_save_statcast_pitcher_data(monkeypatch, tmp_path, capsys):
    def fake_get_season_info(year):
        return {'regularSeasonStartDate': '2020-04-01', 'regularSeasonEndDate': '2020-09-30'}
    monkeypatch.setattr("baseball_data_lab.apis.mlb_stats_client.MlbStatsClient.get_season_info", fake_get_season_info)
    monkeypatch.setattr("baseball_data_lab.apis.pybaseball_client.pyb.statcast_pitcher", fake_statcast_pitcher)
    
    temp_file = tmp_path / "statcast_pitcher_test.csv"
    PybaseballClient.save_statcast_pitcher_data(321, 2020, file_path=str(temp_file))
    assert os.path.exists(temp_file)
    df = pd.read_csv(temp_file)
    assert not df.empty

def test_fetch_batting_splits_leaderboards(monkeypatch):
    # Create a fake StatsConfig with desired stat list for batting splits
    class FakeStatsConfig:
        stat_lists = {'batting': {'splits': ['AB', 'H']}}
    monkeypatch.setattr("baseball_data_lab.apis.pybaseball_client.StatsConfig", lambda: FakeStatsConfig())
    monkeypatch.setattr("baseball_data_lab.apis.pybaseball_client.pyb.get_splits", fake_get_splits)
    result = PybaseballClient.fetch_batting_splits_leaderboards("player_bbref", 2020)
    assert isinstance(result, pd.DataFrame)

def test_fetch_pitching_splits_leaderboards(monkeypatch):
    # Create a fake StatsConfig with desired stat list for pitching splits
    class FakeStatsConfig:
        stat_lists = {'pitching': {'splits': ['AB', 'H']}}
    monkeypatch.setattr("baseball_data_lab.apis.pybaseball_client.StatsConfig", lambda: FakeStatsConfig())
    monkeypatch.setattr("baseball_data_lab.apis.pybaseball_client.pyb.get_splits", fake_get_splits)
    result = PybaseballClient.fetch_pitching_splits_leaderboards("player_bbref", 2020)
    assert isinstance(result, pd.DataFrame)

def test_process_splits():
    # Create a simple multi-index DataFrame to simulate splits data
    # Make sure the split label is in level 1 as expected by process_splits.
    index = pd.MultiIndex.from_tuples([('dummy', 'vs LHP')], names=['Dummy', 'SplitLabel'])
    data = pd.DataFrame({'AB': [10], 'H': [3]}, index=index)
    splits_stats_list = ['AB', 'H']
    split_labels = ['vs LHP', 'vs RHP']
    combined = process_splits(data, splits_stats_list, split_labels, "player_bbref", 2020)
    # Check that the processed data contains the expected split label
    assert not combined.empty
