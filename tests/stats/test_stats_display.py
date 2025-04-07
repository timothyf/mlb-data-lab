import pytest
import pandas as pd
import matplotlib.pyplot as plt

from mlb_data_lab.data_viz.stats_table import StatsTable  # used only to satisfy import in StatsDisplay
from mlb_data_lab.player.player import Player
from mlb_data_lab.stats.stats_display import StatsDisplay
from mlb_data_lab.config import StatsConfig



# --- Dummy Player Data ---
@pytest.fixture
def dummy_player(sample_batter_standard_stats, sample_batter_advanced_stats, sample_batter_stat_splits):
    player = Player(123)
    player.player_stats = sample_batter_standard_stats
    player.player_splits_stats = sample_batter_stat_splits
    return player

# --- Dummy StatsTable ---
# We will monkeypatch _plot_stats_table so we don't invoke the real StatsTable.
@pytest.fixture
def capture_plot(monkeypatch):
    calls = []
    def dummy_plot(self, stats, stat_fields, ax, title, is_splits):
        calls.append({
            'stats': stats,
            'stat_fields': stat_fields,
            'ax': ax,
            'title': title,
            'is_splits': is_splits
        })
    monkeypatch.setattr(StatsDisplay, "_plot_stats_table", dummy_plot)
    return calls

# --- Tests for Helper Methods ---

def test_filter_columns_all_present():
    # All columns available.
    stat_fields = ['AB', 'H', 'AVG', 'RBI']
    df = pd.DataFrame([{'AB': 400, 'H': 120, 'AVG': '.300', 'RBI': 50, 'Extra': 99}])
    from mlb_data_lab.stats.stats_display import StatsDisplay
    sd = StatsDisplay(Player(123), 2023, 'batting')
    filtered = sd._filter_columns(stat_fields, df)
    expected = pd.DataFrame([{'AB': 400, 'H': 120, 'AVG': '.300', 'RBI': 50}])
    pd.testing.assert_frame_equal(filtered, expected)

def test_filter_columns_some_missing(capfd):
    stat_fields = ['AB', 'H', 'AVG', 'RBI']
    df = pd.DataFrame([{'AB': 400, 'H': 120}])
    from mlb_data_lab.stats.stats_display import StatsDisplay
    sd = StatsDisplay(Player(123), 2023, 'batting')
    filtered = sd._filter_columns(stat_fields, df)
    captured = capfd.readouterr().out
    assert "Warning: The following columns are missing" in captured
    expected = pd.DataFrame([{'AB': 400, 'H': 120}])
    pd.testing.assert_frame_equal(filtered, expected)

def test_filter_columns_none_available(capfd):
    stat_fields = ['AB', 'H', 'AVG', 'RBI']
    df = pd.DataFrame([{'X': 1, 'Y': 2}])
    from mlb_data_lab.stats.stats_display import StatsDisplay
    sd = StatsDisplay(Player(123), 2023, 'batting')
    filtered = sd._filter_columns(stat_fields, df)
    captured = capfd.readouterr().out
    assert "Warning: The following columns are missing" in captured
    assert filtered is None


# --- Tests for Display Methods ---

def test_display_standard_stats(dummy_player, capture_plot, sample_batter_standard_stats):
    fig, ax = plt.subplots()
    sd = StatsDisplay(dummy_player, 2023, 'batting')
    sd.display_standard_stats(ax)
    assert len(capture_plot) == 1
    call = capture_plot[0]
    assert "Standard" in call['title']
    expected_fields = ['AB', 'H', 'AVG', 'RBI']
    
    # Filter the fixture data to only include the expected fields.
    expected_filtered = {k: v for k, v in sample_batter_standard_stats.items() if k in expected_fields}
    
    # Convert the actual stats to a DataFrame if needed.
    if isinstance(call['stats'], pd.DataFrame):
        actual_df = call['stats'].reset_index(drop=True)
    else:
        actual_df = pd.DataFrame(call['stats']).reset_index(drop=True)
    
    # Ensure we have exactly one row.
    assert len(actual_df) == 1, "Expected one row in the stats DataFrame."
    
    # For each expected field, check that the actual value matches the expected value.
    for field in expected_fields:
        actual_value = actual_df.at[0, field]
        expected_value = expected_filtered[field]
        assert actual_value == expected_value, f"Field {field} mismatch: expected {expected_value}, got {actual_value}"
    
    plt.close(fig)


def test_display_advanced_stats(dummy_player, capture_plot, sample_batter_advanced_stats):
    fig, ax = plt.subplots()
    sd = StatsDisplay(dummy_player, 2023, 'batting')
    sd.display_advanced_stats(ax)
    assert len(capture_plot) == 1
    call = capture_plot[0]
    assert "Advanced" in call['title']
    expected_fields = ['OBP', 'SLG', 'OPS']
    
    # Filter the fixture data to include only expected fields.
    expected_filtered = {k: v for k, v in sample_batter_advanced_stats.items() if k in expected_fields}
    
    # Convert the actual stats to a DataFrame.
    if isinstance(call['stats'], pd.DataFrame):
        actual_df = call['stats'].reset_index(drop=True)
    else:
        actual_df = pd.DataFrame(call['stats']).reset_index(drop=True)
    
    # Ensure that there is exactly one row.
    assert len(actual_df) == 1, "Expected one row in the advanced stats DataFrame."
    
    # Check that each expected field has the correct value.
    for field in expected_fields:
        actual_value = actual_df.at[0, field]
        expected_value = expected_filtered.get(field)
        assert actual_value == expected_value, f"Mismatch for field '{field}': expected {expected_value}, got {actual_value}"
    
    plt.close(fig)



def test_plot_splits_stats(dummy_player, capture_plot, sample_batter_stat_splits):
    fig, ax = plt.subplots()
    sd = StatsDisplay(dummy_player, 2023, 'batting')
    sd.plot_splits_stats(ax)
    assert len(capture_plot) == 1
    call = capture_plot[0]
    assert "Splits" in call['title']
    
    # Define expected fields based on the keys in the sample fixture.
    expected_fields = ['atBats', 'hits', 'avg', 'rbi']
    
    # Build expected DataFrame from the entire sample_batter_stat_splits fixture:
    # For each split in the fixture, extract its "stat" dictionary and filter by expected_fields.
    expected_stats = [
        {k: v for k, v in split.get('stat', {}).items() if k in expected_fields}
        for split in sample_batter_stat_splits
    ]
    expected_df = pd.DataFrame(expected_stats).reset_index(drop=True)
    
    # Process the actual stats from the call: extract the "stat" field from each split and filter by expected_fields.
    actual_stats = [
        {k: v for k, v in split.get('stat', {}).items() if k in expected_fields}
        for split in call['stats'] if 'stat' in split
    ]
    actual_df = pd.DataFrame(actual_stats).reset_index(drop=True)
    
    pd.testing.assert_frame_equal(actual_df, expected_df, check_like=True)
    plt.close(fig)

