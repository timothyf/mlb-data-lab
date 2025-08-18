import pandas as pd
import pytest
from baseball_data_lab.stats.save_season_stats import SeasonStatsDownloader


@pytest.mark.integration
def test_fetch_player_stats_integration(tmp_path):
    downloader = SeasonStatsDownloader(season=2023, output_dir=str(tmp_path))
    df = downloader._fetch_player_stats(545361)  # Mike Trout
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert (df["mlbam_id"] == 545361).all()


@pytest.mark.integration
def test_download_integration(tmp_path, monkeypatch):
    downloader = SeasonStatsDownloader(season=2023, output_dir=str(tmp_path))

    def fake_gather_rosters(self):
        roster_df = pd.DataFrame([{"mlbam_id": 545361}])
        return [(108, roster_df)]

    monkeypatch.setattr(SeasonStatsDownloader, "_gather_rosters", fake_gather_rosters)
    output_file = tmp_path / "stats.csv"
    downloader.download(output_file=str(output_file))
    assert output_file.exists()
    df = pd.read_csv(output_file)
    assert not df.empty
    assert (df["mlbam_id"] == 545361).all()
