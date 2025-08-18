import pytest
import pandas as pd
from types import SimpleNamespace

from baseball_data_lab.stats.stats_display import StatsDisplay


# --- Dummy Player Data ---
@pytest.fixture(scope="module")
def dummy_player(sample_batter_stats, sample_batter_stat_splits):
    return SimpleNamespace(
        player_stats=pd.DataFrame(sample_batter_stats),
        player_splits_stats=sample_batter_stat_splits,
    )


# --- Dummy StatsTable ---
# We will monkeypatch _plot_stats_table so we don't invoke the real StatsTable.
@pytest.fixture(scope="module")
def capture_plot():
    calls = []
    mp = pytest.MonkeyPatch()

    def dummy_plot(self, stats, stat_fields, ax, title, is_splits):
        calls.append(
            {
                "stats": stats,
                "stat_fields": stat_fields,
                "ax": ax,
                "title": title,
                "is_splits": is_splits,
            }
        )

    mp.setattr(StatsDisplay, "_plot_stats_table", dummy_plot)
    yield calls
    mp.undo()


@pytest.fixture(scope="module")
def stats_display(dummy_player):
    return StatsDisplay(dummy_player, 2023, "batting")


# --- Tests for Helper Methods ---
@pytest.mark.parametrize(
    "df, expected, missing",
    [
        (
            pd.DataFrame([{"AB": 400, "H": 120, "AVG": ".300", "RBI": 50, "Extra": 99}]),
            pd.DataFrame([{"AB": 400, "H": 120, "AVG": ".300", "RBI": 50}]),
            [],
        ),
        (
            pd.DataFrame([{"AB": 400, "H": 120}]),
            pd.DataFrame([{"AB": 400, "H": 120}]),
            ["AVG", "RBI"],
        ),
        (
            pd.DataFrame([{"X": 1, "Y": 2}]),
            None,
            ["AB", "H", "AVG", "RBI"],
        ),
    ],
)
def test_filter_columns(stats_display, df, expected, missing, capfd):
    stat_fields = ["AB", "H", "AVG", "RBI"]
    filtered = stats_display._filter_columns(stat_fields, df)
    captured = capfd.readouterr().out
    if missing:
        assert "Warning: The following columns are missing" in captured
    else:
        assert captured == ""
    if expected is None:
        assert filtered is None
    else:
        pd.testing.assert_frame_equal(filtered, expected)


# --- Tests for Display Methods ---
def test_display_standard_stats(stats_display, capture_plot, sample_batter_stats):
    capture_plot.clear()
    stats_display.display_standard_stats(ax=None)
    assert len(capture_plot) == 1
    call = capture_plot[0]
    assert "Standard" in call["title"]
    expected_fields = ["AB", "H", "AVG", "RBI"]
    expected_df = pd.DataFrame(sample_batter_stats)[expected_fields]
    actual_df = (
        call["stats"][expected_fields]
        if isinstance(call["stats"], pd.DataFrame)
        else pd.DataFrame(call["stats"])[expected_fields]
    )
    pd.testing.assert_frame_equal(
        actual_df.reset_index(drop=True),
        expected_df.reset_index(drop=True),
    )


def test_display_advanced_stats(stats_display, capture_plot, sample_batter_stats):
    capture_plot.clear()
    stats_display.display_advanced_stats(ax=None)
    assert len(capture_plot) == 1
    call = capture_plot[0]
    assert "Advanced" in call["title"]
    expected_fields = ["OBP", "SLG", "OPS"]
    expected_df = pd.DataFrame(sample_batter_stats)[expected_fields]
    actual_df = (
        call["stats"][expected_fields]
        if isinstance(call["stats"], pd.DataFrame)
        else pd.DataFrame(call["stats"])[expected_fields]
    )
    pd.testing.assert_frame_equal(
        actual_df.reset_index(drop=True),
        expected_df.reset_index(drop=True),
    )


def test_plot_splits_stats(stats_display, capture_plot, sample_batter_stat_splits):
    capture_plot.clear()
    stats_display.plot_splits_stats(ax=None)
    assert len(capture_plot) == 1
    call = capture_plot[0]
    assert "Splits" in call["title"]
    expected_fields = ["atBats", "hits", "avg", "rbi"]
    expected_stats = [
        {k: v for k, v in split.get("stat", {}).items() if k in expected_fields}
        for split in sample_batter_stat_splits
    ]
    expected_df = pd.DataFrame(expected_stats).reset_index(drop=True)

    actual_stats = [
        {k: v for k, v in split.get("stat", {}).items() if k in expected_fields}
        for split in call["stats"]
        if "stat" in split
    ]
    actual_df = pd.DataFrame(actual_stats).reset_index(drop=True)
    pd.testing.assert_frame_equal(actual_df, expected_df, check_like=True)

