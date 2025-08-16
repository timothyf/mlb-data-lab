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


def create_multi_team_stats_df():
    """Return stats with a player appearing for two teams and a total row."""
    return pd.DataFrame(
        {
            "Pos": ["C", "C", "C", "1B", "OF"],
            "xMLBAMID": [1, 1, 1, 2, 3],
            "TeamName": ["BOS", "CHC", "- - -", "LAD", "NYY"],
            "AB": [100, 50, 150, 200, 150],
            "H": [30, 15, 45, 60, 50],
            "HR": [5, 3, 8, 10, 8],
            "SO": [20, 10, 30, 40, 30],
            "RBI": [20, 15, 35, 50, 40],
        }
    )


def test_league_totals_and_averages_include_multi_team_players():
    stats = create_multi_team_stats_df()

    totals = compute_leage_totals(2024, stats)
    expected_totals = pd.DataFrame(
        [
            [250, 80, 13, 50, 60],
            [250, 75, 13, 50, 65],
            [500, 155, 26, 100, 125],
        ],
        columns=["AB", "H", "HR", "SO", "RBI"],
        index=["AL", "NL", "MLB"],
    )
    pd.testing.assert_frame_equal(totals, expected_totals)

    avgs = compute_league_averages(2024, stats)
    expected_avgs = pd.DataFrame(
        [
            [2024, 125.0, 40.0, 6.5, 25.0, 30.0, 0.32],
            [2024, 125.0, 37.5, 6.5, 25.0, 32.5, 0.3],
            [2024, 125.0, 38.75, 6.5, 25.0, 31.25, 0.31],
        ],
        columns=["season", "AB", "H", "HR", "SO", "RBI", "BA"],
        index=["AL", "NL", "MLB"],
    )
    pd.testing.assert_frame_equal(avgs, expected_avgs)
