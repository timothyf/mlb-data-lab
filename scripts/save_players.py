from source.player import Player


# Suppress MarkupResemblesLocatorWarning
#warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)



def save_player(player_name: str):
    player = Player(player_name)
    json_data = player.export_to_json()

    file_path = f"data/players/{player_name.replace(' ', '_').lower()}.json"

    # Open the file in write mode and save the JSON data
    with open(file_path, 'w') as json_file:
        json_file.write(json_data)

    print(f"Player data saved to {file_path}")

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



    

