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
        fontsize = 14 if is_splits else 18  # Set font size based on whether it's split data

        # Ensure the column can hold strings (object dtype)
        data = self.data.astype('object')

        # Ensure only valid columns are reindexed
        valid_columns = [col for col in self.stat_list if col in data.columns]
        data = data.reindex(columns=valid_columns)

        if data.empty:
            print("Warning: Data is empty.")
            return

        # Prepare for multiple rows (vs LHP and vs RHP)
        cell_text = []  # This will store all rows of data

        # Check if we're dealing with splits data
        if is_splits:
            if isinstance(data.index, pd.MultiIndex):
                # Get the split names from the first level of the MultiIndex
                split_names = data.index.get_level_values(0).unique()
            else:
                print("The index is not a MultiIndex.")

        # Only reset the index if it's not splits
        if not is_splits:
            # Reset the index to ensure 0 exists for non-split data
            data.reset_index(drop=True, inplace=True)

        # Modify column headers based on whether we're displaying splits
        if is_splits:
            col_labels = ['Split'] + valid_columns
        else:
            col_labels = [self.stats_display_config[col]['table_header'] for col in valid_columns if col in self.stats_display_config]

        # Ensure that each row in cell_text has the same number of elements as col_labels
        # Check for alignment of cell_text rows with col_labels
        # Loop through each row in the data to format the values
        for index, row in data.iterrows():
            formatted_values = []

            # If this is splits data, add the split name as the first column value
            if is_splits:
                # Ensure index is either a tuple or an integer and handle accordingly
                if isinstance(index, tuple):
                    split_index = index[0]  # Use the first value of the tuple for the split name
                else:
                    split_index = index

                # Check if the split_index exists in split_names (membership check instead of indexing)
                split_name = split_index if split_index in split_names else "Unknown Split"

                # If split_name is a tuple (e.g., from MultiIndex), join its elements into a string
                if isinstance(split_name, tuple):
                    split_name = " - ".join(map(str, split_name))

                formatted_values.append(split_name)

            # Format the rest of the values
            for col in data.columns:
                if col in row and pd.notna(row[col]) and row[col] != '---':
                    formatted_value = Utils.format_stat(row[col], self.stats_display_config[col]['format']) if 'format' in self.stats_display_config[col] else row[col]
                else:
                    formatted_value = '---'
                formatted_values.append(formatted_value)

            # Add the formatted row to cell_text, ensuring it matches the number of col_labels
            if len(formatted_values) == len(col_labels):
                cell_text.append(formatted_values)
            else:
                print(f"Skipping row {index} due to mismatch in length.")



        # Modify column headers based on whether we're displaying splits
        if is_splits:
            col_labels = ['Split'] + valid_columns
        else:
            #col_labels = valid_columns
            # Assuming valid_columns contains the column keys like 'G', 'gamesPlayed', etc.
            col_labels = [self.stats_display_config[col]['table_header'] for col in valid_columns if col in self.stats_display_config]

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


    def to_html_js(self, title: str = None, is_splits=False):
        """Convert the stats table to an HTML table with optional JavaScript"""
        # Ensure only valid columns are used
        valid_columns = [col for col in self.stat_list if col in self.data.columns]
        data = self.data[valid_columns].fillna('---')  # Fill any NaNs with placeholder

        # Start building HTML string
        html = "<table border='1'>\n"
        
        # Add title, if available
        if title:
            html += f"<caption>{title}</caption>\n"
        
        # Create the header
        html += "  <thead>\n    <tr>\n"
        if is_splits:
            html += "      <th>Split</th>\n"  # Add "Split" column if it's splits data
        for col in valid_columns:
            html += f"      <th>{self.sanitize_text(col)}</th>\n"
        html += "    </tr>\n  </thead>\n"
        
        # Create the body
        html += "  <tbody>\n"
        for index, row in data.iterrows():
            html += "    <tr>\n"
            if is_splits:
                # Assuming you want to insert split data in the first column (you can modify as needed)
                html += f"      <td>{row.name}</td>\n"
            for col in valid_columns:
                value = Utils.format_stat(row[col], self.stats_display_config[col]['format']) if row[col] != '---' else '---'
                html += f"      <td>{self.sanitize_text(str(value))}</td>\n"
            html += "    </tr>\n"
        html += "  </tbody>\n</table>\n"

        # Add optional JavaScript for table sorting (simple example)
        html += """
        <script>
            function sortTable(n) {
              var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
              table = document.querySelector("table");
              switching = true;
              dir = "asc"; 
              while (switching) {
                switching = false;
                rows = table.rows;
                for (i = 1; i < (rows.length - 1); i++) {
                  shouldSwitch = false;
                  x = rows[i].getElementsByTagName("TD")[n];
                  y = rows[i + 1].getElementsByTagName("TD")[n];
                  if (dir == "asc") {
                    if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                      shouldSwitch = true;
                      break;
                    }
                  } else if (dir == "desc") {
                    if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                      shouldSwitch = true;
                      break;
                    }
                  }
                }
                if (shouldSwitch) {
                  rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                  switching = true;
                  switchcount ++; 
                } else {
                  if (switchcount == 0 && dir == "asc") {
                    dir = "desc";
                    switching = true;
                  }
                }
              }
            }
        </script>
        """

        return html
