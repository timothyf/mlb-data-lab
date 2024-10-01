import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from constants import pitch_colors, pitch_stats_dict
from matplotlib import colors as mcolors
import matplotlib
from constants import color_stats, cmap_sum, cmap_sum_r, table_columns




class PitchBreakdownTable:

    def __init__(self, data):
        self.data = data
        #self.pitch_stats_dict = PitchStatsDict()
        self.df_statcast_group = pd.read_csv('statcast_2024_grouped.csv')


    def df_grouping(self, df: pd.DataFrame):
        # Create a dictionary mapping pitch types to their colors
        dict_colour = dict(zip(pitch_colors.keys(), [pitch_colors[key]['colour'] for key in pitch_colors]))
        dict_pitch = dict(zip(pitch_colors.keys(), [pitch_colors[key]['name'] for key in pitch_colors]))

        # Group the DataFrame by pitch type and aggregate various statistics
        df_group = df.groupby(['pitch_type']).agg(
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
        df_group['pitch_description'] = df_group['pitch_type'].map(dict_pitch)

        # Calculate pitch usage as a percentage of total pitches
        df_group['pitch_usage'] = df_group['pitch'] / df_group['pitch'].sum()

        # Calculate whiff rate as the ratio of whiffs to swings
        df_group['whiff_rate'] = df_group['whiff'] / df_group['swing']

        # Calculate in-zone rate as the ratio of in-zone pitches to total pitches
        df_group['in_zone_rate'] = df_group['in_zone'] / df_group['pitch']

        # Calculate chase rate as the ratio of chases to out-of-zone pitches
        df_group['chase_rate'] = df_group['chase'] / df_group['out_zone']

        # Calculate delta run expectancy per 100 pitches
        df_group['delta_run_exp_per_100'] = -df_group['delta_run_exp'] / df_group['pitch'] * 100

        # Map pitch types to their colours
        df_group['colour'] = df_group['pitch_type'].map(dict_colour)

        # Sort the DataFrame by pitch usage in descending order
        df_group = df_group.sort_values(by='pitch_usage', ascending=False)
        colour_list = df_group['colour'].tolist()

        plot_table_all = pd.DataFrame(data={
                    'pitch_type': 'All',
                    'pitch_description': 'All',  # Description for the summary row
                    'pitch': df['pitch_type'].count(),  # Total count of pitches
                    'pitch_usage': 1,  # Usage percentage for all pitches (100%)
                    'release_speed': np.nan,  # Placeholder for release speed
                    'pfx_z': np.nan,  # Placeholder for vertical movement
                    'pfx_x': np.nan,  # Placeholder for horizontal movement
                    'release_spin_rate': np.nan,  # Placeholder for spin rate
                    'release_pos_x': np.nan,  # Placeholder for horizontal release position
                    'release_pos_z': np.nan,  # Placeholder for vertical release position
                    'release_extension': df['release_extension'].mean(),  # Placeholder for release extension
                    'delta_run_exp_per_100': df['delta_run_exp'].sum() / df['pitch_type'].count() * -100,  # Delta run expectancy per 100 pitches
                    'whiff_rate': df['whiff'].sum() / df['swing'].sum(),  # Whiff rate
                    'in_zone_rate': df['in_zone'].sum() / df['pitch_type'].count(),  # In-zone rate
                    'chase_rate': df['chase'].sum() / df['out_zone'].sum(),  # Chase rate
                    'xwoba': df['estimated_woba_using_speedangle'].mean()  # Average expected wOBA
                }, index=[0])

        # Concatenate the group DataFrame with the summary row DataFrame
        df_plot = pd.concat([df_group, plot_table_all], ignore_index=True)


        return df_plot, colour_list

    def plot(self, df: pd.DataFrame, ax: plt.Axes, fontsize: int = 20):
        df_group, colour_list = self.df_grouping(df)
        colour_list_df = self.get_cell_colouts(df_group, self.df_statcast_group, color_stats, cmap_sum, cmap_sum_r)
        df_plot = self.plot_pitch_format(df_group)

        # Create a table plot with the DataFrame values and specified column labels
        table_plot = ax.table(cellText=df_plot.values, colLabels=table_columns, cellLoc='center',
                            bbox=[0, -0.1, 1, 1],
                            colWidths=[2.5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            cellColours=colour_list_df)

        # Disable automatic font size adjustment and set the font size
        table_plot.auto_set_font_size(False)

        table_plot.set_fontsize(fontsize)

        # Scale the table plot
        table_plot.scale(1, 0.5)

        # Correctly format the new column names using LaTeX formatting
        new_column_names = ['$\\bf{Pitch\\ Name}$'] + [pitch_stats_dict[x]['table_header'] if x in pitch_stats_dict else '---' for x in table_columns[1:]]

        # Update the table headers with the new column names
        for i, col_name in enumerate(new_column_names):
            table_plot.get_celld()[(0, i)].get_text().set_text(col_name)

        # Bold the first column in the table
        for i in range(len(df_plot)):
            table_plot.get_celld()[(i+1, 0)].get_text().set_fontweight('bold')

        # Set the color for the first column, all rows except header and last
        for i in range(1, len(df_plot)):
            # Check if the pitch type is in the specified list
            if table_plot.get_celld()[(i, 0)].get_text().get_text() in ['Split-Finger', 'Slider', 'Changeup']:
                table_plot.get_celld()[(i, 0)].set_text_props(color='#000000', fontweight='bold')
            else:
                table_plot.get_celld()[(i, 0)].set_text_props(color='#FFFFFF')
            # Set the background color of the cell
            table_plot.get_celld()[(i, 0)].set_facecolor(colour_list[i-1])

        # Remove the axis
        ax.axis('off')


    def get_cell_colouts(self,
                         df_group: pd.DataFrame,
                        df_statcast_group: pd.DataFrame,
                        colour_stats: list,
                        cmap_sum: matplotlib.colors.LinearSegmentedColormap,
                        cmap_sum_r: matplotlib.colors.LinearSegmentedColormap):
        colour_list_df = []
        for pt in df_group.pitch_type.unique():
            colour_list_df_inner = []
            select_df = df_statcast_group[df_statcast_group['pitch_type'] == pt]
            df_group_select = df_group[df_group['pitch_type'] == pt]

            for tb in table_columns:

                if tb in colour_stats and type(df_group_select[tb].values[0]) == np.float64:
                    if np.isnan(df_group_select[tb].values[0]):
                        colour_list_df_inner.append('#ffffff')
                    elif tb == 'release_speed':
                        normalize = mcolors.Normalize(vmin=(pd.to_numeric(select_df[tb], errors='coerce')).mean() * 0.95,
                                                    vmax=(pd.to_numeric(select_df[tb], errors='coerce')).mean() * 1.05)
                        colour_list_df_inner.append(self.get_color((pd.to_numeric(df_group_select[tb], errors='coerce')).mean(), normalize, cmap_sum))
                    elif tb == 'delta_run_exp_per_100':
                        normalize = mcolors.Normalize(vmin=-1.5, vmax=1.5)
                        colour_list_df_inner.append(self.get_color((pd.to_numeric(df_group_select[tb], errors='coerce')).mean(), normalize, cmap_sum))
                    elif tb == 'xwoba':
                        normalize = mcolors.Normalize(vmin=(pd.to_numeric(select_df[tb], errors='coerce')).mean() * 0.7,
                                                    vmax=(pd.to_numeric(select_df[tb], errors='coerce')).mean() * 1.3)
                        colour_list_df_inner.append(self.get_color((pd.to_numeric(df_group_select[tb], errors='coerce')).mean(), normalize, cmap_sum_r))
                    else:
                        normalize = mcolors.Normalize(vmin=(pd.to_numeric(select_df[tb], errors='coerce')).mean() * 0.7,
                                                    vmax=(pd.to_numeric(select_df[tb], errors='coerce')).mean() * 1.3)
                        colour_list_df_inner.append(self.get_color((pd.to_numeric(df_group_select[tb], errors='coerce')).mean(), normalize, cmap_sum))
                else:
                    colour_list_df_inner.append('#ffffff')
            colour_list_df.append(colour_list_df_inner)
        return colour_list_df
    
    def get_color(self, value, normalize, cmap_sum):
        color = cmap_sum(normalize(value))
        return mcolors.to_hex(color)
    
    def plot_pitch_format(self, df: pd.DataFrame):
        # Create a DataFrame for the summary row with aggregated statistics for all pitches
        df_group = df[table_columns].fillna('—')

        # Apply the formats to the DataFrame
        # Iterate over each column in pitch_stats_dict
        for column, props in pitch_stats_dict.items():
            # Check if the column exists in df_plot
            if column in df_group.columns:
                # Apply the specified format to the column values
                df_group[column] = df_group[column].apply(lambda x: format(x, props['format']) if isinstance(x, (int, float)) else x)
        return df_group

