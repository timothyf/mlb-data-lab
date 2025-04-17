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
        league: str = None,
        max_workers: int = 10,
        retry_attempts: int = 2,
        chunk_size: int = 100,
    ):
        """
        :param season:         Year to fetch
        :param output_dir:     Directory in which to save CSV(s)
        :param league:       List of MLB team IDs (defaults to all 30)
        :param max_workers:    Number of threads for concurrent fetches
        :param retry_attempts: How many times to retry transient fetch errors
        :param chunk_size:     How many players' stats to buffer before writing to disk
        """
        self.season = season
        self.output_dir = output_dir
        self.client = UnifiedDataClient()
        self.league = league.upper() if league else None
        # …
        if league:
            # override default team list with AL or NL teams from JSON
            self.team_ids = self.get_team_ids_by_league(league)
        else:
            self.team_ids = [
            109,144,110,111,112,145,113,114,115,116,
            117,118,108,119,146,158,142,121,147,133,
            143,134,135,137,136,138,139,140,141,120
         ]

        self.max_workers = max_workers
        self.retry_attempts = retry_attempts
        self.chunk_size = chunk_size

        # accumulate each player's status here
        self.statuses: Dict[str, List[str]] = {
            "success": [], "skipped": [], "valueerror": [],
            "error": [], "no_stats": []
        }

        os.makedirs(self.output_dir, exist_ok=True)


    def get_team_ids_by_league(self, league: str) -> List[str]:
        """
        Reads data/current_teams.json and returns the list of 3‑letter team codes
        for the given league ('AL' or 'NL') in self.season.
        """
        fn = os.path.join(DATA_DIR, "mlb_teams.json")
        if not os.path.exists(fn):
            raise FileNotFoundError(f"Could not find team file: {fn}")

        with open(fn, "r") as fp:
            teams = json.load(fp)

        # Filter by league and (optionally) by year:
        filtered = [
            t["mlbam_team_id"]
            for t in teams
            if t.get("league") == league
        ]

        if not filtered:
            raise ValueError(f"No teams found for league={league}")

        return filtered


    # def download_by_league(self, league: str) -> None:
    #     """
    #     Download & save season stats *only* for teams in the specified league.
    #     Output will be written to stats_<league>_<season>.csv
    #     """
    #     league = league.upper()
    #     league_ids = self.get_team_ids_by_league(league)
    #     if not league_ids:
    #         logger.warning(f"No teams found for league {league}.")
    #         return

    #     filename = os.path.join(
    #         self.output_dir,
    #         f"stats_{league}_{self.season}.csv"
    #     )

    #     # spin up a fresh downloader configured only for that league
    #     sub = SeasonStatsDownloader(
    #         season=self.season,
    #         output_dir=self.output_dir,
    #         team_ids=league_ids,
    #         max_workers=self.max_workers,
    #         retry_attempts=self.retry_attempts,
    #         chunk_size=self.chunk_size,
    #     )
    #     sub.download(output_file=filename)
    #     logger.info(f"{league} stats saved to {filename}")


    def download(self, *, output_file: Optional[str] = None) -> None:
        """
        Main entry point.
        - If `output_file` is None, writes to stats_<season>.csv
        - Otherwise writes to the provided path.
        """
        if output_file is None:
            # if league is provided and is "AL" or "NL", append "_al" or "_nl"
            suffix = f"_{self.league.lower()}" if self.league and self.league.upper() in ("AL", "NL") else ""
            filename = f"stats_{self.season}{suffix}.csv"
            output_file = os.path.join(self.output_dir, filename)

        first_chunk = True

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for team_id in self.team_ids:
                try:
                    team = self.client.fetch_team(team_id)
                    roster = self.client.fetch_team_roster(team_id, self.season)
                except Exception as e:
                    logger.error(f"Skipping team {team_id}: {e}")
                    continue

                futures = {
                    executor.submit(self._fetch_player_stats, pname, team): pname
                    for pname in roster
                }

                buffer: List[pd.DataFrame] = []
                for future in tqdm(
                    as_completed(futures),
                    total=len(futures),
                    desc=f"Team {team.get('name','?')}"
                ):
                    stats = future.result()
                    if stats is not None:
                        buffer.append(stats)

                    if len(buffer) >= self.chunk_size:
                        self._flush_to_disk(buffer, output_file, first_chunk)
                        first_chunk = False
                        buffer.clear()

                # flush remainder for this team
                if buffer:
                    self._flush_to_disk(buffer, output_file, first_chunk)
                    first_chunk = False

        self._print_summary(output_file)


    def _fetch_player_stats(self, player_name: str, team: dict) -> Optional[pd.DataFrame]:
        """
        Fetch a single player's season stats (batting or pitching), with retries.
        Records status into self.statuses and returns either a DataFrame or None.
        """
        for attempt in range(1, self.retry_attempts + 1):
            try:
                player = Player.create_from_mlb(
                    player_name=player_name,
                    data_client=self.client
                )
                if not player:
                    self.statuses["skipped"].append(player_name)
                    return None

                # decide batting vs. pitching
                fetch_fn = (
                    self.client.fetch_pitching_stats
                    if player.player_info.primary_position == "P"
                    else self.client.fetch_batting_stats
                )
                stats = fetch_fn(mlbam_id=player.mlbam_id, season=self.season)
                if stats is not None and not stats.empty:
                    stats["mlbam_id"] = player.mlbam_id
                    stats["season"]    = self.season
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


    def _flush_to_disk(self, dfs: List[pd.DataFrame], filename: str, write_header: bool) -> None:
        # 1) drop any DataFrame that has no rows
        valid = [df for df in dfs if not df.empty]

        # 2) optionally drop columns that are all NA in each frame
        cleaned = [df.dropna(axis=1, how="all") for df in valid]

        if not cleaned:
            # nothing to write
            return

        combined = pd.concat(cleaned, ignore_index=True)
        combined.to_csv(
            filename,
            mode="w" if write_header else "a",
            header=write_header,
            index=False,
        )
        logger.info(f"Wrote {len(combined)} rows to {filename}")



    def _print_summary(self, filename: str) -> None:
        """
        Log a summary of how many players fell into each status bucket.
        """
        total = sum(len(lst) for lst in self.statuses.values())
        logger.info(f"\n=== Completed Season {self.season} ===")
        logger.info(f"Output: {filename}")
        logger.info(f"Players processed: {total}")
        for status, lst in self.statuses.items():
            logger.info(f"{status.title():<12}: {len(lst)}")
