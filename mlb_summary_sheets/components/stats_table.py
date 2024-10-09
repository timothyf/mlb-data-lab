import matplotlib.pyplot as plt
import pandas as pd
from typing import List
from mlb_summary_sheets.utils import Utils
from mlb_summary_sheets.config import StatsDisplayConfig



class StatsTable:

    def __init__(self, data: pd.DataFrame, stat_list: List[str], stat_type: str = 'batting'):
        self.data = data
        self.stat_list = stat_list
        self.stats_display_config = getattr(StatsDisplayConfig(), stat_type)


    def sanitize_text(self, text):
        return ''.join(e for e in text if e.isalnum() or e.isspace() or e in ['-', '_', '.', ',', '/'])
        
    def create_table(self, ax: plt.Axes, title: str = None, is_splits=False):

        if is_splits:
            fontsize = 14
        else:
            fontsize = 18  # Set a consistent font size for the table

        # Ensure the column can hold strings (object dtype)
        data = self.data.astype('object')

        # Ensure only valid columns are reindexed
        valid_columns = [col for col in self.stat_list if col in data.columns]
        data = data.reindex(columns=valid_columns)

        # Reset the index to ensure 0 exists
        data.reset_index(drop=True, inplace=True)

        if data.empty:
            print("Warning: Data is empty.")

        # Prepare for multiple rows (vs LHP and vs RHP)
        cell_text = []  # This will store all rows of data

        # Check if we're dealing with splits data
        if is_splits:
            split_names = data.index.get_level_values(0).unique() if isinstance(data.index, pd.MultiIndex) else ['vs LHP', 'vs RHP', 'Ahead', 'Behind']

        # Loop through each row in the data to format the values
        for index, row in data.iterrows():
            formatted_values = []

            # If this is splits data, add the split name as the first column value
            if is_splits:
                split_name = split_names[index] if index < len(split_names) else "Unknown Split"
                formatted_values.append(split_name)

            # Format the rest of the values
            for x in data.columns:
                if x in row and row[x] != '---':
                    formatted_value = Utils.format_stat(row[x], self.stats_display_config[x]['format'])
                else:
                    formatted_value = '---'
                formatted_values.append(formatted_value)

            # Add the formatted row to cell_text
            cell_text.append(formatted_values)

        # Modify column headers based on whether we're displaying splits
        if is_splits:
            col_labels = ['Split'] + valid_columns
        else:
            col_labels = valid_columns

        # Create table with aligned data and column headers
        table_fg = ax.table(cellText=cell_text, colLabels=col_labels, cellLoc='center', bbox=[0.00, 0.0, 1, 1])

        # Disable auto-resizing of font size
        table_fg.auto_set_font_size(False)
        table_fg.set_fontsize(fontsize)

        # Set the font size for all data cells (excluding headers)
        for key, cell in table_fg.get_celld().items():
            row, col = key
            cell.set_fontsize(fontsize)

            # Set background color and bold font for header row (row 0)
            if row == 0:
                cell.set_facecolor("#ADD8E6")  # Light blue background color for the header
                cell.set_text_props(fontweight='bold')
                cell.get_text().set_fontweight('bold')

        # Set font family if there's any font issue
        plt.rcParams["font.family"] = "DejaVu Sans"

        ax.set_title(title, fontsize=18, pad=10, fontweight='bold')
        ax.axis('off')

