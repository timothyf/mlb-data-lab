# tests/player/test_player.py

import os
import pytest
from io import BytesIO
from PIL import Image
import pandas as pd

from mlb_data_lab.player.player import Player
from mlb_data_lab.team.team import Team


# Dummy implementations (as defined before)
class DummyUnifiedDataClient:
    def fetch_pitching_splits(self, player_id: int, season: int) -> pd.DataFrame:
        return {"dummy": "pitcher_splits"}
    def fetch_batting_splits(self, player_id: int, season: int) -> pd.DataFrame:
        return {"dummy": "batter_splits"}
    def fetch_fangraphs_pitcher_data(self, player_name, team_fangraphs_id, start_year, end_year):
        # Default dummy value; will be overridden in tests using monkeypatch.
        return {"dummy": "pitcher_stats"}
    def fetch_fangraphs_batter_data(self, player_name, team_fangraphs_id, start_year, end_year):
        # Default dummy value; will be overridden in tests using monkeypatch.
        return {"dummy": "batter_stats"}
    def fetch_pitching_splits_leaderboards(self, player_bbref, season):
        return {"dummy": "pitcher_splits"}
    def fetch_batting_splits_leaderboards(self, player_bbref, season):
        return {"dummy": "batter_splits"}
    def fetch_statcast_pitcher_data(self, mlbam_id, start_date, end_date):
        return {"dummy": "statcast_pitcher"}
    def fetch_statcast_batter_data(self, mlbam_id, start_date, end_date):
        return {"dummy": "statcast_batter"}
    def fetch_player_info(self, mlbam_id):
        return {"id": mlbam_id, "currentTeam": {"id": 100}}
    def fetch_player_headshot(self, mlbam_id):
        img = Image.new("RGB", (10, 10), color="red")
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    def save_statcast_pitcher_data(self, mlbam_id, year, file_path):
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write("dummy pitcher statcast data")
    def save_statcast_batter_data(self, mlbam_id, year, file_path):
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write("dummy batter statcast data")

class DummyPlayerBio:
    def __init__(self):
        self.full_name = "Dummy Player"
    def set_from_mlb_info(self, mlb_player_info):
        self.full_name = "Dummy Player"
    def to_json(self):
        return {"bio": "dummy"}

class DummyPlayerInfo:
    def __init__(self):
        self.primary_position = "P"  # Default to pitcher
    def set_from_mlb_info(self, mlb_player_info):
        self.primary_position = "P"
    def to_json(self):
        return {"info": "dummy"}

class DummyTeam:
    @classmethod
    def create_from_mlb(cls, team_id):
        team = cls()
        team.name = "Dummy Team"
        team.abbrev = "DT"
        team.fangraphs_id = "dummy_fg"
        return team

class DummyPlayerLookup:
    @staticmethod
    def lookup_player(player_name):
        return {"key_mlbam": 123, "key_bbref": "dummy_bbref"}
    @staticmethod
    def lookup_player_by_id(mlbam_id):
        return {"full_name": "Dummy Player", "key_bbref": "dummy_bbref"}

# --- Fixture that patches the dependencies in the Player module ---
@pytest.fixture(autouse=True)
def setup_player(monkeypatch):
    # Patch the classes used inside the Player module.
    monkeypatch.setattr("mlb_data_lab.player.player.UnifiedDataClient", DummyUnifiedDataClient)
    monkeypatch.setattr("mlb_data_lab.player.player.PlayerInfo", DummyPlayerInfo)
    monkeypatch.setattr("mlb_data_lab.player.player.PlayerBio", DummyPlayerBio)
    monkeypatch.setattr("mlb_data_lab.player.player.Team", DummyTeam)
    monkeypatch.setattr("mlb_data_lab.player.player.PlayerLookup", DummyPlayerLookup)
    # Use monkeypatch.setattr to set the class attribute so it is automatically undone.
    monkeypatch.setattr(Player, "data_client", DummyUnifiedDataClient())


# --- Tests for Player Methods using fixture data for stats ---

def test_set_player_stats_pitcher(monkeypatch, sample_pitcher_stats, sample_pitcher_stat_splits):
    """
    Test set_player_stats for a pitcher using fixture data for standard/advanced stats.
    """
    player = Player(mlbam_id=123)
    player.player_info = DummyPlayerInfo()
    player.player_info.primary_position = "P"  # pitcher
    player.player_bio = DummyPlayerBio()
    player.player_bio.full_name = "Pitcher Dummy"
    player.current_team = DummyTeam.create_from_mlb(100)
    player.bbref_id = "dummy_bbref"
    
    # Override the data client methods to return fixture data.
    monkeypatch.setattr(DummyUnifiedDataClient, "fetch_fangraphs_pitcher_data", 
                        lambda self, player_name, team_fangraphs_id, start_year, end_year: sample_pitcher_stats)
    # Advanced stats are set equal to standard stats.
    monkeypatch.setattr(DummyUnifiedDataClient, "fetch_pitching_splits", 
                        lambda self, player_bbref, season: sample_pitcher_stat_splits)
    
    player.set_player_stats(2020)
    
    assert player.player_stats == sample_pitcher_stats
    assert player.player_splits_stats == sample_pitcher_stat_splits


