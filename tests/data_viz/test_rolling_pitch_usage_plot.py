# test_rolling_pitch_usage_plot.py
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick  # for checking tick formatting
import pytest

from mlb_data_lab.data_viz.rolling_pitch_usage_plot import RollingPitchUsagePlot

# --- Sample Data and Fixtures --- #

@pytest.fixture
def sample_pitch_data():
    """
    Create a small sample DataFrame for testing.
    This sample simulates two games with three unique pitch types:
    Game 1: 'FF' and 'SL' are thrown.
    Game 2: 'FF' and 'CU' are thrown.
    
    The grouping in build_complete_pitch_data should result in data for all three pitch types in each game.
    """
    data = {
        'game_pk': [1, 1, 2, 2],
        'game_date': pd.to_datetime(['2021-04-01', '2021-04-01', '2021-04-02', '2021-04-02']),
        'pitch_type': ['FF', 'SL', 'FF', 'CU'],
        'release_speed': [90, 88, 91, 92]
    }
    return pd.DataFrame(data)

@pytest.fixture
def plot_object():
    """
    Create an instance of RollingPitchUsagePlot.
    (The player parameter isn’t used in the plotting so a dummy value is fine.)
    """
    return RollingPitchUsagePlot(player="Test Pitcher")

# --- Test individual methods --- #

def test_get_color_mapping(plot_object):
    """Test that get_color_mapping returns a valid dictionary with expected keys."""
    color_mapping = plot_object.get_color_mapping()
    # We assume pitch_colors was imported in the module.
    from mlb_data_lab.constants import pitch_colors
    assert isinstance(color_mapping, dict)
    for key in pitch_colors:
        assert key in color_mapping
        assert isinstance(color_mapping[key], str)

def test_build_complete_pitch_data(plot_object, sample_pitch_data):
    """
    Test that build_complete_pitch_data returns a DataFrame
    with the expected game-pitch type combinations and that missing combinations
    are filled with 0.
    """
    complete_data, game_list = plot_object.build_complete_pitch_data(sample_pitch_data)
    # The sample has 2 games and, across the sample, three pitch types: 'FF', 'SL', 'CU'.
    # So the complete DataFrame should have 2 * 3 = 6 rows.
    assert complete_data.shape[0] == 6

    # Check that the missing combination for game 1 and 'CU' is added and its release_speed is 0.
    row = complete_data[(complete_data['game_pk'] == 1) & (complete_data['pitch_type'] == 'CU')]
    assert not row.empty
    assert row.iloc[0]['release_speed'] == 0

    # Check that mapping columns are present.
    assert 'game_date' in complete_data.columns
    assert 'game_number' in complete_data.columns

    # Also, verify that game_list contains the expected games.
    np.testing.assert_array_equal(np.sort(game_list), np.array([1, 2]))

def test_plot_rolling_usage(plot_object, sample_pitch_data):
    """
    Test the rolling usage plot for each pitch type.
    We use window=1 to make the rolling average equal to the original values.
    """
    complete_data, game_list = plot_object.build_complete_pitch_data(sample_pitch_data)
    fig, ax = plt.subplots()
    dict_color = plot_object.get_color_mapping()

    # Use window = 1
    max_roll_values = plot_object.plot_rolling_usage(
        complete_data, sample_pitch_data, window=1, ax=ax, dict_color=dict_color
    )
    # The original sample has three unique pitch types.
    unique_pitch_types = sample_pitch_data['pitch_type'].unique()
    assert len(max_roll_values) == len(unique_pitch_types)

    # For window=1, the rolling average is just the original proportion.
    # Check that the maximum rolling value for each pitch type equals the maximum proportion in the complete data.
    for pitch in unique_pitch_types:
        subset = complete_data[complete_data['pitch_type'] == pitch]['release_speed']
        expected_max = np.nanmax(subset)
        assert any(np.isclose(expected_max, mrv, atol=1e-5) for mrv in max_roll_values)

    plt.close(fig)

def test_set_axes_limits_and_labels(plot_object):
    """
    Test that set_axes_limits_and_labels correctly sets x and y limits and axis labels.
    """
    fig, ax = plt.subplots()
    # Dummy game list and max_roll_values.
    game_list = [1, 2, 3, 4, 5]
    max_roll_values = [0.2, 0.5, 0.8]
    window = 2

    plot_object.set_axes_limits_and_labels(ax, game_list, window, max_roll_values)
    # x-axis should begin at the window and end at the total number of games.
    xlim = ax.get_xlim()
    assert xlim[0] == window
    assert xlim[1] == len(game_list)

    # Expected y-axis upper limit
    max_value = max(max_roll_values)
    expected_ylim = math.ceil(max_value * 10) / 10
    ylim = ax.get_ylim()
    assert ylim[0] == 0
    assert np.isclose(ylim[1], expected_ylim)

    # Test that labels and title are set.
    assert ax.get_xlabel() != ""
    assert ax.get_ylabel() != ""
    assert ax.get_title() != ""
    plt.close(fig)

def test_plot_integration(plot_object, sample_pitch_data):
    """
    Integration test for the top-level plot method.
    As long as no exceptions are raised and the axes have labels, we consider it a pass.
    """
    fig, ax = plt.subplots()
    window = 1
    plot_object.plot(sample_pitch_data, ax, window)

    # Check that axis labels and title are set.
    assert ax.get_xlabel() != ""
    assert ax.get_ylabel() != ""
    assert ax.get_title() != ""
    plt.close(fig)
