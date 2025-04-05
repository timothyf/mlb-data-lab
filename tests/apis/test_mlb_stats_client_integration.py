# tests/apis/test_mlb_stats_client_integration.py

import pytest
from mlb_data_lab.apis.mlb_stats_client import MlbStatsClient

@pytest.mark.integration
def test_fetch_player_stats_integration():
    """
    Integration test for MlbStatsClient.fetch_player_stats.

    This test calls the live Stats API to retrieve season stats splits for a known player.
    It uses Mike Trout's numeric player ID (commonly 545361) and a season with data.
    Note: This test requires a working internet connection and depends on external API responses.
    """
    # Known player id for Mike Trout; adjust if needed.
    player_id = 545361
    season = 2019

    result = MlbStatsClient.fetch_player_stats(player_id, season)
    
    # Assert that the result is not None and is a list.
    assert result is not None, "Expected non-None splits data for player stats."
    assert isinstance(result, list), "Expected splits data to be returned as a list."

    # For each split, check that:
    # - The split is a dictionary.
    # - It contains the keys 'season' and 'stat'.
    # - The 'stat' value is a dictionary with non-None (and if numeric, non-negative) values.
    for split in result:
        assert isinstance(split, dict), "Each split should be a dictionary."
        expected_keys = ['season', 'stat']
        for key in expected_keys:
            assert key in split, f"Expected key '{key}' in split: {split}"
        
        # Ensure that the 'stat' field is a dictionary.
        stat_data = split['stat']
        assert isinstance(stat_data, dict), "The 'stat' field should be a dictionary."
        
        # Check that each stat value is not None. Optionally, if numeric, it should be non-negative.
        for stat_key, value in stat_data.items():
            assert value is not None, f"Stat '{stat_key}' in split {split} is None."
            # If the value is numeric, check that it is not negative.
            try:
                numeric_value = float(value)
                assert numeric_value >= 0, f"Stat '{stat_key}' in split {split} is negative."
            except (ValueError, TypeError):
                # If the value cannot be converted to float, skip the numeric check.
                pass



@pytest.mark.integration
def test_fetch_batter_stat_splits_integration():
    """
    Integration test for MlbStatsClient.fetch_player_stat_splits using sample data for Riley Greene.
    
    Expected sample for hitting splits (from the provided sample JSON):
    
    Two splits for season "2024" should be returned:
      - First split (split code "vl") with:
          gamesPlayed: 84,
          team: id=116, name="Detroit Tigers", teamName="Tigers",
          player: id=682985, fullName="Riley Greene", firstName="Riley", lastName="Greene",
          league: id=103, name="American League",
          sport: id=1, name="Major League Baseball", abbreviation="MLB",
          gameType: "R",
          split: code "vl", description "vs Left", sortOrder 73,
          position: code "7", name="Outfielder", type="Outfielder", abbreviation="LF"
      
      - Second split (split code "vr") with:
          gamesPlayed: 131,
          team: same as above,
          player: same as above,
          league: same as above,
          sport: same as above,
          gameType: "R",
          split: code "vr", description "vs Right", sortOrder 74,
          position: same as above.
    """
    # Use Riley Greene's player id and season 2024.
    player_id = 682985
    season = 2024

    splits = MlbStatsClient.fetch_batter_stat_splits(player_id, season)

    # Basic assertions.
    assert splits is not None, "Expected non-None stat splits for player stats."
    assert isinstance(splits, list), "Expected stat splits to be returned as a list."
    assert len(splits) == 2, f"Expected 2 hitting splits, got {len(splits)} splits."

    # Define expected keys for every split.
    expected_keys = [
        'season', 'stat', 'team', 'player',
        'league', 'sport', 'gameType', 'split', 'position'
    ]

    # Expected values for the "vl" split.
    expected_first = {
        "season": "2024",
        "stat": {
            "gamesPlayed": 84
        },
        "team": {
            "id": 116,
            "name": "Detroit Tigers",
            "teamName": "Tigers"
        },
        "player": {
            "id": 682985,
            "fullName": "Riley Greene",
            "firstName": "Riley",
            "lastName": "Greene"
        },
        "league": {
            "id": 103,
            "name": "American League"
        },
        "sport": {
            "id": 1,
            "name": "Major League Baseball",
            "abbreviation": "MLB"
        },
        "gameType": "R",
        "split": {
            "code": "vl",
            "description": "vs Left",
            "sortOrder": 73
        },
        "position": {
            "code": "7",
            "name": "Outfielder",
            "type": "Outfielder",
            "abbreviation": "LF"
        }
    }

    # Expected values for the "vr" split.
    expected_second = {
        "season": "2024",
        "stat": {
            "gamesPlayed": 131
        },
        "team": {
            "id": 116,
            "name": "Detroit Tigers",
            "teamName": "Tigers"
        },
        "player": {
            "id": 682985,
            "fullName": "Riley Greene",
            "firstName": "Riley",
            "lastName": "Greene"
        },
        "league": {
            "id": 103,
            "name": "American League"
        },
        "sport": {
            "id": 1,
            "name": "Major League Baseball",
            "abbreviation": "MLB"
        },
        "gameType": "R",
        "split": {
            "code": "vr",
            "description": "vs Right",
            "sortOrder": 74
        },
        "position": {
            "code": "7",
            "name": "Outfielder",
            "type": "Outfielder",
            "abbreviation": "LF"
        }
    }

    def check_split(split, expected):
        # Verify that all expected keys exist.
        for key in expected_keys:
            assert key in split, f"Expected key '{key}' in split: {split}"

        # Compare simple string fields.
        assert split["season"] == expected["season"], f"Expected season {expected['season']}, got {split['season']}"
        assert split["gameType"] == expected["gameType"], f"Expected gameType {expected['gameType']}, got {split['gameType']}"

        # Check team fields.
        for k, v in expected["team"].items():
            assert split["team"].get(k) == v, f"Expected team {k}={v}, got {split['team'].get(k)}"
        
        # Check player fields.
        for k, v in expected["player"].items():
            assert split["player"].get(k) == v, f"Expected player {k}={v}, got {split['player'].get(k)}"
        
        # Check league.
        for k, v in expected["league"].items():
            assert split["league"].get(k) == v, f"Expected league {k}={v}, got {split['league'].get(k)}"
        
        # Check sport.
        for k, v in expected["sport"].items():
            assert split["sport"].get(k) == v, f"Expected sport {k}={v}, got {split['sport'].get(k)}"
        
        # Check split details.
        for k, v in expected["split"].items():
            assert split["split"].get(k) == v, f"Expected split info {k}={v}, got {split['split'].get(k)}"
        
        # Check position.
        for k, v in expected["position"].items():
            assert split["position"].get(k) == v, f"Expected position {k}={v}, got {split['position'].get(k)}"
        
        # Check stat; here we only check 'gamesPlayed'.
        for k, v in expected["stat"].items():
            assert split["stat"].get(k) == v, f"Expected stat {k}={v}, got {split['stat'].get(k)}"

    # Iterate over the splits and verify expected values.
    for split in splits:
        code = split.get("split", {}).get("code")
        if code == "vl":
            check_split(split, expected_first)
        elif code == "vr":
            check_split(split, expected_second)
        else:
            pytest.fail(f"Unexpected split code: {code}")