def test_set_player_stats_batter(monkeypatch, sample_batter_stats, sample_batter_stat_splits):
    """
    Test set_player_stats for a batter using fixture data for standard/advanced stats
    and sample batter stat splits.
    """
    player = Player(mlbam_id=124)
    player.player_info = DummyPlayerInfo()
    player.player_info.primary_position = "C"  # non-pitcher
    player.player_bio = DummyPlayerBio()
    player.player_bio.full_name = "Batter Dummy"
    player.current_team = DummyTeam.create_from_mlb(101)
    player.bbref_id = "dummy_bbref"
    
    # Override the data client methods to return fixture data.
    monkeypatch.setattr(
        DummyUnifiedDataClient, 
        "fetch_fangraphs_batter_data", 
        lambda self, player_name, team_fangraphs_id, start_year, end_year: sample_batter_stats
    )
    monkeypatch.setattr(
        DummyUnifiedDataClient, 
        "fetch_batting_splits", 
        lambda self, player_bbref, season: sample_batter_stat_splits
    )
    
    player.set_player_stats(2020)
    
    assert player.player_stats == sample_batter_stats
    assert player.player_splits_stats == sample_batter_stat_splits


# The remaining tests remain unchanged.
def test_set_statcast_data_pitcher():
    # Test set_statcast_data for a pitcher.
    player = Player(mlbam_id=123)
    player.player_info = DummyPlayerInfo()
    player.player_info.primary_position = "P"
    player.set_statcast_data("2020-04-01", "2020-09-30")
    assert player.statcast_data == {"dummy": "statcast_pitcher"}

def test_set_statcast_data_batter():
    # Test set_statcast_data for a batter.
    player = Player(mlbam_id=124)
    player.player_info = DummyPlayerInfo()
    player.player_info.primary_position = "C"
    player.set_statcast_data("2020-04-01", "2020-09-30")
    assert player.statcast_data == {"dummy": "statcast_batter"}

def test_get_headshot():
    # Test that get_headshot returns a PIL Image.
    player = Player(mlbam_id=123)
    img = player.get_headshot()
    from PIL import Image
    assert isinstance(img, Image.Image)

def test_save_statcast_data_pitcher(tmp_path, monkeypatch):
    # Test saving statcast data for a pitcher.
    player = Player(mlbam_id=123)
    player.player_info = DummyPlayerInfo()
    player.player_info.primary_position = "P"
    player.player_bio = DummyPlayerBio()
    player.player_bio.full_name = "Pitcher Dummy"
    player.current_team = DummyTeam.create_from_mlb(100)
    year = 2024
    monkeypatch.setattr("mlb_data_lab.player.player.STATCAST_DATA_DIR", str(tmp_path))
    player.save_statcast_data(year)
    expected_file = tmp_path / f'{year}/statcast_data/{player.current_team.abbrev}/pitching/statcast_data_{player.player_bio.full_name.lower().replace(" ", "_")}_{year}.csv'
    assert expected_file.exists(), f"Expected file {expected_file} does not exist."

def test_save_statcast_data_batter(tmp_path, monkeypatch):
    # Test saving statcast data for a batter.
    player = Player(mlbam_id=124)
    player.player_info = DummyPlayerInfo()
    player.player_info.primary_position = "C"
    player.player_bio = DummyPlayerBio()
    player.player_bio.full_name = "Batter Dummy"
    player.current_team = DummyTeam.create_from_mlb(101)
    year = 2024
    monkeypatch.setattr("mlb_data_lab.player.player.STATCAST_DATA_DIR", str(tmp_path))
    player.save_statcast_data(year)
    expected_file = tmp_path / f'{year}/statcast_data/{player.current_team.abbrev}/batting/statcast_data_{player.player_bio.full_name.lower().replace(" ", "_")}_{year}.csv'
    assert expected_file.exists()

def test_create_from_mlb():
    # Test the create_from_mlb static method using player_name.
    player = Player.create_from_mlb(player_name="Dummy Player")
    assert player.mlbam_id == 123
    assert player.bbref_id == "dummy_bbref"
    assert hasattr(player.player_info, "primary_position")
    assert player.current_team.name == "Dummy Team"

def test_to_json():
    # Test that to_json returns the expected dictionary structure.
    player = Player(mlbam_id=123)
    player.bbref_id = "dummy_bbref"
    dummy_team = DummyTeam.create_from_mlb(100)
    player.current_team = dummy_team
    player.player_bio = DummyPlayerBio()
    player.player_info = DummyPlayerInfo()
    player.player_bio.full_name = "Dummy Player"
    player.player_bio.to_json = lambda: {"bio": "dummy"}
    player.player_info.to_json = lambda: {"info": "dummy"}
    result = player.to_json()
    assert result["mlbam_id"] == 123
    assert result["bbref_id"] == "dummy_bbref"
    assert result["team_name"] == dummy_team.name
    assert result["player_bio"] == {"bio": "dummy"}
    assert result["player_info"] == {"info": "dummy"}
