import os
import logging
import time
import json
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from tqdm import tqdm

from mlb_data_lab.apis.unified_data_client import UnifiedDataClient
from mlb_data_lab.player.player import Player
from mlb_data_lab.config import DATA_DIR

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
            "error": [], "no_stats": []
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
        # build output path
        if output_file is None:
            # build up any suffixes
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

        # 1) grab every roster
        teams_and_rosters: List[Tuple[int, List[str]]] = []
        for team_id in self.team_ids:
            try:
                roster = self.client.fetch_team_roster(team_id, self.season)
                teams_and_rosters.append((team_id, roster))
            except Exception as e:
                logger.error(f"Skipping team {team_id}: {e}")

        # 2) flatten to (player_name, team) tasks
        tasks = [
            (player_name, team_id)
            for team_id, roster in teams_and_rosters
            for player_name in roster
        ]

        # 3) fire off threads
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._fetch_player_stats, pname): pname
                for pname, _ in tasks
            }

            buffer = []
            for future in tqdm(as_completed(futures),
                            total=len(futures),
                            desc=f"Fetching {len(futures)} players"):
                stats = future.result()
                if stats is not None:
                    buffer.append(stats)
                if len(buffer) >= self.chunk_size:
                    self._flush_to_disk(buffer, output_file, first_chunk)
                    first_chunk = False
                    buffer.clear()

            if buffer:
                self._flush_to_disk(buffer, output_file, first_chunk)

        self._print_summary(output_file)


    def _fetch_player_stats(
        self,
        player_name: str
    ) -> Optional[pd.DataFrame]:
        """
        Fetch a single player's stats, skip if not matching self.player_type.
        """
        for attempt in range(1, self.retry_attempts + 1):
            try:
                # look up the player
                player = Player.create_from_mlb(
                    player_name=player_name,
                    data_client=self.client
                )
                if not player:
                    self.statuses["skipped"].append(player_name)
                    return None

                # ENFORCE THE NEW FILTER:
                pos = player.player_info.primary_position
                if self.player_type == "pitchers" and pos != "P":
                    self.statuses["skipped"].append(player_name)
                    return None
                if self.player_type == "batters" and pos == "P":
                    self.statuses["skipped"].append(player_name)
                    return None

                # pick the right fetch method
                fetch_fn = (
                    self.client.fetch_pitching_stats
                    if pos == "P"
                    else self.client.fetch_batting_stats
                )
                stats = fetch_fn(mlbam_id=player.mlbam_id, season=self.season)

                if stats is not None and not stats.empty:
                    stats["mlbam_id"] = player.mlbam_id
                    stats["season"]   = self.season
                    self.statuses["success"].append(player_name)
                    return stats

                self.statuses["no_stats"].append(player_name)
                return None

            except ValueError:
                self.statuses["valueerror"].append(player_name)
                return None

            except Exception as exc:
                logger.warning(f"[{player_name}] attempt {attempt} failed: {exc}")
                if attempt == self.retry_attempts:
                    self.statuses["error"].append(player_name)
                    return None
                time.sleep(0.5)


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
