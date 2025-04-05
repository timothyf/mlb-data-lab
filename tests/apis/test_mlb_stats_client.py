# tests/apis/test_mlb_stats_client.py

import pytest
import json
import requests
import statsapi
from mlb_data_lab.apis.mlb_stats_client import MlbStatsClient

# A simple fake response class for monkeypatching requests.get
class FakeResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code
    def json(self):
        return self._json_data

# ---------------------------
# Test fetch_player_info
# ---------------------------
def test_fetch_player_info(monkeypatch):
    fake_data = {"people": [{"id": 669373, "name": "Test Player", "currentTeam": {"id": 123}}]}
    def fake_get(url):
        return FakeResponse(fake_data)
    monkeypatch.setattr(requests, "get", fake_get)
    
    result = MlbStatsClient.fetch_player_info(669373)
    assert result["id"] == 669373
    assert result["name"] == "Test Player"

# ---------------------------
# Test fetch_team
# ---------------------------
def test_fetch_team(monkeypatch):
    fake_data = {"teams": [{"id": 116, "name": "Test Team"}]}
    def fake_get(url):
        return FakeResponse(fake_data)
    monkeypatch.setattr(requests, "get", fake_get)
    
    result = MlbStatsClient.fetch_team(116)
    assert result["id"] == 116
    assert result["name"] == "Test Team"

# ---------------------------
# Test fetch_player_stats
# ---------------------------
def test_fetch_player_stats(monkeypatch):
    fake_stats = {"people": [{"stats": [{"splits": [{"some_stat": 42}]}]}]}
    def fake_statsapi_get(endpoint, params):
        # 'endpoint' is expected to be 'people'
        return fake_stats
    monkeypatch.setattr(statsapi, "get", fake_statsapi_get)
    
    result = MlbStatsClient.fetch_player_stats(12345, 2020)
    assert result == [{"some_stat": 42}]

# ---------------------------
# Test fetch_player_stats_by_season
# ---------------------------
def test_fetch_player_stats_by_season(monkeypatch):
    fake_json = {
        "people": [
            {
                "id": 12345,
                "stats": [
                    {
                        "type": {"displayName": "season"},
                        "splits": [
                            {"season": "2024", "stat": {"baseOnBalls": 10, "plateAppearances": 100, "strikeOuts": 20}},
                        ],
                    },
                    {
                        "type": {"displayName": "seasonAdvanced"},
                        "splits": [
                            {"season": "2024", "stat": {"someAdvancedStat": 5}},
                        ],
                    }
                ]
            }
        ]
    }
    def fake_requests_get(url):
        return FakeResponse(fake_json)
    monkeypatch.setattr(requests, "get", fake_requests_get)
    
    result = MlbStatsClient.fetch_player_stats_by_season(12345, 2024)
    # Verify that the returned structure contains calculated values.
    assert "season" in result["season_stats"]
    season_stats = result["season_stats"]["season"]
    # Check that BB% and K% were calculated
    assert "BB%" in season_stats
    assert "K%" in season_stats

# ---------------------------
# Test fetch_player_team
# ---------------------------
def test_fetch_player_team(monkeypatch):
    fake_data = {
        "people": [
            {
                "stats": [
                    {"splits": [{"team": {"teamName": "Test Team"}}]}
                ]
            }
        ]
    }
    def fake_statsapi_get(endpoint, params):
        return fake_data
    monkeypatch.setattr(statsapi, "get", fake_statsapi_get)
    
    result = MlbStatsClient.fetch_player_team(12345, 2020)
    assert result["teamName"] == "Test Team"

# ---------------------------
# Test fetch_active_roster
# ---------------------------
def test_fetch_active_roster(monkeypatch):
    fake_roster = {"roster": [{"person": {"fullName": "Player A"}}, {"person": {"fullName": "Player B"}}]}
    monkeypatch.setattr(statsapi, "roster", lambda team_id, rosterType, season: fake_roster)
    
    result = MlbStatsClient.fetch_active_roster(team_id=100, year=2024)
    assert isinstance(result, dict)
    assert "roster" in result
    assert len(result["roster"]) == 2

# ---------------------------
# Test fetch_team_roster
# ---------------------------
def test_fetch_team_roster(monkeypatch):
    fake_roster = {
        "roster": [
            {"person": {"fullName": "Player A"}},
            {"person": {"fullName": "Player B"}}
        ]
    }
    def fake_statsapi_get(endpoint, params):
        return fake_roster
    monkeypatch.setattr(statsapi, "get", fake_statsapi_get)
    
    result = MlbStatsClient.fetch_team_roster(100, 2024)
    assert isinstance(result, list)
    assert result == ["Player A", "Player B"]

# ---------------------------
# Test get_team_id
# ---------------------------
def test_get_team_id(monkeypatch):
    fake_lookup = [{"id": 200, "name": "Test Team"}]
    monkeypatch.setattr(statsapi, "lookup_team", lambda team_name: fake_lookup)
    
    result = MlbStatsClient.get_team_id("Test Team")
    assert result == 200

def test_get_team_id_not_found(monkeypatch):
    monkeypatch.setattr(statsapi, "lookup_team", lambda team_name: [])
    with pytest.raises(ValueError):
        MlbStatsClient.get_team_id("Nonexistent Team")

# ---------------------------
# Test get_player_mlbam_id
# ---------------------------
def test_get_player_mlbam_id(monkeypatch, capsys):
    fake_lookup = [{"id": 300, "fullName": "Test Player"}]
    monkeypatch.setattr(statsapi, "lookup_player", lambda player_name: fake_lookup)
    
    result = MlbStatsClient.get_player_mlbam_id("Test Player")
    captured = capsys.readouterr().out
    assert "Player Name: Test Player, MLBAM ID: 300" in captured
    assert result == 300

def test_get_player_mlbam_id_not_found(monkeypatch, capsys):
    monkeypatch.setattr(statsapi, "lookup_player", lambda player_name: [])
    
    result = MlbStatsClient.get_player_mlbam_id("Unknown Player")
    captured = capsys.readouterr().out
    assert "No player found for name: Unknown Player" in captured
    assert result is None

# ---------------------------
# Test get_season_info
# ---------------------------
def test_get_season_info(monkeypatch):
    def fake_statsapi_get(endpoint, params):
        return {"seasons": [{"seasonId": params["seasonId"], "startDate": "2024-03-28", "endDate": "2024-10-01"}]}
    monkeypatch.setattr(statsapi, "get", fake_statsapi_get)
    
    result = MlbStatsClient.get_season_info(2024)
    assert result["seasonId"] == 2024
    assert result["startDate"] == "2024-03-28"
    assert result["endDate"] == "2024-10-01"
