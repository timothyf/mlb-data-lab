import os
import pytest
import pandas as pd
import matplotlib.pyplot as plt

from mlb_data_lab.data_viz.stats_table import StatsTable
from mlb_data_lab.config import StatsDisplayConfig
from mlb_data_lab.config import StatsConfig
from mlb_data_lab.apis.mlb_stats_client import process_splits



# --- Fixtures to create StatsTable instances for each data type ---

@pytest.fixture
def stats_table_standard(sample_batter_stats):
    stats_list = StatsConfig().stat_lists['batting']['standard']
    stats_df = pd.DataFrame([sample_batter_stats])
    return StatsTable(stats_df, stats_list, stat_type='batting')

@pytest.fixture
def stats_table_advanced(sample_batter_stats):
    stats_list = StatsConfig().stat_lists['batting']['advanced']
    df = pd.DataFrame([sample_batter_stats])
    return StatsTable(df, stats_list, stat_type='batting')

@pytest.fixture
def stats_table_splits(sample_batter_stat_splits):
    data = process_splits(sample_batter_stat_splits)
    stats_list = StatsConfig().stat_lists['batting']['splits']
    #df = pd.DataFrame([data])
    return StatsTable(data, stats_list, stat_type='batting')


# --- Tests for StatsTable methods ---

def test_sanitize_text(stats_table_standard):
    input_text = "Hello@World!"
    expected = "HelloWorld"
    result = stats_table_standard.sanitize_text(input_text)
    assert result == expected

def test_create_table_non_splits_standard(stats_table_standard):
    fig, ax = plt.subplots()
    stats_table_standard.create_table(ax, title="Standard Table", is_splits=False)
    tables = ax.tables
    assert len(tables) >= 1, "No table created on Axes for standard data"
    table = tables[0]
    
    # Get expected headers from the real configuration.
    config = StatsDisplayConfig().batting
    expected_headers = {config['AB']['table_header'], config['H']['table_header'],
                        config['AVG']['table_header'], config['RBI']['table_header']}
    header_texts = {cell.get_text().get_text() for key, cell in table.get_celld().items() if key[0] == 0}
    assert expected_headers.issubset(header_texts), f"Headers {header_texts} do not include expected {expected_headers}"
    plt.close(fig)

def test_create_table_non_splits_advanced(stats_table_advanced):
    fig, ax = plt.subplots()
    stats_table_advanced.create_table(ax, title="Advanced Table", is_splits=False)
    tables = ax.tables
    assert len(tables) >= 1, "No table created on Axes for advanced data"
    table = tables[0]
    config = StatsDisplayConfig().batting
    # For advanced stats, expected headers come from advanced keys.
    expected_headers = {config.get('OBP', {'table_header': 'OBP'})['table_header'],
                        config.get('SLG', {'table_header': 'SLG'})['table_header'],
                        config.get('OPS', {'table_header': 'OPS'})['table_header']}
    header_texts = {cell.get_text().get_text() for key, cell in table.get_celld().items() if key[0] == 0}
    assert expected_headers.issubset(header_texts), f"Headers {header_texts} do not include expected {expected_headers}"
    plt.close(fig)

def test_create_table_splits(stats_table_splits):
    fig, ax = plt.subplots()
    stats_table_splits.create_table(ax, title="Splits Table", is_splits=True)
    tables = ax.tables
    assert len(tables) >= 1, "No table created on Axes for splits data"
    table = tables[0]
    header_texts = {cell.get_text().get_text() for key, cell in table.get_celld().items() if key[0] == 0}
    # For splits, the header should include "Split" as the first column.
    assert "Split" in header_texts, "Missing 'Split' header in splits table"
    plt.close(fig)

