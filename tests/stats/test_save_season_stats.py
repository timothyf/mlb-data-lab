import json
import pandas as pd
import os
import pytest

from mlb_data_lab.stats import save_season_stats
from mlb_data_lab.stats.save_season_stats import SeasonStatsDownloader


def test_get_team_ids_by_league(tmp_path, monkeypatch):
    data_dir = tmp_path
    teams = [
        {"mlbam_team_id": 1, "league": "AL"},
        {"mlbam_team_id": 2, "league": "NL"},
        {"mlbam_team_id": 3, "league": "AL"}
    ]
    (data_dir / "mlb_teams.json").write_text(json.dumps(teams))
    monkeypatch.setattr(save_season_stats, "DATA_DIR", str(data_dir))
    downloader = SeasonStatsDownloader(season=2024, output_dir=str(tmp_path))
    ids = downloader.get_team_ids_by_league("AL")
    assert ids == [1, 3]


def test_flush_to_disk(tmp_path):
    downloader = SeasonStatsDownloader(season=2024, output_dir=str(tmp_path))
    file_path = tmp_path / "out.csv"
    df1 = pd.DataFrame({"A": [1, 2]})
    df2 = pd.DataFrame({"A": [3]})
    downloader._flush_to_disk([df1], str(file_path), True)
    downloader._flush_to_disk([df2], str(file_path), False)
    df = pd.read_csv(file_path)
    assert df["A"].tolist() == [1, 2, 3]


class DummyClient:
    def __init__(self):
        self.pitch_df = pd.DataFrame({"wins": [1]})
        self.bat_df = pd.DataFrame({"hits": [5]})

    def fetch_pitching_stats(self, mlbam_id, season, fangraphs_team_id=None):
        return self.pitch_df

    def fetch_batting_stats(self, mlbam_id, season, fangraphs_team_id=None):
        return self.bat_df


class DummyPlayerInfo:
    def __init__(self, pos):
        self.primary_position = pos


class DummyBio:
    full_name = "Dummy Player"


class DummyPlayer:
    def __init__(self, pos):
        self.player_info = DummyPlayerInfo(pos)
        self.player_bio = DummyBio()


def test_fetch_player_stats_success(monkeypatch, tmp_path):
    client = DummyClient()
    downloader = SeasonStatsDownloader(season=2024, output_dir=str(tmp_path))
    downloader.client = client
    monkeypatch.setattr(save_season_stats.Player, "create_from_mlb", lambda mlbam_id, data_client=None: DummyPlayer("P"))
    df = downloader._fetch_player_stats(1, 109)
    assert isinstance(df, pd.DataFrame)
    assert df["mlbam_id"].iloc[0] == 1
    assert df["season"].iloc[0] == 2024
    assert downloader.statuses["success"] == ["Dummy Player"]


def test_fetch_player_stats_position_mismatch(monkeypatch, tmp_path):
    client = DummyClient()
    downloader = SeasonStatsDownloader(season=2024, output_dir=str(tmp_path), player_type="batters")
    downloader.client = client
    monkeypatch.setattr(save_season_stats.Player, "create_from_mlb", lambda mlbam_id, data_client=None: DummyPlayer("P"))
    result = downloader._fetch_player_stats(2, 109)
    assert result is None
    assert downloader.statuses["position_mismatch"] == ["Dummy Player"]
