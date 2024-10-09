import json
from mlb_summary_sheets.utils import Utils


class PlayerInfo:

    def __init__(self) -> None:
        self.mlbam_id = None
        self.first_name = None
        self.last_name = None
        self.link = None
        self.active = None
        self.primary_position = None
        self.use_name = None

    def set_from_mlb_info(self, mlb_player_info):
        self.mlbam_id = mlb_player_info.get('id')
        self.first_name = mlb_player_info.get('firstName')
        self.last_name = mlb_player_info.get('lastName')
        self.link = mlb_player_info.get('link')
        self.active = mlb_player_info.get('active')
        self.primary_position = mlb_player_info.get('primaryPosition', {}).get('abbreviation')
        self.use_name = mlb_player_info.get('useName')


    def to_json(self):
        player_info = {
            "mlbam_id": self.mlbam_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "link": self.link,
            "active": self.active,
            "primary_position": self.primary_position,
            "use_name": self.use_name
        }
        return player_info #json.dumps(player_info, indent=4, cls=Utils.NumpyEncoder)

    # "player_info": {
    #     "first_name": "Tarik",
    #     "last_name": "Skubal",
    #     "link": "/api/v1/people/669373",
    #     "active": true,
    #     "primary_position": {
    #         "code": "1",
    #         "name": "Pitcher",
    #         "type": "Pitcher",
    #         "abbreviation": "P"
    #     },
    #     "use_name": "Tarik",
    #     "use_last_name": "Skubal",
    #     "middle_name": "Daniel",
    #     "boxscore_name": "Skubal",
    #     "strike_zone": {
    #         "top": 3.49,
    #         "bottom": 1.601
    #     }