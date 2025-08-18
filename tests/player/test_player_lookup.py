# tests/test_player_lookup.py

import os
import logging
import pytest
import pandas as pd

from baseball_data_lab.player.player_lookup import PlayerLookup
from baseball_data_lab.special_name_mappings import SpecialNameMappings

logging.getLogger("baseball_data_lab").setLevel(logging.DEBUG)


class DummyClient:
    """A stand‐in for UnifiedDataClient that we can monkey‐patch per test."""
    def __init__(self):
        # capture the last call arguments
        self.calls = []

    def lookup_player(self, last_name, first_name, fuzzy=False):
        self.calls.append(("lookup_player", last_name, first_name, fuzzy))
        # default: return empty frame
        return pd.DataFrame()

    def lookup_player_by_id(self, player_id):
        self.calls.append(("lookup_player_by_id", player_id))
        return pd.DataFrame()


@pytest.fixture
def dummy_client():
    return DummyClient()


@pytest.fixture
def lookup(dummy_client):
    return PlayerLookup(data_client=dummy_client)


def test_parse_full_name_basic():
    pl = PlayerLookup(data_client=DummyClient())
    assert pl.parse_full_name("John Doe") == ("John", "Doe")
    assert pl.parse_full_name("Alice van Helsing") == ("Alice", "Helsing")


def test_parse_full_name_suffix():
    pl = PlayerLookup(data_client=DummyClient())
    # Jr. at end, so take second‐to‐last
    assert pl.parse_full_name("John Michael Jr.") == ("John", "Michael")
    # IV at end
    assert pl.parse_full_name("Sarah Anne IV") == ("Sarah", "Anne")


def test_parse_full_name_too_short_raises():
    pl = PlayerLookup(data_client=DummyClient())
    with pytest.raises(ValueError):
        pl.parse_full_name("Madonna")


def test_lookup_player_id_direct_int(monkeypatch, lookup, dummy_client, caplog):
    # simulate direct hit returning a single int
    def fake(last, first, fuzzy=False):
        return pd.DataFrame([{"key_mlbam": 123}])
    monkeypatch.setattr(dummy_client, "lookup_player", fake)

    caplog.set_level(logging.WARNING)
    result = lookup.lookup_player_id("Jane Doe")
    # got back the int
    assert result == 123
    # no warning about multiple
    assert "Multiple names found" not in caplog.text


def test_lookup_player_id_multiple_names(monkeypatch, lookup, dummy_client, caplog):
    # simulate hit returning a list
    def fake(last, first, fuzzy=False):
        return pd.DataFrame([{"key_mlbam": [111, 222]}])
    monkeypatch.setattr(dummy_client, "lookup_player", fake)

    caplog.set_level(logging.WARNING)
    result = lookup.lookup_player_id("John Doe")
    assert result == [111, 222]
    assert "Multiple names found for: John Doe" in caplog.text


def test_lookup_player_id_fuzzy(monkeypatch, lookup, dummy_client):
    # first call returns empty
    def first(last, first, fuzzy=False):
        return pd.DataFrame()
    # fuzzy call returns list of dicts
    def second(last, first, fuzzy=False):
        return [{"foo": "bar"}]
    calls = {"n": 0}

    def fake(last, first, fuzzy=False):
        calls["n"] += 1
        if calls["n"] == 1:
            return pd.DataFrame()
        else:
            return second(last, first, fuzzy)

    monkeypatch.setattr(dummy_client, "lookup_player", fake)

    df = lookup.lookup_player_id("Mary Smith")
    # should be a DataFrame wrapping the dict
    assert isinstance(df, pd.DataFrame)
    assert df.to_dict(orient="records") == [{"foo": "bar"}]


def test_lookup_player_by_name_direct(monkeypatch, lookup, dummy_client):
    row = {"key_mlbam": 999, "name_first": "Joe", "name_last": "Bloggs"}
    def fake(last, first, fuzzy=False):
        return pd.DataFrame([row])
    monkeypatch.setattr(dummy_client, "lookup_player", fake)

    result = lookup.lookup_player("Joe Bloggs")
    # expect a pandas Series
    assert hasattr(result, "name")  # Series
    assert result["key_mlbam"] == 999
    assert result["name_first"] == "Joe"
    assert result["name_last"] == "Bloggs"


