import pandas as pd

from mlb_data_lab.stats.league_averages import compute_leage_totals, compute_league_averages


def create_sample_stats_df():
    return pd.DataFrame(
        {
            "Pos": ["C", "1B", "OF", "P"],
            "xMLBAMID": [1, 2, 3, 4],
            "TeamName": ["BOS", "BOS", "NYY", "BOS"],
            "AB": [100, 200, 150, 0],
            "H": [30, 60, 50, 0],
            "HR": [5, 10, 8, 0],
            "SO": [20, 40, 30, 0],
            "RBI": [20, 50, 40, 0],
        }
    )


def test_compute_team_totals_and_averages():
    stats = create_sample_stats_df()
    team = "BOS"

    totals = compute_leage_totals(2024, stats, team=team)
    expected_totals = pd.DataFrame(
        [[300, 90, 15, 60, 70]],
        columns=["AB", "H", "HR", "SO", "RBI"],
        index=[team],
    )
    pd.testing.assert_frame_equal(totals, expected_totals)

    avgs = compute_league_averages(2024, stats, team=team)
    expected_avgs = pd.DataFrame(
        [[2024, 150.0, 45.0, 7.5, 30.0, 35.0, 0.3]],
        columns=["season", "AB", "H", "HR", "SO", "RBI", "BA"],
        index=[team],
    )
    pd.testing.assert_frame_equal(avgs, expected_avgs)
