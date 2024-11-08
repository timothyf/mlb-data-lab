import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from mlb_data_lab.player.player import Player
from mlb_data_lab.config import DATA_DIR
from mlb_data_lab.utils import Utils

# Suppress MarkupResemblesLocatorWarning
#warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


def save_player(player_name: str):
    player = Player.create_from_mlb(player_name = player_name)
    json_data = Utils.dump_json(player.to_json())

    # Construct the file path
    file_path = f"{DATA_DIR}/players/{player.mlbam_id}.json"

    # Ensure that the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Open the file in write mode and save the JSON data
    with open(file_path, 'w') as json_file:
        json_file.write(json_data)

    print(f"Player {player_name} data saved to {file_path}")


# import debugpy

# # 5678 is the default attach port in the VS Code debug configurations. Unless a host and port are specified, host defaults to 127.0.0.1
# debugpy.listen(5678)
# print("Waiting for debugger attach")
# debugpy.wait_for_client()

# Example Usage
if __name__ == "__main__":
    # pitchers = ['Beau Brieske', 'Jason Foley', 'Sean Guenther', 'Brenan Hanifee', 'Tyler Holton', 
    #             'Brant Hurter', 'Jackson Jobe', 'Ty Madden', 'Kenta Maeda', 'Casey Mize', 
    #             'Keider Montero', 'Reese Olson', 'Tarik Skubal', 'Will Vest']
    pitchers = ['Tarik Skubal']
    for pitcher in pitchers:
        save_player(pitcher)

    batters = ['Kerry Carpenter', 'Riley Greene']
    for batter in batters:
        save_player(batter)



    