def test_lookup_player_name_parse_error(monkeypatch, lookup, caplog):
    # give a single‐token name
    caplog.set_level(logging.ERROR)
    result = lookup.lookup_player("Prince")
    assert result is None
    assert "does not contain enough parts" in caplog.text


def test_lookup_player_direct_lookup_exception(monkeypatch, lookup, dummy_client, caplog):
    def boom(last, first, fuzzy=False):
        raise RuntimeError("no network")
    monkeypatch.setattr(dummy_client, "lookup_player", boom)

    caplog.set_level(logging.ERROR)
    result = lookup.lookup_player("Jim Doe")
    assert result is None
    assert "Error looking up player Jim Doe" in caplog.text


def test_lookup_player_special_fullname(monkeypatch, lookup, dummy_client):
    # pick a mapping from SpecialNameMappings of type "player_name"
    orig, pid = next(iter(SpecialNameMappings["player_name"].items()))

    # first lookup returns empty Frame
    def fake_lp(last, first, fuzzy=False):
        return pd.DataFrame()
    # then lookup_by_id returns a row
    def fake_by_id(pid_arg):
        return pd.DataFrame([{
            "key_mlbam": pid_arg,
            "name_first": "X", "name_last": "Y"
        }])
    monkeypatch.setattr(dummy_client, "lookup_player", fake_lp)
    monkeypatch.setattr(dummy_client, "lookup_player_by_id", fake_by_id)

    result = lookup.lookup_player(orig)
    # should come back from lookup_player_by_id
    assert result["key_mlbam"] == pid
    assert result["name_first"] == "X"
    assert result["name_last"] == "Y"


def test_handle_special_cases_first_name(monkeypatch, lookup, dummy_client):
    # find a first_name mapping
    orig, resolved = next(iter(SpecialNameMappings["first_name"].items()))

    # direct new_last_name path: name_parts length==2 so skip
    # next, corrected first_name path should trigger
    def fake_lookup(last, first, fuzzy=False):
        # only accept the corrected first name
        if first == resolved:
            return pd.DataFrame([{"key_mlbam": 555}])
        else:
            return pd.DataFrame()
    monkeypatch.setattr(dummy_client, "lookup_player", fake_lookup)

    # first_name = orig, last_name = "Smith", player_name = "Orig Smith"
    df, pid = lookup.handle_special_cases(orig, "Smith", f"{orig} Smith")

    # got back df with our fake data, pid stays None
    assert pid is None
    assert isinstance(df, pd.DataFrame)
    assert df.iloc[0]["key_mlbam"] == 555


def test_handle_special_cases_last_name(monkeypatch, lookup, dummy_client):
    # find a last_name mapping
    orig, resolved = next(iter(SpecialNameMappings["last_name"].items()))

    # first two paths skip or fail, then corrected last_name path
    def fake_lookup(last, first, fuzzy=False):
        if last == resolved:
            return pd.DataFrame([{"key_mlbam": 777}])
        else:
            return pd.DataFrame()
    monkeypatch.setattr(dummy_client, "lookup_player", fake_lookup)

    # first_name = "Bob", last_name = orig, player_name = "Bob Orig"
    df, pid = lookup.handle_special_cases("Bob", orig, f"Bob {orig}")
    
    assert pid is None
    assert df.iloc[0]["key_mlbam"] == 777


def test_handle_special_cases_no_match(monkeypatch, lookup, dummy_client):
    # all lookups fail; no full‐name mapping for "Nobody Here"
    def fake_lookup(last, first, fuzzy=False):
        return pd.DataFrame()
    monkeypatch.setattr(dummy_client, "lookup_player", fake_lookup)

    df, pid = lookup.handle_special_cases("No Body Here", "No", "Here")
    assert pid is None
    assert df.empty

