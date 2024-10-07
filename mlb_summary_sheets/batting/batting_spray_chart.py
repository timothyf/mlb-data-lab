import numpy as np
import matplotlib.lines as mlines
import mplcursors
from mlb_summary_sheets.constants import statcast_events
from mlb_summary_sheets.constants import event_styles


class BattingSprayChart:
    def __init__(self, player_id, events=statcast_events['hit_events']):
        self.player_id = player_id
        self.events = events


    def plot(self, ax, statcast_data, title):
        # Fetch data for a specific player and time period
        data = statcast_data.copy()

        # Filter for events passed in the constructor
        data = data[data['events'].isin(self.events)]

        # Drop rows with missing hit coordinates (important for valid plotting)
        data = data.dropna(subset=['hc_x', 'hc_y'])

        data['color'] = data['events'].map(lambda event: event_styles[event]['color'] if event in event_styles else 'black')
        data['marker'] = data['events'].map(lambda event: event_styles[event]['marker'] if event in event_styles else 'o')

        # Transform Statcast coordinates (adjust scaling for alignment)
        data['trans_hc_x'] = (data['hc_x'] - 125.42)
        data['trans_hc_y'] = (198.27 - data['hc_y'])

        # Adjust xlim and ylim to align the field and points correctly
        ax.set_xlim(data['trans_hc_x'].min() - 10, data['trans_hc_x'].max() + 10)
        ax.set_ylim(data['trans_hc_y'].min() - 10, data['trans_hc_y'].max() + 10)

        # Draw the infield baselines at 45-degree angles (the diamond)
        diamond_size = 0.2 * (ax.get_xlim()[1] - ax.get_xlim()[0])  # 20% of the x-range

        ax.plot([0, diamond_size], [0, diamond_size], color='lightgray')  # Home to 1st base
        ax.plot([0, -diamond_size], [0, diamond_size], color='lightgray')  # Home to 3rd base
        ax.plot([diamond_size, 0, -diamond_size], [diamond_size, diamond_size * 2, diamond_size], color='lightgray')  # 1st to 2nd to 3rd base

        # List to keep track of scatter plots
        scatter_plots = []

        # Iterate through each unique marker and plot the points with that marker
        for marker_style in data['marker'].unique():
            subset = data[data['marker'] == marker_style]  # Filter data for this marker style
            scatter = ax.scatter(subset['trans_hc_x'], subset['trans_hc_y'], c=subset['color'], marker=marker_style, s=40)
            scatter_plots.append(scatter)  # Store scatter plot

        # Apply mplcursors to all scatter plots
        cursor = mplcursors.cursor(scatter_plots, hover=True)

        # Customize the click annotation
        @cursor.connect("add")
        def on_add(sel):
            index = sel.index
            sel.annotation.set_text(
                f"Event: {data.iloc[index]['events']}\n"
                f"EV: {data.iloc[index]['launch_speed']} mph\n"
                f"Distance: {data.iloc[index]['hit_distance_sc']} ft\n"
                f"Game: {data.iloc[index]['game_date']}\n"
                f"Location: ({data.iloc[index]['hc_x']}, {data.iloc[index]['hc_y']})\n"
            )
            sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9)  # Styling the annotation box

        ax.set_title(title, fontweight='bold', fontsize=18, pad=20)

        
        # # Define custom legend handles for each hit type
        # single = mlines.Line2D([], [], color='blue', marker='o', linestyle='None', markersize=8, label='1B')
        # double = mlines.Line2D([], [], color='green', marker='o', linestyle='None', markersize=8, label='2B')
        # triple = mlines.Line2D([], [], color='lightblue', marker='o', linestyle='None', markersize=8, label='3B')
        # home_run = mlines.Line2D([], [], color='red', marker='o', linestyle='None', markersize=8, label='HR')

        legend_handles = []
        # Variable to track if we have already added the 'Out' legend handle
        out_legend_added = False

        # Iterate through events to dynamically create legend handles based on event_styles
        for event in self.events:
            if event in event_styles:
                style = event_styles[event]

                # If the event is an out type, group them under a single 'Out' label
                if event in statcast_events['out_events']:
                    if not out_legend_added:
                        # Create a single legend handle for all out types
                        legend_handle = mlines.Line2D(
                            [], [], 
                            color='grey', 
                            marker='x', 
                            linestyle='None', 
                            markersize=8, 
                            label='Out'  # Single label for all out events
                        )
                        legend_handles.append(legend_handle)
                        out_legend_added = True
                else:
                    # Create legend handles for non-out events individually
                    legend_handle = mlines.Line2D(
                        [], [], 
                        color=style['color'], 
                        marker=style['marker'], 
                        linestyle='None', 
                        markersize=8, 
                        label=style['label']
                    )
                    legend_handles.append(legend_handle)

        # Add the legend to the plot
        ax.legend(handles=legend_handles, loc='lower right', bbox_to_anchor=(1.1, 0))


        # Ensure the aspect ratio is equal to avoid vertical compression
        ax.set_aspect('equal')

        ax.axis('off')

        # Move the plot down by adjusting y0 (shift it slightly down if needed)
        pos = ax.get_position()
        new_pos = [pos.x0, pos.y0 - 0.05, pos.width, pos.height * 0.9]  # Slightly reducing the height

        ax.set_position(new_pos)




