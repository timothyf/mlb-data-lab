import json
from mlb_stats.utils import Utils


class PlayerBio:
    def __init__(self):
        self.full_name = None
        self.bats_hand = None
        self.throws_hand = None
        self.current_age = None
        self.height = None
        self.weight = None
        self.primary_number = None
        self.birth_date = None
        self.birth_city = None
        self.birth_state_province = None
        self.birth_country = None
        self.gender = None
        self.draft_year = None
        self.mlb_debut_date = None


    def set_from_mlb_info(self, mlb_player_info):
        self.full_name = mlb_player_info.get('fullName')
        self.current_age = mlb_player_info.get('currentAge')
        self.height = mlb_player_info.get('height')
        self.weight = mlb_player_info.get('weight')
        self.throws_hand = mlb_player_info.get('pitchHand', {}).get('code')
        self.bats_hand = mlb_player_info.get('batSide', {}).get('code')


    def to_json(self):
        player_bio = {
            "full_name": self.full_name,
            "bats_hand": self.bats_hand,
            "throws_hand": self.throws_hand,
            "current_age": self.current_age,
            "height": self.height,
            "weight": self.weight,
            # "primary_number": self.primary_number,
            # "birth_date": self.birth_date,
            # "birth_city": self.birth_city,
            # "birth_state_province": self.birth_state_province,
            # "birth_country": self.birth_country,
            # "gender": self.gender,
            # "draft_year": self.draft_year,
            # "mlb_debut_date": self.mlb_debut_date,
        }
        return player_bio #json.dumps(player_bio, indent=4, cls=Utils.NumpyEncoder)