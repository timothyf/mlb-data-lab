import pandas as pd
import pytest
from mlb_data_lab.stats.save_season_stats import SeasonStatsDownloader


@pytest.mark.integration
def test_fetch_player_stats_integration(tmp_path):
    downloader = SeasonStatsDownloader(season=2023, output_dir=str(tmp_path))
    df = downloader._fetch_player_stats(545361)  # Mike Trout
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert (df["mlbam_id"] == 545361).all()
