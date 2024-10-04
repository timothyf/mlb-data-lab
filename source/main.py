from player import Player
from pitching.pitcher_summary_sheet import PitcherSummarySheet
from batting.batter_summary_sheet import BatterSummarySheet


def generate_pitcher_sheet(pitcher_name: str, year: int = 2024):
    player = Player(pitcher_name)
    pitcher_summary = PitcherSummarySheet(player, year)
    pitcher_summary.generate_plots()

def generate_batter_sheet(batter_name: str, year: int = 2024):
    player = Player(batter_name)
    batter_summary = BatterSummarySheet(player, year)
    batter_summary.generate_plots()

# Example Usage
if __name__ == "__main__":
    # pitchers = ['Beau Brieske', 'Jason Foley', 'Sean Guenther', 'Brenan Hanifee', 'Tyler Holton', 
    #             'Brant Hurter', 'Jackson Jobe', 'Ty Madden', 'Kenta Maeda', 'Casey Mize', 
    #             'Keider Montero', 'Reese Olson', 'Tarik Skubal', 'Will Vest']
    pitchers = ['Tarik Skubal']
    for pitcher in pitchers:
        generate_pitcher_sheet(pitcher)

    batters = ['Kerry Carpenter', 'Riley Greene']
    for batter in batters:
        generate_batter_sheet(batter)



    

