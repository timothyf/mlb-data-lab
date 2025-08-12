import pandas as pd
import requests
import pytest

from mlb_data_lab.apis.fangraphs_client import FangraphsClient
from mlb_data_lab.config import FANGRAPHS_BASE_URL

class DummyResponse:
    def __init__(self, data):
        self._data = data
    def json(self):
        return {"data": self._data}


def make_fake_get(monkeypatch, expected_url, data):
    def fake_get(url):
        assert url == expected_url
        return DummyResponse(data)
    monkeypatch.setattr(requests, "get", fake_get)


def test_fetch_player_stats_builds_correct_url(monkeypatch):
    # Past season uses month=0
    expected_url = (
        f"{FANGRAPHS_BASE_URL}?pos=all&stats=pit&lg=all&qual=0"
        f"&season=2024&startdate=2024-03-01&enddate=2024-11-01"
        f"&month=0&team=12&players=345"
    )
    make_fake_get(monkeypatch, expected_url, [{"x": 1}])
    df = FangraphsClient.fetch_player_stats(345, 2024, 12, "pitching")
    assert isinstance(df, pd.DataFrame)
    assert df.to_dict("records") == [{"x": 1}]


def test_fetch_player_stats_current_season(monkeypatch):
    # Current season uses month=33 and handles batting
    expected_url = (
        f"{FANGRAPHS_BASE_URL}?pos=all&stats=bat&lg=all&qual=0"
        f"&season=2025&startdate=2025-03-01&enddate=2025-11-01"
        f"&month=33&players=999"
    )
    make_fake_get(monkeypatch, expected_url, [{"y": 2}])
    df = FangraphsClient.fetch_player_stats(999, 2025, None, "batting")
    assert df.to_dict("records") == [{"y": 2}]


def test_fetch_player_stats_invalid_type():
    with pytest.raises(ValueError):
        FangraphsClient.fetch_player_stats(1, 2024, None, "fielding")


def test_fetch_leaderboards_dispatch(monkeypatch):
    calls = []
    def fake_pitch(season):
        calls.append(("pitch", season))
    def fake_bat(season):
        calls.append(("bat", season))
    monkeypatch.setattr(FangraphsClient, "fetch_pitching_leaderboards", fake_pitch)
    monkeypatch.setattr(FangraphsClient, "fetch_batting_leaderboards", fake_bat)
    FangraphsClient.fetch_leaderboards(2030, "pitching")
    FangraphsClient.fetch_leaderboards(2031, "batting")
    assert calls == [("pitch", 2030), ("bat", 2031)]
    with pytest.raises(ValueError):
        FangraphsClient.fetch_leaderboards(2000, "oops")


def test_fetch_team_players_merges_names(monkeypatch):
    expected_bat_url = (
        f"{FANGRAPHS_BASE_URL}?age=&pos=all&stats=bat&lg=all&qual=0"
        f"&season=2024&season1=2024&hand=&team=99"
        f"&pageitems=800&pagenum=1&ind=0&rost=0&players=0&type=8"
        f"&postseason=&sortdir=default&sortstat=WAR"
    )
    expected_pitch_url = (
        f"{FANGRAPHS_BASE_URL}?age=&pos=all&stats=pit&lg=all&qual=0&season=2024"
        f"&season1=2024&hand=&team=99&pageitems=800&pagenum=1&ind=0&rost=0"
        f"&players=0&type=8&postseason=&sortdir=default&sortstat=WAR"
    )
    urls = []
    def fake_get(url):
        urls.append(url)
        if url == expected_bat_url:
            return DummyResponse([{"PlayerName": "A"}, {"PlayerName": "B"}])
        else:
            return DummyResponse([{"PlayerName": "B"}, {"PlayerName": "C"}])
    monkeypatch.setattr(requests, "get", fake_get)
    players = FangraphsClient.fetch_team_players(99, 2024)
    assert urls == [expected_bat_url, expected_pitch_url]
    assert players == ["A", "B", "C"]

def test_fetch_leaderboard_helpers(monkeypatch):
    pitch_url = (
        f"{FANGRAPHS_BASE_URL}?age=&pos=all&stats=pit&lg=all"
        f"&season=2022&season1=2022&ind=0&qual=0&type=8&month=0&pageitems=500000"
    )
    bat_url = (
        f"{FANGRAPHS_BASE_URL}?age=&pos=all&stats=bat&lg=all"
        f"&season=2022&season1=2022&ind=0&qual=0&type=8&month=0&pageitems=500000"
    )
    urls = []
    def fake_get(url):
        urls.append(url)
        return DummyResponse([{"PlayerName": "X"}])
    monkeypatch.setattr(requests, "get", fake_get)
    df1 = FangraphsClient.fetch_pitching_leaderboards(2022)
    df2 = FangraphsClient.fetch_batting_leaderboards(2022)
    assert urls == [pitch_url, bat_url]
    assert df1.to_dict("records") == [{"PlayerName": "X"}]
    assert df2.to_dict("records") == [{"PlayerName": "X"}]



