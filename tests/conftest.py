import json
import os
import pytest

@pytest.fixture
def sample_batter_stats():
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "sample_batter_stats.json")
    with open(fixture_path, "r") as f:
        data = json.load(f)
    return data

@pytest.fixture
def sample_pitcher_stats():
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "sample_pitcher_stats.json")
    with open(fixture_path, "r") as f:
        data = json.load(f)
    return data

@pytest.fixture
def sample_batter_stat_splits():
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "sample_batter_stat_splits.json")
    with open(fixture_path, "r") as f:
        data = json.load(f)
    return data

@pytest.fixture
def sample_pitcher_stat_splits():
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "sample_pitcher_stat_splits.json")
    with open(fixture_path, "r") as f:
        data = json.load(f)
    return data