# Standard library imports
import os

# Third-party library imports
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import colors as mcolors

# Local application-specific imports
from mlb_summary_sheets.config import DATA_DIR
from mlb_summary_sheets.constants import (
    pitch_colors, 
    pitch_stats_dict, 
    color_stats, 
    cmap_sum, 
    cmap_sum_r, 
    pitch_summary_columns
)


class PitchBreakdownTable:

    def __init__(self, data):
        self.data = data


    def group_and_summarize_pitching_data(self, pitch_data: pd.DataFrame):
        # Create a dictionary mapping pitch types to their colors
        dict_color = dict(zip(pitch_colors.keys(), [pitch_colors[key]['color'] for key in pitch_colors]))
        dict_pitch = dict(zip(pitch_colors.keys(), [pitch_colors[key]['name'] for key in pitch_colors]))

        # Group the DataFrame by pitch type and aggregate various statistics
        pitch_summary = pitch_data.groupby(['pitch_type']).agg(
                            pitch = ('pitch_type','count'),  # Count of pitches
                            release_speed = ('release_speed','mean'),  # Average release speed
                            pfx_z = ('pfx_z','mean'),  # Average vertical movement
                            pfx_x = ('pfx_x','mean'),  # Average horizontal movement
                            release_spin_rate = ('release_spin_rate','mean'),  # Average spin rate
                            release_pos_x = ('release_pos_x','mean'),  # Average horizontal release position
                            release_pos_z = ('release_pos_z','mean'),  # Average vertical release position
                            release_extension = ('release_extension','mean'),  # Average release extension
                            delta_run_exp = ('delta_run_exp','sum'),  # Total change in run expectancy
                            swing = ('swing','sum'),  # Total swings
                            whiff = ('whiff','sum'),  # Total whiffs
                            in_zone = ('in_zone','sum'),  # Total in-zone pitches
                            out_zone = ('out_zone','sum'),  # Total out-of-zone pitches
                            chase = ('chase','sum'),  # Total chases
                            xwoba = ('estimated_woba_using_speedangle','mean'),  # Average expected wOBA
                        ).reset_index()

        # Map pitch types to their descriptions
        pitch_summary['pitch_description'] = pitch_summary['pitch_type'].map(dict_pitch)

        # Calculate pitch usage as a percentage of total pitches
        pitch_summary['pitch_usage'] = pitch_summary['pitch'] / pitch_summary['pitch'].sum()

        # Calculate whiff rate as the ratio of whiffs to swings
        pitch_summary['whiff_rate'] = pitch_summary['whiff'] / pitch_summary['swing']

        # Calculate in-zone rate as the ratio of in-zone pitches to total pitches
        pitch_summary['in_zone_rate'] = pitch_summary['in_zone'] / pitch_summary['pitch']

        # Calculate chase rate as the ratio of chases to out-of-zone pitches
        pitch_summary['chase_rate'] = pitch_summary['chase'] / pitch_summary['out_zone']

        # Calculate delta run expectancy per 100 pitches
        pitch_summary['delta_run_exp_per_100'] = -pitch_summary['delta_run_exp'] / pitch_summary['pitch'] * 100

        # Map pitch types to their colors
        pitch_summary['color'] = pitch_summary['pitch_type'].map(dict_color)

        # Sort the DataFrame by pitch usage in descending order
        pitch_summary = pitch_summary.sort_values(by='pitch_usage', ascending=False)
        color_list = pitch_summary['color'].tolist()

        pitch_count = pitch_data['pitch_type'].count()
        swing_count = pitch_data['swing'].sum()
        out_zone_count = pitch_data['out_zone'].sum()
        if pitch_count > 0:
            delta_run_exp_per_100 = (pitch_data['delta_run_exp'].sum() / pitch_count) * -100
            in_zone_rate = pitch_data['in_zone'].sum() / pitch_count
        else:
            delta_run_exp_per_100 = 0  
            in_zone_rate = 0
        if swing_count > 0:
            whiff_rate = pitch_data['whiff'].sum() / swing_count
        else:
            whiff_rate = 0
        if out_zone_count > 0:
            chase_rate = pitch_data['chase'].sum() / out_zone_count
        else:
            chase_rate = 0

        aggregated_pitch_totals = pd.DataFrame(data={
                    'pitch_type': 'All',
                    'pitch_description': 'All',  # Description for the summary row
                    'pitch': pitch_data['pitch_type'].count(),  # Total count of pitches
                    'pitch_usage': 1,  # Usage percentage for all pitches (100%)
                    'release_speed': np.nan,  # Placeholder for release speed
                    'pfx_z': np.nan,  # Placeholder for vertical movement
                    'pfx_x': np.nan,  # Placeholder for horizontal movement
                    'release_spin_rate': np.nan,  # Placeholder for spin rate
                    'release_pos_x': np.nan,  # Placeholder for horizontal release position
                    'release_pos_z': np.nan,  # Placeholder for vertical release position
                    'release_extension': pitch_data['release_extension'].mean(),  # Placeholder for release extension
                    'delta_run_exp_per_100': delta_run_exp_per_100,  # Delta run expectancy per 100 pitches
                    'whiff_rate': whiff_rate,  # Whiff rate
                    'in_zone_rate': in_zone_rate,  # In-zone rate
                    'chase_rate': chase_rate,  # Chase rate
                    'xwoba': pitch_data['estimated_woba_using_speedangle'].mean()  # Average expected wOBA
                }, index=[0])

        # Concatenate the group DataFrame with the summary row DataFrame
        final_pitch_summary = pd.concat([pitch_summary, aggregated_pitch_totals], ignore_index=True)

        return final_pitch_summary, color_list

    def plot(self, pitch_data: pd.DataFrame, ax: plt.Axes, league_pitch_avgs: pd.DataFrame, fontsize: int = 20):
        grouped_pitch_data, color_list = self.group_and_summarize_pitching_data(pitch_data)
        cell_colors = self.generate_stat_colormap(grouped_pitch_data, league_pitch_avgs, color_stats, cmap_sum, cmap_sum_r)
        formatted_pitch_data = self.format_pitch_stats(grouped_pitch_data)

        # Create a table plot with the DataFrame values and specified column labels
        pitch_stat_table = ax.table(cellText=formatted_pitch_data.values, colLabels=pitch_summary_columns, cellLoc='center',
                            bbox=[0, -0.1, 1, 1],
                            colWidths=[2.5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            cellColours=cell_colors)

        # Disable automatic font size adjustment and set the font size
        pitch_stat_table.auto_set_font_size(False)

        pitch_stat_table.set_fontsize(fontsize)

        # Scale the table plot
        pitch_stat_table.scale(1, 0.5)

        # Correctly format the new column names using LaTeX formatting
        new_column_names = ['$\\bf{Pitch\\ Name}$'] + [pitch_stats_dict[x]['table_header'] if x in pitch_stats_dict else '---' for x in pitch_summary_columns[1:]]

        # Update the table headers with the new column names
        for i, col_name in enumerate(new_column_names):
            pitch_stat_table.get_celld()[(0, i)].get_text().set_text(col_name)

        # Bold the first column in the table
        for i in range(len(formatted_pitch_data)):
            pitch_stat_table.get_celld()[(i+1, 0)].get_text().set_fontweight('bold')

        # Set the color for the first column, all rows except header and last
        for i in range(1, len(formatted_pitch_data)):
            # Check if the pitch type is in the specified list
            if pitch_stat_table.get_celld()[(i, 0)].get_text().get_text() in ['Split-Finger', 'Slider', 'Changeup']:
                pitch_stat_table.get_celld()[(i, 0)].set_text_props(color='#000000', fontweight='bold')
            else:
                pitch_stat_table.get_celld()[(i, 0)].set_text_props(color='#FFFFFF')
            # Set the background color of the cell
            pitch_stat_table.get_celld()[(i, 0)].set_facecolor(color_list[i-1])

        ax.axis('off')


    def generate_stat_colormap(self,
                         grouped_pitch_data: pd.DataFrame,
                        league_pitch_averages: pd.DataFrame,
                        color_stats: list,
                        cmap_sum: matplotlib.colors.LinearSegmentedColormap,
                        cmap_sum_r: matplotlib.colors.LinearSegmentedColormap):
        color_list_df = []
        for pt in grouped_pitch_data.pitch_type.unique():
            color_list_df_inner = []
            pitch_type_data = league_pitch_averages[league_pitch_averages['pitch_type'] == pt]
            pitch_type_summary = grouped_pitch_data[grouped_pitch_data['pitch_type'] == pt]

            for tb in pitch_summary_columns:

                if tb in color_stats and type(pitch_type_summary[tb].values[0]) == np.float64:
                    if np.isnan(pitch_type_summary[tb].values[0]):
                        color_list_df_inner.append('#ffffff')
                    elif tb == 'release_speed':
                        normalize = mcolors.Normalize(vmin=(pd.to_numeric(pitch_type_data[tb], errors='coerce')).mean() * 0.95,
                                                    vmax=(pd.to_numeric(pitch_type_data[tb], errors='coerce')).mean() * 1.05)
                        color_list_df_inner.append(self.map_value_to_color((pd.to_numeric(pitch_type_summary[tb], errors='coerce')).mean(), normalize, cmap_sum))
                    elif tb == 'delta_run_exp_per_100':
                        normalize = mcolors.Normalize(vmin=-1.5, vmax=1.5)
                        color_list_df_inner.append(self.map_value_to_color((pd.to_numeric(pitch_type_summary[tb], errors='coerce')).mean(), normalize, cmap_sum))
                    elif tb == 'xwoba':
                        normalize = mcolors.Normalize(vmin=(pd.to_numeric(pitch_type_data[tb], errors='coerce')).mean() * 0.7,
                                                    vmax=(pd.to_numeric(pitch_type_data[tb], errors='coerce')).mean() * 1.3)
                        color_list_df_inner.append(self.map_value_to_color((pd.to_numeric(pitch_type_summary[tb], errors='coerce')).mean(), normalize, cmap_sum_r))
                    else:
                        normalize = mcolors.Normalize(vmin=(pd.to_numeric(pitch_type_data[tb], errors='coerce')).mean() * 0.7,
                                                    vmax=(pd.to_numeric(pitch_type_data[tb], errors='coerce')).mean() * 1.3)
                        color_list_df_inner.append(self.map_value_to_color((pd.to_numeric(pitch_type_summary[tb], errors='coerce')).mean(), normalize, cmap_sum))
                else:
                    color_list_df_inner.append('#ffffff')
            color_list_df.append(color_list_df_inner)
        return color_list_df
    
    def map_value_to_color(self, value, normalize, cmap_sum):
        color = cmap_sum(normalize(value))
        return mcolors.to_hex(color)
    
    def format_pitch_stats(self, pitch_stats: pd.DataFrame):
        # Create a DataFrame for the summary row with aggregated statistics for all pitches
        # Fill missing values with '—' and then infer the correct data types for object columns
        # Enable future behavior to suppress the warning
        pd.set_option('future.no_silent_downcasting', True)

        # Fill missing values and ensure future behavior is handled
        formatted_pitch_stats = pitch_stats[pitch_summary_columns].fillna('—').infer_objects(copy=False)



        # Apply the formats to the DataFrame
        # Iterate over each column in pitch_stats_dict
        for column, props in pitch_stats_dict.items():
            # Check if the column exists in df_plot
            if column in formatted_pitch_stats.columns:
                # Apply the specified format to the column values
                formatted_pitch_stats[column] = formatted_pitch_stats[column].apply(lambda x: format(x, props['format']) if isinstance(x, (int, float)) else x)
        return formatted_pitch_stats

