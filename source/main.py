from player_lookup import PlayerLookup  
from player import Player
from pitching.pitcher_summary_sheet import PitcherSummarySheet
from batting.batter_summary_sheet import BatterSummarySheet


def generate_pitcher_sheet(pitcher_name: str, year: int = 2024):
    player_id = PlayerLookup.get_player_mlbam_id(pitcher_name)
    player = Player(player_id)
    pitcher_summary = PitcherSummarySheet(player, year)
    pitcher_summary.generate_plots(player)

def generate_batter_sheet(batter_name: str, year: int = 2024):
    player_id = PlayerLookup.get_player_mlbam_id(batter_name)
    player = Player(player_id)
    batter_summary = BatterSummarySheet(player, year)
    batter_summary.generate_plots(player)

# Example Usage
if __name__ == "__main__":
    # pitchers = ['Beau Brieske', 'Jason Foley', 'Sean Guenther', 'Brenan Hanifee', 'Tyler Holton', 
    #             'Brant Hurter', 'Jackson Jobe', 'Ty Madden', 'Kenta Maeda', 'Casey Mize', 
    #             'Keider Montero', 'Reese Olson', 'Tarik Skubal', 'Will Vest']
    # pitchers = ['Tarik Skubal']
    # for pitcher in pitchers:
    #     generate_pitcher_sheet(pitcher)

    batters = ['Kerry Carpenter', 'Riley Greene']
    for batter in batters:
        generate_batter_sheet(batter)



    

