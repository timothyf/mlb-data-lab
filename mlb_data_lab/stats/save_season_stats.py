import os
import logging
import time
import json
from typing import Tuple
from typing import List, Dict, Optional
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

        # validate player_type
        valid = {None, "pitchers", "batters"}
        if player_type not in valid:
            raise ValueError(f"player_type must be one of {valid}")
        self.player_type = player_type

        # pick teams
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

        # track statuses
        self.statuses: Dict[str, List[str]] = {
            "success": [], "skipped": [], "valueerror": [],
            "error": [], "no_stats": [], "position_mismatch": [],
            "not_found": [], "stat_fetch_error": [], "no_fangraphs_id": []
        }

        os.makedirs(self.output_dir, exist_ok=True)


    def get_team_ids_by_league(self, league: str) -> List[int]:
        fn = os.path.join(DATA_DIR, "mlb_teams.json")
        if not os.path.exists(fn):
            raise FileNotFoundError(f"Could not find team file: {fn}")
        with open(fn, "r") as fp:
            teams = json.load(fp)

        filtered = [
            t["mlbam_team_id"]
            for t in teams
            if t.get("league") == league
        ]
        if not filtered:
            raise ValueError(f"No teams found for league={league}")
        return filtered


    def download(self, *, output_file: Optional[str] = None) -> None:
        """
        Main entry point: flatten all rosters, spin up one executor.
        """
        # Build output filename with any _league or _pitchers/_batters suffixes
        if output_file is None:
            suffix_parts = []
            if self.league in ("AL", "NL"):
                suffix_parts.append(self.league.lower())
            if self.player_type == "pitchers":
                suffix_parts.append("pitchers")
            elif self.player_type == "batters":
                suffix_parts.append("batters")

            suffix = "" if not suffix_parts else "_" + "_".join(suffix_parts)
            output_file = os.path.join(
                self.output_dir,
                f"stats_{self.season}{suffix}.csv"
            )

        first_chunk = True

        # 1) grab every roster as a DataFrame
        teams_and_rosters: List[Tuple[int, pd.DataFrame]] = []
        for team_id in self.team_ids:
            try:
                roster_df = self.client.fetch_team_roster(team_id, self.season)
                # roster_df now has columns ['player_name', 'mlbam_id']
                teams_and_rosters.append((team_id, roster_df))
            except Exception as e:
                logger.error(f"Skipping team {team_id}: {e}")

        # 2) flatten to a list of (player_name, team_id) tasks
        tasks = [
            (row["mlbam_id"], team_id)
            for team_id, roster_df in teams_and_rosters
            for _, row in roster_df.iterrows()
        ]

        # 3) fire off threads
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._fetch_player_stats, mlbam_id): (mlbam_id, team_id)
                for mlbam_id, team_id in tasks
            }

            buffer: List[pd.DataFrame] = []
            for future in tqdm(
                as_completed(futures),
                total=len(futures),
                desc=f"Fetching {len(futures)} players"
            ):
                stats = future.result()
                if stats is not None:
                    buffer.append(stats)

                if len(buffer) >= self.chunk_size:
                    self._flush_to_disk(buffer, output_file, first_chunk)
                    first_chunk = False
                    buffer.clear()

            # final flush
            if buffer:
                self._flush_to_disk(buffer, output_file, first_chunk)

        self._print_summary(output_file)



    def _fetch_player_stats(
        self,
        mlbam_id: int
    ) -> Optional[pd.DataFrame]:
        """
        Fetch a single player's stats, skip if not matching self.player_type.
        """
        for attempt in range(1, self.retry_attempts + 1):
            try:
                # 1) lookup the player
                player = Player.create_from_mlb(
                    mlbam_id=mlbam_id,
                    data_client=self.client
                )
                if not player:
                    raise PlayerNotFoundError(f"No player for id {mlbam_id}")

                # 2) enforce the new pitcher/batter filter
                pos = player.player_info.primary_position
                if self.player_type == "pitchers" and pos != "P":
                    raise PositionMismatchError(f"{mlbam_id} is not a pitcher")
                if self.player_type == "batters" and pos == "P":
                    raise PositionMismatchError(f"{mlbam_id} is a pitcher, not a batter")

                # 3) fetch the stats
                fetch_fn = (
                    self.client.fetch_pitching_stats
                    if pos == "P"
                    else self.client.fetch_batting_stats
                )

                stats = fetch_fn(mlbam_id=mlbam_id, season=self.season)

                # 4) check for no data
                if stats is None or stats.empty:
                    raise NoStatsError(f"No stats for {mlbam_id} in {self.season}")

                # 5) success—annotate and return
                stats["mlbam_id"] = mlbam_id
                stats["season"]   = self.season
                self.statuses["success"].append(player.player_bio.full_name)
                return stats

            except NoFangraphsIdError as e:
                # Fangraphs ID not found, skip this player
                self.statuses["no_fangraphs_id"].append(player.player_bio.full_name)
                return None
            
            except PlayerNotFoundError as e:
                self.statuses["not_found"].append(player.player_bio.full_name)
                return None

            except PositionMismatchError as e:
                # maybe count these separately or lump in "skipped"
                self.statuses["position_mismatch"].append(player.player_bio.full_name)
                return None

            except NoStatsError as e:
                self.statuses["no_stats"].append(player.player_bio.full_name)
                return None

            except ValueError as e:
                # any ValueError from deep inside create_from_mlb or client
                self.statuses["valueerror"].append(player.player_bio.full_name)
                return None

            except Exception as exc:
                # wrap and retry, or finally give up
                logger.warning(f"[{mlbam_id}] attempt {attempt} failed: {exc}")
                if attempt == self.retry_attempts:
                    self.statuses["error"].append(mlbam_id)
                    return None
                time.sleep(0.5)  # wait a bit before retrying


    def _flush_to_disk(
        self,
        dfs: List[pd.DataFrame],
        filename: str,
        write_header: bool
    ) -> None:
        valid   = [df for df in dfs if not df.empty]
        cleaned = [df.dropna(axis=1, how="all") for df in valid]
        if not cleaned:
            return

        combined = pd.concat(cleaned, ignore_index=True)
        combined.to_csv(
            filename,
            mode="w" if write_header else "a",
            header=write_header,
            index=False,
        )
        logger.debug(f"Wrote {len(combined)} rows to {filename}")


    def _print_summary(self, filename: str) -> None:
        total = sum(len(lst) for lst in self.statuses.values())
        logger.info(f"\n=== Completed Season {self.season} ===")
        logger.info(f"Output: {filename}")
        logger.info(f"Players processed: {total}")
        for status, lst in self.statuses.items():
            logger.info(f"{status.title():<12}: {len(lst)}")

        # If any players had no stats, list them out
        no_stats = self.statuses.get("no_stats", [])
        if no_stats:
            logger.info("\nPlayers with no stats returned:")
            for name in no_stats:
                logger.info(f"  - {name}")

        # If any players had no stats, list them out
        valueerror = self.statuses.get("valueerror", [])
        if valueerror:
            logger.info("\nPlayers with valueerror returned:")
            for name in valueerror:
                logger.info(f"  - {name}")

        # If any players had no stats, list them out
        no_fangraphs_id = self.statuses.get("no_fangraphs_id", [])
        if no_fangraphs_id:
            logger.info("\nPlayers with no_fangraphs_id returned:")
            for name in no_fangraphs_id:
                logger.info(f"  - {name}")