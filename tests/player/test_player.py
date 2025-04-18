import pytest
from io import BytesIO
from PIL import Image
import os


import mlb_data_lab.player.player as player_module
from mlb_data_lab.player.player import Player


class DummyDataClient:
    def __init__(self):
        self.fetched_info = None
        self.pitching_stats = {'wins': 10}
        self.batting_stats = {'hits': 50}
        self.pitching_splits = {'splits': 'pitch'}
        self.batting_splits = {'splits': 'bat'}
        self.statcast_pitcher = [{'pitch_data': 1}]
        self.statcast_batter = [{'bat_data': 2}]
        self.headshot_bytes = BytesIO()
        Image.new('RGB', (1, 1)).save(self.headshot_bytes, format='PNG')
        self.headshot_bytes = self.headshot_bytes.getvalue()

    def fetch_pitching_stats(self, mlbam_id, season):
        return self.pitching_stats

    def fetch_batting_stats(self, mlbam_id, season):
        return self.batting_stats

    def fetch_pitching_splits(self, mlbam_id, season):
        return self.pitching_splits

    def fetch_batting_splits(self, mlbam_id, season):
        return self.batting_splits

    def fetch_statcast_pitcher_data(self, mlbam_id, start, end):
        return self.statcast_pitcher

    def fetch_statcast_batter_data(self, mlbam_id, start, end):
        return self.statcast_batter

    def fetch_player_info(self, mlbam_id):
        self.fetched_info = {'name_first': 'john', 'name_last': 'doe', 'currentTeam': {'id': 99}}
        return self.fetched_info

    def fetch_player_headshot(self, mlbam_id):
        return self.headshot_bytes

    def save_statcast_pitcher_data(self, mlbam_id, year, path):
        # ensure the directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write("pitcher data")

    def save_statcast_batter_data(self, mlbam_id, year, path):
        # ensure the directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write("batter data")


class DummyLookupClient:
    def __init__(self, return_data=None):
        self.return_data = return_data

    def lookup_player(self, *args, **kwargs):
        return self.return_data


class DummyPlayerInfo:
    def __init__(self):
        self.primary_position = None

    def set_from_mlb_info(self, info):
        self.primary_position = 'P' if info.get('primary_position', 'P') == 'P' else 'H'
    
    def to_json(self):
        return {'info': True}


class DummyPlayerBio:
    def __init__(self):
        self.full_name = 'John Doe'

    def set_from_mlb_info(self, info):
        self.full_name = f"{info['name_first']} {info['name_last']}"

    def to_json(self):
        return {'bio': True}


class DummyTeam:
    def __init__(self, data_client=None):
        self.name = 'Fake Team'
        self.abbrev = 'FTM'

    @classmethod
    def create_from_mlb(cls, team_id, data_client=None):
        return DummyTeam()


@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch, tmp_path):
    # Patch data_client, lookup_client, PlayerInfo, PlayerBio, Team, STATCAST_DATA_DIR
    monkeypatch.setattr(player_module, 'STATCAST_DATA_DIR', str(tmp_path))
    monkeypatch.setattr(player_module, 'UnifiedDataClient', lambda: DummyDataClient())
    monkeypatch.setattr(player_module, 'PlayerLookup', lambda data_client=None: DummyLookupClient(return_data={'key_mlbam': 1, 'key_bbref': 'BB'}))
    monkeypatch.setattr(player_module, 'PlayerInfo', DummyPlayerInfo)
    monkeypatch.setattr(player_module, 'PlayerBio', DummyPlayerBio)
    monkeypatch.setattr(player_module, 'Team', DummyTeam)


def test_init_default():
    player = Player()
    assert player.mlbam_id is None
    assert player.bbref_id is None
    assert isinstance(player.player_info, DummyPlayerInfo)
    assert isinstance(player.player_bio, DummyPlayerBio)
    assert isinstance(player.current_team, DummyTeam)
    assert isinstance(player.data_client, DummyDataClient)
    assert isinstance(player.lookup_client, DummyLookupClient)


