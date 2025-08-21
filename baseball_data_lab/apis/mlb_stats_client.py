"""Utilities for interacting with the public MLB Stats API."""

from typing import Any, Dict, List, Optional, Literal
from urllib.parse import urlencode

import pandas as pd
import requests
import statsapi
from requests.adapters import HTTPAdapter, Retry

from baseball_data_lab.config import STATS_API_BASE_URL, SAVANT_BASE_URL
from datetime import date


class MlbStatsClient:
    """Thin wrapper around the MLB Stats API."""

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _get_json(url: str, *, session: Optional[Any] = None) -> Dict[str, Any]:
        """Fetch ``url`` and return the decoded JSON payload."""
        http = session or requests
        return http.get(url).json()

    @staticmethod
    def _process_splits(data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Reformat split data into a ``pandas`` ``DataFrame``."""
        stat_rows: List[Dict[str, Any]] = []
        split_names: List[str] = []
        for entry in data:
            split_name = entry.get("split", {}).get("code", "Unknown Split")
            stat_rows.append(entry.get("stat", {}))
            split_names.append(split_name)

        df_stats = pd.DataFrame(stat_rows)
        multi_index = pd.MultiIndex.from_tuples(
            [(split_names[i], i) for i in range(len(split_names))],
            names=["Split", "Row"],
        )
        df_stats.index = multi_index
        return df_stats

    @staticmethod
    def _safe_pct(numer: Any, denom: Any) -> Optional[float]:
        """Return percentage (0–100) rounded to 2 decimals, or ``None`` if invalid."""
        try:
            n = float(numer)
            d = float(denom)
            if d == 0:
                return None
            return round((n / d) * 100.0, 2)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _add_rate_stats(bucket: Dict[str, Any]) -> None:
        """Compute BB% and K% in-place if possible."""
        bb_pct = MlbStatsClient._safe_pct(bucket.get("baseOnBalls"), bucket.get("plateAppearances"))
        if bb_pct is not None:
            bucket["BB%"] = bb_pct
        k_pct = MlbStatsClient._safe_pct(bucket.get("strikeOuts"), bucket.get("plateAppearances"))
        if k_pct is not None:
            bucket["K%"] = k_pct

    @staticmethod
    def _session_with_retries(total: int = 3, backoff: float = 0.3) -> requests.Session:
        s = requests.Session()
        retries = Retry(
            total=total,
            backoff_factor=backoff,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET"]),
        )
        s.mount("https://", HTTPAdapter(max_retries=retries))
        return s

    # ------------------------------------------------------------------
    # Simple fetchers
    # ------------------------------------------------------------------
    @staticmethod
    def fetch_player_info(player_id: int):
        """Fetch player information by MLBAM player ID.
            https://statsapi.mlb.com/api/v1/people?personIds=669373&hydrate=currentTeam
        """
        url = f"{STATS_API_BASE_URL}people?personIds={player_id}&hydrate=currentTeam"
        data = MlbStatsClient._get_json(url)
        return data["people"][0]

    @staticmethod
    def fetch_team(team_id: int):
        """Fetch team information by MLBAM team ID.
            https://statsapi.mlb.com/api/v1/teams/116 
        """
        url = f"{STATS_API_BASE_URL}teams/{team_id}"
        data = MlbStatsClient._get_json(url)
        return data.get("teams", {})[0]

    @staticmethod
    def fetch_batter_stat_splits(player_id: int, year: int):
        """
        Fetch batter stat splits for a player in a specific year.
       https://statsapi.mlb.com/api/v1/people?personIds=682985&hydrate=stats(group=[hitting],type=statSplits,sitCodes=[vr,vl,h,a],season=2024)       """
        url = (
            f"{STATS_API_BASE_URL}people?personIds={player_id}"
            f"&hydrate=stats(group=[hitting],type=statSplits,sitCodes=[vr,vl,h,a],season={year})"
        )
        data = MlbStatsClient._get_json(url)
        return MlbStatsClient._process_splits(data["people"][0]["stats"][0]["splits"])

    @staticmethod
    def fetch_pitcher_stat_splits(player_id: int, year: int):
        """
        Fetch pitcher stat splits for a player in a specific year.
        https://statsapi.mlb.com/api/v1/people?personIds=669373&hydrate=stats(group=[pitching],type=statSplits,sitCodes=[vr,vl],season=2024)
        """
        url = (
            f"{STATS_API_BASE_URL}people?personIds={player_id}"
            f"&hydrate=stats(group=[pitching],type=statSplits,sitCodes=[vr,vl],season={year})"
        )
        data = MlbStatsClient._get_json(url)
        return MlbStatsClient._process_splits(data["people"][0]["stats"][0]["splits"])

    # @staticmethod
    # def fetch_player_stats(player_id: int, year: int):
    #     stats = statsapi.get(
    #         "people",
    #         {
    #             "personIds": player_id,
    #             "season": year,
    #             "hydrate": f"stats(group=[hitting,pitching],type=season,season={year})",
    #         },
    #     )["people"][0]
    #     if "stats" not in stats:
    #         return None
    #     return stats["stats"][0]["splits"]
    """
    Fetch season and team-split stats for a player/year using the StatsAPI hydrate
    endpoint.

    Returns
    -------
    dict
        {
        "player_id": int,
        "season_stats": {"season": {...}},  # aggregated season totals (if present)
        "teams": {team_id: {"teamId": ..., "teamName": ..., "abbrev": ..., "stats": {...}}, ...},
        "team_ids": [ ... ]                  # distinct team IDs for that season, in response order
        }

    Raises
    ------
    requests.HTTPError
        For non-200 responses.
    ValueError
        For missing/invalid response shapes.
    """
    @staticmethod
    def fetch_player_stats_by_season(
        player_id: int,
        year: int,
        *,
        group: Optional[Literal["batting", "pitching", "fielding"]] = None,
        timeout: float = 8.0,
    ) -> Dict[str, Any]:

        # Build the hydrate expression
        stat_types = ["season", "seasonAdvanced"]  # add/remove types as needed
        stat_types_part = ",".join(stat_types)

        # If you want to filter to a specific group, you can also request:
        # stats(type=[...], group=[pitching])
        # The API accepts group inside the stats() block; including it reduces payload size.
        group_part = f",group=[{group}]" if group else ""

        hydrate = (
            f"team,"
            f"stats(type=[{stat_types_part}]{group_part}"
            f"(team(league)),leagueListId=mlb_hist,season={year})"
        )

        params = {
            "hydrate": hydrate,
        }
        url = f"{STATS_API_BASE_URL}/people/{player_id}"

        # Build full URL to allow simple monkeypatching of requests.get
        full_url = f"{url}?{urlencode(params)}"
        try:
            resp = requests.get(full_url, timeout=timeout)
        except TypeError:
            # Support mocks that don't accept a timeout argument
            resp = requests.get(full_url)
        if resp.status_code != 200:
            # Surface a clear message with URL & params for debugging
            msg = f"StatsAPI error {resp.status_code} for {resp.url}"
            try:
                details = resp.json()
                msg += f" | body: {details}"
            except Exception:
                pass
            resp.raise_for_status()

        payload = resp.json()
        people = payload.get("people") or []
        if not people:
            raise ValueError(f"No 'people' found for player_id={player_id}, year={year}")

        # Find the exact player (safety in case multiple entries are returned)
        person = next((p for p in people if p.get("id") == player_id), people[0])

        season_bucket: Dict[str, Any] = {}
        result: Dict[str, Any] = {
            "player_id": player_id,
            "season": season_bucket,  # aggregate (no team) if present
            "season_stats": {"season": season_bucket},
            "teams": {},      # keyed by teamId
            "team_ids": [],   # ordered, deduped
        }

        for stat_group in person.get("stats") or []:
            # Only consider our requested types
            type_name = stat_group.get("type", {}).get("displayName")
            if type_name not in stat_types:
                continue

            for split in stat_group.get("splits") or []:
                if split.get("season") != str(year):
                    continue

                stat_block = split.get("stat") or {}

                # Season aggregate (no team key)
                if "team" not in split:
                    # Merge into aggregate bucket
                    season_bucket.update(stat_block)
                    MlbStatsClient._add_rate_stats(season_bucket)
                    continue

                # Team-specific entry
                team = split["team"]
                team_id = team.get("id")
                if team_id is None:
                    # Fallback if id missing (shouldn’t happen, but be defensive)
                    # Use name as a last resort key
                    team_id = team.get("abbreviation") or team.get("teamName") or "unknown"

                # Create team record if new
                if team_id not in result["teams"]:
                    result["teams"][team_id] = {
                        "teamId": team.get("id"),
                        "teamName": team.get("teamName"),
                        "abbrev": team.get("abbreviation"),
                        "leagueId": (team.get("league") or {}).get("id"),
                        "leagueName": (team.get("league") or {}).get("name"),
                        "stats": {},
                    }
                    if team_id not in result["team_ids"]:
                        result["team_ids"].append(team_id)

                # Merge/overlay stats from this split into the team bucket
                team_stats = result["teams"][team_id]["stats"]
                team_stats.update(stat_block)
                MlbStatsClient._add_rate_stats(team_stats)

        return result

    ## Usage:
    # # Jack Flaherty, 2024
    # teams = MlbStatsClient.get_player_teams_for_season(656427, 2024)
    # # e.g. [{'teamId': 116, 'teamName': 'Detroit Tigers', 'abbrev': 'DET', ...},
    # #       {'teamId': 119, 'teamName': 'Los Angeles Dodgers', 'abbrev': 'LAD', ...}]

    # ids = MlbStatsClient.get_player_teams_for_season(656427, 2024, ids_only=True)
    # # e.g. [116, 119]
    @staticmethod
    def get_player_teams_for_season(
        player_id: int,
        year: int,
        *,
        group: Optional[str] = None,
        ids_only: bool = False,
    ) -> List[Any]:
        """
        Return the distinct teams a player played for in a given season.

        Args:
            player_id: MLBAM personId
            year: target season (e.g., 2024)
            group: optionally limit stats retrieval to 'batting' | 'pitching' | 'fielding'
                   (keeps payload small; not required for team membership)
            ids_only: if True, return a list of teamIds (ints); otherwise a list of dicts:
                      [{teamId, teamName, abbrev, leagueId, leagueName}]

        Returns:
            [] if no teams found; otherwise a list ordered as returned by the API.
        """
        data: Dict[str, Any] = MlbStatsClient.fetch_player_stats_by_season(
            player_id, year, group=group
        )

        team_ids = data.get("team_ids") or []
        teams_map = data.get("teams") or {}

        if ids_only:
            # Normalize to ints when possible
            out: List[int] = []
            for tid in team_ids:
                entry = teams_map.get(tid, {})
                team_id = entry.get("teamId", tid)
                try:
                    team_id = int(team_id)
                except (TypeError, ValueError):
                    pass
                out.append(team_id)
            return out

        results: List[Dict[str, Any]] = []
        for tid in team_ids:
            entry = teams_map.get(tid, {})
            results.append({
                "teamId": entry.get("teamId", tid),
                "teamName": entry.get("teamName"),
                "abbrev": entry.get("abbrev"),
                "leagueId": entry.get("leagueId"),
                "leagueName": entry.get("leagueName"),
            })
        return results

    
    @staticmethod
    def fetch_player_team(player_id: int, year: int):
        """
        Fetch the current team for a player in a specific year.

            https://statsapi.mlb.com/api/v1/people?personIds=111509&season=1984&hydrate=stats(group=[],type=season,team,season=1984)
        """
        url = (
            f"{STATS_API_BASE_URL}people?"
            f"personIds={player_id}"
            f"&season={year}"
            f"&hydrate=stats(group=[],type=season,team,season={year})"
        )
        data = MlbStatsClient._get_json(url)
        splits = data["people"][0]["stats"][0]["splits"]

        for element in splits:
            team = element.get("team")
            if team:
                return team

        print(f"No team information found for player {player_id} in season {year}.")
        return None


    
    # Sample
        #77  2B  Andy Ibáñez
        #4   P   Beau Brieske
        #48  P   Brant Hurter
        #75  P   Brenan Hanifee
        #33  2B  Colt Keith
        #38  C   Dillon Dingler
        #17  3B  Jace Jung
        #21  P   Jackson Jobe
        #34  C   Jake Rogers
        #68  P   Jason Foley
        #44  LF  Justyn-Henry Malloy
        #54  P   Keider Montero
        #30  RF  Kerry Carpenter
        #8   CF  Matt Vierling
        #22  CF  Parker Meadows
        #45  P   Reese Olson
        #31  LF  Riley Greene
        #73  P   Sean Guenther
        #20  1B  Spencer Torkelson
        #29  P   Tarik Skubal
        #27  SS  Trey Sweeney
        #36  P   Ty Madden
        #87  P   Tyler Holton
        #46  RF  Wenceel Pérez
        #19  P   Will Vest
        #39  SS  Zach McKinstry
    @staticmethod
    def fetch_active_roster(team_id: int = None, team_name: str = None, year: int = 2024):
        """Return the active roster for a team in a given ``year``.

        """
        if not team_id:
            team_id = MlbStatsClient.get_team_id(team_name)

        url = (
            f"{STATS_API_BASE_URL}teams/{team_id}/roster"
            f"?season={year}&rosterType=active"
        )
        data = MlbStatsClient._get_json(url)
        return data["roster"]
    

    @staticmethod
    def fetch_full_season_roster(team_id: int, year: int = 2024):
        """Return the full roster for a team in a given ``year``.

        https://statsapi.mlb.com/api/v1/teams/116/roster?&season=2025&rosterType=fullSeason
        """
        url = f"{STATS_API_BASE_URL}teams/{team_id}/roster?season={year}&rosterType=fullSeason"
        data = MlbStatsClient._get_json(url)
        return data["roster"]

    @staticmethod
    def get_team_id(team_name):
        teams = statsapi.lookup_team(team_name)
        if teams:
            return teams[0]['id']
        else:
            raise ValueError(f"Team '{team_name}' not found.")
    
    @staticmethod
    def get_player_mlbam_id(player_name):
        # Search for the player using the player's name
        search_results = statsapi.lookup_player(player_name)
        
        # Check if any results are found
        if search_results:
            # Take the first result (or handle multiple results if necessary)
            player_info = search_results[0]
            player_id = player_info['id']
            player_full_name = player_info['fullName']
            print(f"Player Name: {player_full_name}, MLBAM ID: {player_id}")
            return player_id
        else:
            print(f"No player found for name: {player_name}")
            return None

    @staticmethod
    def get_season_info(year: int) -> Dict[str, Any]:
        """Return season metadata for the given year.

        Parameters
        ----------
        year : int
            The season year to retrieve.

        Returns
        -------
        dict
            The first season record returned by ``statsapi.get``.
        """
        return statsapi.get('season', {'seasonId': year, 'sportId': 1})['seasons'][0]
    

    @staticmethod
    def get_standings_data(season: int, league_ids: str) -> pd.DataFrame:
        """Return the standings data for a given season."""
        """ AL ID = 103, NL ID = 104"""
        url = f"{STATS_API_BASE_URL}standings?leagueId={league_ids}&season={season}&standingsTypes=regularSeason"
        data = MlbStatsClient._get_json(url)
        return data["records"]

    # https://statsapi.mlb.com/api/v1/teams?&teamId=116&season=2024&hydrate=standings
    @staticmethod
    def get_team_record_for_season(season: int, team_id: int) -> pd.DataFrame:
        """Return the team record for a given season."""
        url = f"{STATS_API_BASE_URL}teams/?teamId={team_id}&season={season}&hydrate=standings"
        data = MlbStatsClient._get_json(url)
        return data["teams"][0]["record"]
    
    # https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2025-08-16&endDate=2025-08-18
    @staticmethod
    def get_schedule_for_date_range(start_date: str, end_date: str) -> pd.DataFrame:
        """Return the schedule for a given date range."""
        url = f"{STATS_API_BASE_URL}schedule?sportId=1&startDate={start_date}&endDate={end_date}&hydrate=probablePitcher,decisions,team"
        data = MlbStatsClient._get_json(url)
        return data["dates"]
    
    # https://www.mlbstatic.com/team-logos/team-cap-on-light/109.svg
    @staticmethod
    def get_team_logo_url(team_id: int) -> str:
        """Return the URL for the team's logo."""
        return f"https://www.mlbstatic.com/team-logos/team-cap-on-light/{team_id}.svg"

    # https://midfield.mlbstatic.com/v1/team/158/spots/128.svg
    @staticmethod
    def get_team_spot_url(team_id: int, size: int) -> str:
        """Return the URL for a specific spot on the team's cap."""
        return f"https://midfield.mlbstatic.com/v1/team/{team_id}/spots/{size}"

    # https://baseballsavant.mlb.com/gf?game_pk=776673
    @staticmethod
    def get_game_data(game_pk: int) -> pd.DataFrame:
        """Return the game data for a given game ID."""
        url = f"{SAVANT_BASE_URL}gf?game_pk={game_pk}"
        data = MlbStatsClient._get_json(url)
        return data
    
    @staticmethod
    def get_recent_schedule_for_team(team_id: int) -> pd.DataFrame:
        """Fetch the recent schedule for a specific team.
            https://statsapi.mlb.com/api/v1/teams?&teamId=116&season=2025&hydrate=previousSchedule,nextSchedule
        """
        season = date.today().year
        url = f"{STATS_API_BASE_URL}teams?teamId={team_id}&season={season}&hydrate=previousSchedule,nextSchedule"
        data = MlbStatsClient._get_json(url)
        return data["teams"][0]

def process_splits(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Compatibility wrapper around :meth:`MlbStatsClient._process_splits`."""
    return MlbStatsClient._process_splits(data)

