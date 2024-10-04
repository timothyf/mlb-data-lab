import numpy as np
import matplotlib.lines as mlines
import mplcursors
from constants import event_type_colors
from constants import statcast_events


class BattingSprayChart:
    def __init__(self, player_id, year, events=statcast_events['hit_events']):
        self.player_id = player_id
        self.year = year
        self.start_date = f'{year}-03-28'
        self.end_date = f'{year}-10-01'
        self.events = events


    def plot(self, ax, statcast_data):
        # Fetch data for a specific player and time period
        data = statcast_data.copy()

        # Filter for events passed in the constructor
        data = data[data['events'].isin(self.events)]

        data['color'] = data['events'].map(event_type_colors)

        # Transform Statcast coordinates (adjust scaling for alignment)
        data['trans_hc_x'] = (data['hc_x'] - 125.42)
        data['trans_hc_y'] = (198.27 - data['hc_y'])

        # Draw the infield baselines at 45-degree angles (the diamond)
        # Reduce the diamond size by adjusting the length of the baselines
        diamond_size = 30  # Reduce the size of the diamond

        ax.plot([0, diamond_size], [0, diamond_size], color='lightgray')  # Home to 1st base
        ax.plot([0, -diamond_size], [0, diamond_size], color='lightgray')  # Home to 3rd base
        ax.plot([diamond_size, 0, -diamond_size], [diamond_size, diamond_size * 2, diamond_size], color='lightgray')  # 1st to 2nd to 3rd base

        # Plot the transformed batted balls with custom colors
        scatter = ax.scatter(data['trans_hc_x'], data['trans_hc_y'], c=data['color'], s=40)

        # Add interactive click with mplcursors
        cursor = mplcursors.cursor(scatter, hover=True)

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

        ax.set_title("Hit Spray Chart", fontweight='bold', fontsize=18, pad=20)

        # Define custom legend handles for each hit type
        single = mlines.Line2D([], [], color='blue', marker='o', linestyle='None', markersize=8, label='1B')
        double = mlines.Line2D([], [], color='green', marker='o', linestyle='None', markersize=8, label='2B')
        triple = mlines.Line2D([], [], color='lightblue', marker='o', linestyle='None', markersize=8, label='3B')
        home_run = mlines.Line2D([], [], color='red', marker='o', linestyle='None', markersize=8, label='HR')

        # Add the legend to the plot
        ax.legend(handles=[single, double, triple, home_run], loc='upper right', bbox_to_anchor=(1.1, 1))

        # Adjust xlim and ylim to align the field and points correctly
        ax.set_xlim(-170, 170)
        ax.set_ylim(-50, 220)  # Increase the y-limit to give more space vertically

        # Ensure the aspect ratio is equal to avoid vertical compression
        ax.set_aspect('equal')

        ax.axis('off')

        # Move the plot down by adjusting y0 (shift it slightly down if needed)
        pos = ax.get_position()
        new_pos = [pos.x0, pos.y0 - 0.05, pos.width, pos.height]  # Slightly smaller shift
        ax.set_position(new_pos)