def test_load_stats_for_season_pitcher():
    player = Player(mlbam_id=123)
    player.player_info.primary_position = 'P'
    player.load_stats_for_season(2021)
    assert player.player_stats == player.data_client.pitching_stats
    assert player.player_splits_stats == player.data_client.pitching_splits


def test_load_stats_for_season_batter():
    player = Player(mlbam_id=456)
    player.player_info.primary_position = 'H'
    player.load_stats_for_season(2021)
    assert player.player_stats == player.data_client.batting_stats
    assert player.player_splits_stats == player.data_client.batting_splits


def test_load_statcast_data_pitcher():
    player = Player(mlbam_id=789)
    player.player_info.primary_position = 'P'
    player.load_statcast_data('2021-01-01', '2021-12-31')
    assert player.statcast_data == player.data_client.statcast_pitcher


def test_load_statcast_data_batter():
    player = Player(mlbam_id=789)
    player.player_info.primary_position = 'H'
    player.load_statcast_data('2021-01-01', '2021-12-31')
    assert player.statcast_data == player.data_client.statcast_batter


def test_create_from_mlb_with_name():
    # Using patched lookup_client to return valid data
    player = Player.create_from_mlb(player_name='John Doe')
    assert isinstance(player, Player)
    assert player.mlbam_id == 1
    assert player.bbref_id == 'BB'
    # After creation, player_info and player_bio should have been set
    assert player.player_info.primary_position in ('P', 'H')
    assert player.player_bio.full_name in ('john doe', 'John Doe')


def test_create_from_mlb_with_invalid_name(monkeypatch):
    # Patch lookup_client to return None
    monkeypatch.setattr(player_module, 'PlayerLookup', lambda data_client=None: DummyLookupClient(return_data=None))
    player = Player.create_from_mlb(player_name='Jane Doe')
    assert player is None


def test_create_from_mlb_with_id(monkeypatch):
    # Patch lookup_client to use id branch
    monkeypatch.setattr(player_module, 'PlayerLookup', lambda data_client=None: DummyLookupClient(return_data={'name_first': 'jane', 'name_last': 'smith', 'key_bbref': 'BB2'}))
    player = Player.create_from_mlb(mlbam_id=999)
    assert isinstance(player, Player)
    assert player.mlbam_id == 999
    assert player.bbref_id == 'BB2'


def test_set_team_no_info(caplog):
    player = Player(mlbam_id=123)
    # fetch_player_info gives currentTeam id, so override fetched_info to no id
    player.data_client.fetched_info = {'name_first': 'x', 'name_last': 'y', 'currentTeam': {}}
    player.set_team(player.data_client.fetched_info)
    assert 'No current team information available' in caplog.text


def test_get_headshot():
    player = Player(mlbam_id=111)
    img = player.get_headshot()
    assert isinstance(img, Image.Image)
    assert img.size == (1, 1)


def test_save_statcast_data(tmp_path):
    player = Player(mlbam_id=222)
    player.player_info.primary_position = 'H'
    player.player_bio.full_name = 'Jane Doe'
    player.current_team.abbrev = 'JTD'
    player.save_statcast_data(year=2022)
    # Check that file was created
    expected = tmp_path / '2022' / 'statcast_data' / 'JTD' / 'batting' / 'statcast_data_jane_doe_2022.csv'
    assert expected.exists()


def test_to_json():
    player = Player(mlbam_id=333)
    player.bbref_id = 'BREF'
    player.current_team.name = 'TeamX'
    # Monkeypatch to_json methods
    player.player_bio.to_json = lambda: {'bio_test': True}
    player.player_info.to_json = lambda: {'info_test': True}
    result = player.to_json()
    assert result == {
        "mlbam_id": 333,
        "bbref_id": 'BREF',
        "team_name": 'TeamX',
        "player_bio": {'bio_test': True},
        "player_info": {'info_test': True},
    }

