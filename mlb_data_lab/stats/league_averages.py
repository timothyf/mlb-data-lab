# mlb_data_lab/league_averages.py

import pandas as pd
import os
from mlb_data_lab.config import BASE_DIR  
from mlb_data_lab.config import LeagueTeams


DEFAULT_METRICS = ["PA", "AB", "H", "HR", "SO", "RBI", "SB"]  # HR: home runs, SO: strikeouts, BA: batting average, RBI: runs batted in 

def load_season_stats(season: int) -> pd.DataFrame:
    """
    Load the season-level stats CSV file for a given season.
    (Assumes that the stat file is saved in DATA_DIR/season_stats/ with filename format stats_{season}.csv)
    """
    file_path = os.path.join(BASE_DIR, "output/season_stats", f"stats_{season}_batters.csv")
    try:     
        stats_df = pd.read_csv(file_path)
        return stats_df
    except FileNotFoundError:
        raise FileNotFoundError(f"Stat file not found for season {season}: {file_path}")


def compute_leage_totals(
    season: int,
    stats_df: pd.DataFrame,
    metrics: list = None,
    team: str | None = None,
) -> pd.DataFrame:
    if metrics is None:
        metrics = DEFAULT_METRICS

    # Exclude rows where position == P (pitchers)
    stats_df = stats_df[stats_df["Pos"] != "P"].copy()

    if team:
        team_totals = (
            stats_df[stats_df["TeamName"] == team][metrics]
            .sum()
            .round(0)
            .astype(int)
            .to_frame()
            .T
        )
        team_totals.index = [team]
        return team_totals

    # Map teams to leagues before aggregating
    set_league(stats_df)

    # Drop aggregate rows (e.g. "- - -") that don't map to a league
    stats_df = stats_df[stats_df["League"].notnull()].copy()

    # Ensure numeric metrics and remove rows with missing data
    for metric in metrics:
        stats_df[metric] = pd.to_numeric(stats_df[metric], errors="coerce")
    stats_df = stats_df.dropna(subset=metrics)

    # Sum player stats within each league to avoid double counting
    player_league_stats = (
        stats_df.groupby(["xMLBAMID", "League"], as_index=False)[metrics]
        .sum()
    )

    al_totals = (
        player_league_stats[player_league_stats["League"] == "AL"][metrics]
        .sum()
        .round(0)
        .astype(int)
        .to_frame()
        .T
    )
    nl_totals = (
        player_league_stats[player_league_stats["League"] == "NL"][metrics]
        .sum()
        .round(0)
        .astype(int)
        .to_frame()
        .T
    )
    mlb_totals = (
        player_league_stats[metrics]
        .sum()
        .round(0)
        .astype(int)
        .to_frame()
        .T
    )

    league_totals = (
        pd.concat([al_totals, nl_totals, mlb_totals], keys=["AL", "NL", "MLB"])
        .droplevel(1)
    )
    return league_totals


def compute_league_averages(
    season: int,
    stats_df: pd.DataFrame,
    metrics: list = None,
    team: str | None = None,
) -> pd.DataFrame:
    if metrics is None:
        metrics = DEFAULT_METRICS

    # Exclude rows where position == P (pitchers)
    stats_df = stats_df[stats_df["Pos"] != "P"].copy()

    # Exclude rows where AB < 502
    # stats_df = stats_df[stats_df["AB"] >= 502]

    # # Exclude rows where TeamName == '- - -'
    # stats_df = stats_df[stats_df["TeamName"] != "- - -"]

    if team:
        team_stats = stats_df[stats_df["TeamName"] == team].copy()
        for metric in metrics:
            team_stats[metric] = pd.to_numeric(team_stats[metric], errors="coerce")
        team_stats = team_stats.dropna(subset=metrics)
        team_averages = team_stats[metrics].mean().round(2).to_frame().T
        if "AVG" not in metrics:
            team_averages["BA"] = (team_averages["H"] / team_averages["AB"]).round(3)
        team_averages.insert(0, "season", season)
        team_averages.index = [team]
        return team_averages

    set_league(stats_df)

    # Drop aggregate rows (e.g. "- - -") that don't map to a league
    stats_df = stats_df[stats_df["League"].notnull()].copy()

    # Ensure that the columns we are going to average are numeric. (This is particularly important for BA.)
    for metric in metrics:
        stats_df[metric] = pd.to_numeric(stats_df[metric], errors="coerce")

    # It might be useful to drop rows where the key stats are missing.
    stats_df = stats_df.dropna(subset=metrics)

    # Aggregate player stats by league to avoid double counting
    player_league_stats = (
        stats_df.groupby(["xMLBAMID", "League"], as_index=False)[metrics]
        .sum()
    )

    # Calculate league averages by league
    al_averages = (
        player_league_stats[player_league_stats["League"] == "AL"][metrics]
        .mean()
        .round(2)
        .to_frame()
        .T
    )
    nl_averages = (
        player_league_stats[player_league_stats["League"] == "NL"][metrics]
        .mean()
        .round(2)
        .to_frame()
        .T
    )
    mlb_averages = (
        player_league_stats[metrics]
        .mean()
        .round(2)
        .to_frame()
        .T
    )

    # Combine league averages into a single DataFrame and drop the default
    # integer index added by ``to_frame().T`` to avoid an unnecessary
    # MultiIndex in the result.
    league_averages = (
        pd.concat([al_averages, nl_averages, mlb_averages], keys=["AL", "NL", "MLB"])
        .droplevel(1)
    )

    # Inject batting average (h/AB)
    if "AVG" not in metrics:
        league_averages["BA"] = (league_averages["H"] / league_averages["AB"]).round(3)
    league_averages.insert(0, "season", season)

    return league_averages


def set_league(df):
    team_to_league = {team: league for league, teams in LeagueTeams.items.items() for team in teams}
    df['League'] = df['TeamName'].map(team_to_league)
    
    # Identify teams that were not matched
    unmatched_teams = df[df['League'].isnull()]['TeamName'].unique()
    
    if len(unmatched_teams) > 0:
        print("No league found for the following teams:")
        for team in unmatched_teams:
            print(f" - {team}")
    
    df['League'] = df['League'].where(df['League'].notnull(), None)



def save_league_averages(season: int, output_dir: str) -> None:
    league_avgs_df = compute_league_averages(season)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"league_averages_{season}.csv")
    league_avgs_df.to_csv(output_file, index=False)
    print(f"League averages for season {season} saved to: {output_file}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Compute league and team statistics.")
    parser.add_argument("--team", help="Team abbreviation to compute stats for")
    args = parser.parse_args()

    for season in range(2024, 2025):
        print(f"Season {season}")
        stats = load_season_stats(season)
        totals = compute_leage_totals(season, stats)
        print(f"TOTALS:")
        print(totals)
        avgs = compute_league_averages(season, stats)
        print(f"AVERAGES")
        print(avgs)

        if args.team:
            team_totals = compute_leage_totals(season, stats, team=args.team)
            print(f"{args.team} TOTALS:")
            print(team_totals)
            team_avgs = compute_league_averages(season, stats, team=args.team)
            print(f"{args.team} AVERAGES:")
            print(team_avgs)

