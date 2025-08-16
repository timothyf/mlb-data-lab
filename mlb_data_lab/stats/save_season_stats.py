import os
import logging
import time
import json
import re
import csv
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from tqdm import tqdm

from mlb_data_lab.apis.unified_data_client import UnifiedDataClient
from mlb_data_lab.player.player import Player
from mlb_data_lab.config import DATA_DIR
from mlb_data_lab.exceptions.custom_exceptions import NoFangraphsIdError
from mlb_data_lab.exceptions.custom_exceptions import PlayerNotFoundError
from mlb_data_lab.exceptions.custom_exceptions import PositionMismatchError
from mlb_data_lab.exceptions.custom_exceptions import NoStatsError


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class SeasonStatsDownloader:
    def __init__(
        self,
        season: int,
        output_dir: str,
        league: Optional[str] = None,
        *,
        player_type: Optional[str] = None,
        max_workers: int = 10,
        retry_attempts: int = 2,
        chunk_size: int = 100,
    ):
        """
        :param season:       Year to fetch
        :param output_dir:   Where to save CSV(s)
        :param league:       'AL' or 'NL' or None for all teams
        :param player_type:  'pitchers', 'batters', or None for both
        :param max_workers:  Number of threads
        :param retry_attempts: How many times to retry transient errors
        :param chunk_size:   How many players before flushing to disk
        """
        self.season = season
        self.output_dir = output_dir
        self.client = UnifiedDataClient()
        self.league = league.upper() if league else None

        valid = {None, "pitchers", "batters"}
        if player_type not in valid:
            raise ValueError(f"player_type must be one of {valid}")
        self.player_type = player_type

        if league:
            self.team_ids = self.get_team_ids_by_league(league)
        else:
            self.team_ids = [
                109,144,110,111,112,145,113,114,115,116,
                117,118,108,119,146,158,142,121,147,133,
                143,134,135,137,136,138,139,140,141,120
            ]

        self.max_workers    = max_workers
        self.retry_attempts = retry_attempts
        self.chunk_size     = chunk_size

        self.statuses: Dict[str, List[str]] = {
            "success": [],
            "skipped": [],
            "valueerror": [],
            "error": [],
            "no_stats": [],
            "position_mismatch": [],
            "not_found": [],
            "stat_fetch_error": [],
            "no_fangraphs_id": [],
        }

        # Mapping from MLBAM team IDs to Fangraphs team IDs so we can
        # request team‑specific player stats.  This allows us to
        # differentiate players who played on multiple teams in a season
        # and fetch only the stats for the relevant team.
        teams_path = os.path.join(DATA_DIR, "mlb_teams.json")
        with open(teams_path, "r") as fp:
            teams_json = json.load(fp)
        self.team_id_map: Dict[int, int] = {
            t["mlbam_team_id"]: t.get("fg_team_id") for t in teams_json
        }

        os.makedirs(self.output_dir, exist_ok=True)

    # ---------- NEW: text sanitization helpers ----------

    _TAG_RE = re.compile(r"<[^>]*>")

    @staticmethod
    def _strip_html(val):
        if isinstance(val, str) and "<" in val and ">" in val:
            return SeasonStatsDownloader._TAG_RE.sub("", val)
        return val

    @staticmethod
    def _sanitize_text_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Strip HTML, collapse newlines/tabs to spaces, and trim.
        Only touches object (string-like) columns.
        """
        if df is None or df.empty:
            return df
        obj_cols = df.select_dtypes(include="object").columns
        if not len(obj_cols):
            return df
        # Do all replacements in a vectorized way for performance
        for c in obj_cols:
            s = df[c].astype(str)
            s = s.map(SeasonStatsDownloader._strip_html)
            s = s.str.replace(r"[\r\n\t]+", " ", regex=True).str.strip()
            df[c] = s
        return df

    # ----------------------------------------------------

    def get_team_ids_by_league(self, league: str) -> List[int]:
        fn = os.path.join(DATA_DIR, "mlb_teams.json")
        if not os.path.exists(fn):
            raise FileNotFoundError(f"Could not find team file: {fn}")
        with open(fn, "r") as fp:
            teams = json.load(fp)

        filtered = [t["mlbam_team_id"] for t in teams if t.get("league") == league]
        if not filtered:
            raise ValueError(f"No teams found for league={league}")
        return filtered

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _determine_output_file(self, output_file: Optional[str]) -> str:
        """Return the path where stats should be written."""
        if output_file:
            return output_file

        suffix_parts = []
        if self.league in ("AL", "NL"):
            suffix_parts.append(self.league.lower())
        if self.player_type == "pitchers":
            suffix_parts.append("pitchers")
        elif self.player_type == "batters":
            suffix_parts.append("batters")

        suffix = "" if not suffix_parts else "_" + "_".join(suffix_parts)
        return os.path.join(self.output_dir, f"stats_{self.season}{suffix}.csv")

    def _gather_rosters(self) -> List[Tuple[int, pd.DataFrame]]:
        """Fetch the roster for each team."""
        teams_and_rosters: List[Tuple[int, pd.DataFrame]] = []
        for team_id in self.team_ids:
            try:
                roster_df = self.client.fetch_team_roster(team_id, self.season)
                teams_and_rosters.append((team_id, roster_df))
            except Exception as e:  # pragma: no cover - network errors
                logger.error(f"Skipping team {team_id}: {e}")
        return teams_and_rosters

    @staticmethod
    def _build_player_tasks(
        teams_and_rosters: List[Tuple[int, pd.DataFrame]]
    ) -> List[int]:
        """Return a de-duplicated list of player IDs from the supplied rosters."""
        ids = {
            row["mlbam_id"]
            for _, roster_df in teams_and_rosters
            for _, row in roster_df.iterrows()
        }
        return list(ids)

    def _combine_and_clean_dfs(
        self, dfs: List[pd.DataFrame]
    ) -> Optional[pd.DataFrame]:
        """Drop empty columns, concatenate, and sanitize text columns."""
        valid = [df for df in dfs if not df.empty]
        cleaned = [df.dropna(axis=1, how="all") for df in valid]
        if not cleaned:
            return None

        combined = pd.concat(cleaned, ignore_index=True, sort=False)
        return self._sanitize_text_df(combined)


    def download(self, *, output_file: Optional[str] = None) -> None:
        """Main entry point to download and persist season stats."""

        output_file = self._determine_output_file(output_file)

        teams_and_rosters = self._gather_rosters()
        tasks = self._build_player_tasks(teams_and_rosters)

        all_stats: List[pd.DataFrame] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._fetch_player_stats, mlbam_id): mlbam_id
                for mlbam_id in tasks
            }

            for future in tqdm(
                as_completed(futures),
                total=len(futures),
                desc=f"Fetching {len(futures)} players",
            ):
                stats = future.result()
                if stats is not None:
                    all_stats.append(stats)

        if all_stats:
            self._write_all_to_disk(all_stats, output_file)

        self._print_summary(output_file)



    def _fetch_player_stats(
        self,
        mlbam_id: int,
    ) -> Optional[pd.DataFrame]:
        """Fetch a single player's stats split by team.

        The player's team(s) for the season are discovered automatically.
        Returns a DataFrame containing one row per team, or ``None`` if
        no stats are available or the player should be skipped.
        """
        # note: keep a safe name for error logging if player lookup fails early
        safe_name = f"mlbam:{mlbam_id}"
        for attempt in range(1, self.retry_attempts + 1):
            try:
                player = Player.create_from_mlb(
                    mlbam_id=mlbam_id,
                    data_client=self.client
                )
                if not player:
                    raise PlayerNotFoundError(f"No player for id {mlbam_id}")
                safe_name = getattr(getattr(player, "player_bio", None), "full_name", safe_name)

                pos = player.player_info.primary_position
                if self.player_type == "pitchers" and pos != "P":
                    raise PositionMismatchError(f"{mlbam_id} is not a pitcher")
                if self.player_type == "batters" and pos == "P":
                    raise PositionMismatchError(f"{mlbam_id} is a pitcher, not a batter")

                fetch_fn = (
                    self.client.fetch_pitching_stats
                    if pos == "P"
                    else self.client.fetch_batting_stats
                )

                group = "pitching" if pos == "P" else "batting"
                team_ids = self.client.get_player_teams_for_season(
                    mlbam_id, self.season, group=group, ids_only=True
                )
                if not team_ids:
                    team_ids = [None]

                team_dfs: List[pd.DataFrame] = []
                for team_id in team_ids:
                    fg_id = self.team_id_map.get(team_id) if team_id is not None else None
                    stats = fetch_fn(
                        mlbam_id=mlbam_id,
                        season=self.season,
                        fangraphs_team_id=fg_id,
                    )
                    # Drop dataframes that have no meaningful values to avoid
                    # FutureWarning from pandas concat about empty or all-NA inputs
                    if stats is None or stats.empty or stats.isna().all().all():
                        continue
                    stats["mlbam_id"] = mlbam_id
                    stats["season"] = self.season
                    stats["mlbam_team_id"] = team_id
                    team_dfs.append(stats)

                if not team_dfs:
                    raise NoStatsError(f"No stats for {mlbam_id} in {self.season}")

                combined = pd.concat(team_dfs, ignore_index=True, sort=False)
                self.statuses["success"].append(safe_name)
                return combined

            except NoFangraphsIdError:
                self.statuses["no_fangraphs_id"].append(safe_name)
                return None
            except PlayerNotFoundError:
                self.statuses["not_found"].append(safe_name)
                return None
            except PositionMismatchError:
                self.statuses["position_mismatch"].append(safe_name)
                return None
            except NoStatsError:
                self.statuses["no_stats"].append(safe_name)
                return None
            except ValueError:
                self.statuses["valueerror"].append(safe_name)
                return None
            except Exception as exc:
                logger.warning(f"[{mlbam_id}] attempt {attempt} failed: {exc}")
                if attempt == self.retry_attempts:
                    self.statuses["error"].append(mlbam_id)
                    return None
                time.sleep(0.5)

    def _flush_to_disk(
        self, dfs: List[pd.DataFrame], filename: str, write_header: bool
    ) -> None:
        combined = self._combine_and_clean_dfs(dfs)
        if combined is None:
            return

        combined.to_csv(
            filename,
            mode="w" if write_header else "a",
            header=write_header,
            index=False,
            quoting=csv.QUOTE_MINIMAL,
            quotechar='"',
            escapechar='\\',
            lineterminator='\n',
        )
        logger.debug(f"Wrote {len(combined)} rows to {filename}")

    def _write_all_to_disk(self, dfs: List[pd.DataFrame], filename: str) -> None:
        # drop all-empty columns per-frame, then concat with union of columns
        combined = self._combine_and_clean_dfs(dfs)
        if combined is None:
            return

        combined.to_csv(
            filename,
            index=False,
            quoting=csv.QUOTE_MINIMAL,
            quotechar='"',
            escapechar='\\',
            lineterminator='\n',
        )
        logger.debug(f"Wrote {len(combined)} rows to {filename}")


    def _print_summary(self, filename: str) -> None:
        total = sum(len(lst) for lst in self.statuses.values())
        logger.info(f"\n=== Completed Season {self.season} ===")
        logger.info(f"Output: {filename}")
        logger.info(f"Players processed: {total}")
        for status, lst in self.statuses.items():
            logger.info(f"{status.title():<12}: {len(lst)}")

        no_stats = self.statuses.get("no_stats", [])
        if no_stats:
            logger.info("\nPlayers with no stats returned:")
            for name in no_stats:
                logger.info(f"  - {name}")

        valueerror = self.statuses.get("valueerror", [])
        if valueerror:
            logger.info("\nPlayers with valueerror returned:")
            for name in valueerror:
                logger.info(f"  - {name}")

        no_fangraphs_id = self.statuses.get("no_fangraphs_id", [])
        if no_fangraphs_id:
            logger.info("\nPlayers with no_fangraphs_id returned:")
            for name in no_fangraphs_id:
                logger.info(f"  - {name}")
