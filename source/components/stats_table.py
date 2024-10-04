import matplotlib.pyplot as plt
import pandas as pd
from typing import List
from utils import Utils
from config import StatsDisplayConfig



class StatsTable:

    def __init__(self, data: pd.DataFrame, stat_list: List[str], stat_type: str = 'batting'):
        self.data = data
        self.stat_list = stat_list
        self.stats_display_config = getattr(StatsDisplayConfig(), stat_type)
        

    def create_table(self, ax: plt.Axes, fontsize: int = 20, title: str = None):
        # Ensure the column can hold strings (object dtype)
        data = self.data.astype('object')

        # Assign the formatted values
        data.loc[0] = [
            Utils.format_stat(data[x][0], self.stats_display_config[x]['format'])
            if data[x][0] != '---' else '---' 
            for x in data
        ]

        table_fg = ax.table(cellText=data.values, colLabels=self.stat_list, cellLoc='center', bbox=[0.00, 0.0, 1, 1])
        table_fg.set_fontsize(fontsize)

        # Adjust column headers
        new_column_names = [
            self.stats_display_config[x]['table_header'] if x in data else '---' for x in self.stat_list
        ]
        for i, col_name in enumerate(new_column_names):
            table_fg.get_celld()[(0, i)].get_text().set_text(col_name)

        ax.set_title(title, fontsize=18, pad=10, fontweight='bold')

        ax.axis('off')

