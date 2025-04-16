# mlb_data_lab/league_averages.py

import pandas as pd
import os
from mlb_data_lab.config import BASE_DIR  
from mlb_data_lab.config import LeagueTeams



def load_season_stats(season: int) -> pd.DataFrame:
    """
    Load the season-level stats CSV file for a given season.
    (Assumes that the stat file is saved in DATA_DIR/season_stats/ with filename format stats_{season}.csv)
    """
    file_path = os.path.join(BASE_DIR, "output/season_stats", f"stats_{season}.csv")
    try:
        stats_df = pd.read_csv(file_path)
        return stats_df
    except FileNotFoundError:
        raise FileNotFoundError(f"Stat file not found for season {season}: {file_path}")


def compute_leage_totals(season: int, stats_df: pd.DataFrame, metrics: list = None) -> pd.DataFrame:
    if metrics is None:
        metrics = ["AB", "H", "HR", "SO", "RBI"]  # HR: home runs, SO: strikeouts, BA: batting average, RBI: runs batted in

    # Exclude rows where position == P (pitchers)
    stats_df = stats_df[stats_df["Pos"] != "P"]

    # Count each player only once, remove duplicates.
    stats_df = stats_df.drop_duplicates(subset=["xMLBAMID"])

    set_league(stats_df)

    al_totals = stats_df[stats_df["League"] == "AL"][metrics].sum().round(0).astype(int).to_frame().T
    nl_totals = stats_df[stats_df["League"] == "NL"][metrics].sum().round(0).astype(int).to_frame().T
    mlb_totals = stats_df[metrics].sum().round(0).astype(int).to_frame().T
    league_totals = pd.concat([al_totals, nl_totals, mlb_totals], keys=["AL", "NL", "MLB"])
    return league_totals


def compute_league_averages(season: int, stats_df: pd.DataFrame, metrics: list = None) -> pd.DataFrame:
    if metrics is None:
        metrics = ["AB", "H", "HR", "SO", "RBI"]  # HR: home runs, SO: strikeouts, BA: batting average, RBI: runs batted in

    # Exclude rows where position == P (pitchers)
    stats_df = stats_df[stats_df["Pos"] != "P"]

    # Count each player only once, remove duplicates.
    stats_df = stats_df.drop_duplicates(subset=["xMLBAMID"])

    # Exclude rows where AB < 502
    # stats_df = stats_df[stats_df["AB"] >= 502]

    # # Exlude rows where TeamName == '- - -'
    # stats_df = stats_df[stats_df["TeamName"] != "- - -"]

    set_league(stats_df)

    # Ensure that the columns we are going to average are numeric. (This is particularly important for BA.)
    for metric in metrics:
        stats_df[metric] = pd.to_numeric(stats_df[metric], errors='coerce')

    # It might be useful to drop rows where the key stats are missing.
    stats_df = stats_df.dropna(subset=metrics)

    # Calculate league averages by league
    al_averages = stats_df[stats_df["League"] == "AL"][metrics].mean().round(2).to_frame().T
    nl_averages = stats_df[stats_df["League"] == "NL"][metrics].mean().round(2).to_frame().T
    mlb_averages = stats_df[metrics].mean().round(2).to_frame().T

    # Combine league averages into a single DataFrame
    league_averages = pd.concat([al_averages, nl_averages, mlb_averages], keys=["AL", "NL", "MLB"])

    # Inject batting average (h/AB)
    if "AVG" not in metrics:
        league_averages["BA"] = (league_averages["H"] / league_averages["AB"]).round(3)
    league_averages.insert(0, "season", season)

    return league_averages


def set_league(df):
    team_to_league = {team: league for league, teams in LeagueTeams.items.items() for team in teams}
    df['League'] = df['TeamName'].map(team_to_league)
    df['League'] = df['League'].where(df['League'].notnull(), None)


def save_league_averages(season: int, output_dir: str) -> None:
    league_avgs_df = compute_league_averages(season)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"league_averages_{season}.csv")
    league_avgs_df.to_csv(output_file, index=False)
    print(f"League averages for season {season} saved to: {output_file}")


if __name__ == '__main__':
    for season in range(2022, 2025):
        print(f"Season {season}")
        stats = load_season_stats(season)
        totals = compute_leage_totals(season, stats)
        print(f"TOTALS:")
        print(totals)
        avgs = compute_league_averages(season, stats)
        print(f"AVERAGES")
        print(avgs)

