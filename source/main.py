from player_lookup import PlayerLookup  
from player import Player
from pitcher_summary_sheet import PitcherSummarySheet

def generate_pitcher_sheet(pitcher_name: str, year: int = 2024):
    player_id = PlayerLookup.get_player_mlbam_id(pitcher_name)
    player = Player(player_id)
    pitcher_summary = PitcherSummarySheet(player, year)
    pitcher_summary.generate_plots(player)

# Example Usage
if __name__ == "__main__":
    pitchers = ['Beau Brieske', 'Jason Foley', 'Sean Guenther', 'Brenan Hanifee', 'Tyler Holton', 
                'Brant Hurter', 'Jackson Jobe', 'Ty Madden', 'Kenta Maeda', 'Casey Mize', 
                'Keider Montero', 'Reese Olson', 'Tarik Skubal', 'Will Vest']
    for pitcher in pitchers:
        generate_pitcher_sheet(pitcher)


    

