import pandas as pd
import pytest
from mlb_data_lab.player.player_lookup import PlayerLookup

# Define a dummy data client to use in our tests
class DummyDataClient:
    def lookup_player(self, last_name, first_name, fuzzy=False):
        # For testing lookup_player_id and lookup_player:
        if fuzzy:
            # When fuzzy=True, return a result that is a dict (which will be
            # converted to a DataFrame) for testing purposes.
            return [{'key_mlbam': 88888, 'name_first': first_name, 'name_last': last_name}]
        # Return a non-empty DataFrame if we are looking for "John Doe"
        if last_name == "Doe" and first_name == "John":
            return pd.DataFrame([{'key_mlbam': 12345, 'name_first': 'John', 'name_last': 'Doe'}])
        # Otherwise, return an empty DataFrame
        return pd.DataFrame()

    def lookup_player_by_id(self, player_id):
        # Return a non-empty DataFrame for a test id (e.g. 55555)
        if player_id == 55555:
            return pd.DataFrame([{'key_mlbam': 55555, 'name_first': 'Test', 'name_last': 'Player'}])
        else:
            return pd.DataFrame()


# Create a dummy client instance
dummy_client = DummyDataClient()

# Use a pytest fixture to override the data_client for all tests
@pytest.fixture(autouse=True)
def override_data_client():
    PlayerLookup.data_client = dummy_client


def test_lookup_player_id_found():
    """Test lookup_player_id returns the key_mlbam when a match is found."""
    pitcher_name = "John Doe"
    result = PlayerLookup.lookup_player_id(pitcher_name)
    assert result == 12345


def test_lookup_player_id_multiple_names(monkeypatch, capsys):
    """Test that a list for key_mlbam triggers the multiple names print message."""
    def fake_lookup_player(last_name, first_name, fuzzy=False):
        # Return a DataFrame with a key_mlbam that is a list
        return pd.DataFrame([{'key_mlbam': [111, 222], 'name_first': first_name, 'name_last': last_name}])
    
    monkeypatch.setattr(dummy_client, 'lookup_player', fake_lookup_player)
    pitcher_name = "John Doe"
    result = PlayerLookup.lookup_player_id(pitcher_name)
    
    captured = capsys.readouterr().out
    assert "Multiple names found for: John Doe" in captured
    assert result == [111, 222]


def test_lookup_player_id_not_found(monkeypatch, capsys):
    """Test when lookup_player returns an empty DataFrame so that fuzzy matching is used."""
    def fake_lookup_player(last_name, first_name, fuzzy=False):
        if fuzzy:
            # Return a value that can be converted into a DataFrame
            return [{'key_mlbam': 88888, 'name_first': first_name, 'name_last': last_name}]
        return pd.DataFrame()
    
    monkeypatch.setattr(dummy_client, 'lookup_player', fake_lookup_player)
    pitcher_name = "Jane Smith"
    result = PlayerLookup.lookup_player_id(pitcher_name)
    # fuzzy_results gets converted to a DataFrame in the method
    assert isinstance(result, pd.DataFrame)
    # Validate that the first row has key_mlbam equal to 88888
    assert result.iloc[0]['key_mlbam'] == 88888


def test_lookup_player_by_name_found():
    """Test lookup_player when a player_name is given and a matching record is found."""
    player_name = "John Doe"
    result = PlayerLookup.lookup_player(player_name=player_name)
    # Expect that we get a Series (a row) with the correct key_mlbam value
    assert isinstance(result, pd.Series)
    assert result['key_mlbam'] == 12345


def test_lookup_player_by_id():
    """Test lookup_player when player_id is provided."""
    result = PlayerLookup.lookup_player(player_id=55555)
    assert isinstance(result, pd.Series)
    assert result['key_mlbam'] == 55555


def test_lookup_player_not_found(monkeypatch):
    """Test lookup_player returns None when no matching player is found."""
    def fake_lookup_player(last_name, first_name, fuzzy=False):
        return pd.DataFrame()  # Always return empty DataFrame
    
    monkeypatch.setattr(dummy_client, 'lookup_player', fake_lookup_player)
    result = PlayerLookup.lookup_player(player_name="Nonexistent Player")
    assert result is None


def test_handle_special_cases_matthew(monkeypatch, capsys):
    """Test special case handling for first name 'Matthew' --> 'Matt'."""
    def fake_lookup_player(last_name, first_name):
        if first_name == 'Matt':
            return pd.DataFrame([{'key_mlbam': 77777, 'name_first': first_name, 'name_last': last_name}])
        else:
            return pd.DataFrame()
    
    monkeypatch.setattr(dummy_client, 'lookup_player', fake_lookup_player)
    name_parts = ["Matthew", "Smith"]
    player_df, player_id = PlayerLookup.handle_special_cases(name_parts, "Matthew", "Smith", "Matthew Smith")
    captured = capsys.readouterr().out
    # We expect that with 'Matthew' switched to 'Matt', a DataFrame with key_mlbam 77777 is returned
    assert not player_df.empty
    assert player_df.iloc[0]['key_mlbam'] == 77777
    assert player_id is None


def test_handle_special_cases_willie():
    """Test special case for 'Willie Hernandez'."""
    name_parts = ["Willie", "Hernandez"]
    _, player_id = PlayerLookup.handle_special_cases(name_parts, "Willie", "Hernandez", "Willie Hernandez")
    assert player_id == 115822


def test_handle_special_cases_barbaro():
    """Test special case for 'Barbaro Garbey'."""
    name_parts = ["Barbaro", "Garbey"]
    _, player_id = PlayerLookup.handle_special_cases(name_parts, "Barbaro", "Garbey", "Barbaro Garbey")
    assert player_id == 114579


def test_handle_special_cases_aurelio():
    """Test special case for 'Aurelio Lopez'."""
    name_parts = ["Aurelio", "Lopez"]
    _, player_id = PlayerLookup.handle_special_cases(name_parts, "Aurelio", "Lopez", "Aurelio Lopez")
    assert player_id == 117916
